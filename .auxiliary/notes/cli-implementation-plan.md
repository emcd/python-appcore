# CLI Implementation Plan

**Date**: 2025-07-16
**Updated**: 2025-09-20
**Context**: Post-1.2 release planning
**Status**: Active Development Plan

## Background & Decision Summary

**Problem**: CLI applications duplicate Tyro CLI skeletons despite using `emcd-appcore` for application initialization.

**Decision**: Add CLI foundation as optional dependency group (`emcd-appcore[cli]`) rather than separate package.

**Rationale**: Tight integration with appcore systems, guaranteed API compatibility, single release cycle, better user experience.

## Reference Implementations

**Current CLI patterns for reference:**
- `../ai-experiments/sources/aiwb/libcore/cli.py` (older approach)
- `../python-librovore/sources/librovore/cli.py` (preferred direction)

## Architecture Overview

### Package Structure
```
sources/appcore/
├── __init__.py              # Core exports
├── cli/                     # New CLI module
│   ├── __init__.py         # CLI foundation exports
│   ├── __main__.py         # python -m appcore.cli support
│   ├── foundation.py       # Base CLI scaffolding
│   ├── preparation.py      # CLI-specific preparation helpers
│   └── example.py          # Built-in example CLI (inspect)
├── application.py          # Existing core
├── preparation.py          # Existing core
└── ...                     # Other existing modules
```

### Dependencies
```toml
[project.optional-dependencies]
cli = ["tyro~=0.9.0", "rich~=13.0"]

[project.scripts]
appcore = "appcore.cli.example:execute_cli"
```

## Implementation Phases

### Phase 1: Foundation Components (MVP)

#### 1.1 Core Foundation (`appcore/cli/foundation.py`)
```python
# Mutex group for output targets (reuse librovore pattern)
TargetMutex = __.tyro.conf.create_mutex_group(required=False)

class DisplayOptions(__.immut.DataclassObject):
    """Standardized output configuration"""
    format: DisplayFormat = DisplayFormat.Rich
    target_stream: __.typx.Annotated[
        __.typx.Optional[TargetStream],
        TargetMutex,
        __.tyro.conf.DisallowNone,
    ] = TargetStream.Stderr
    target_file: __.typx.Annotated[
        __.typx.Optional[Path],
        TargetMutex,
    ] = None
    color: bool = True

class CliInscriptionControl(__.immut.DataclassObject):
    """Bridge between CLI args and appcore inscription"""
    mode: ScribePresentations = ScribePresentations.Plain
    level: str = 'info'
    target_stream: __.typx.Annotated[
        __.typx.Optional[TargetStream],
        TargetMutex,
        __.tyro.conf.DisallowNone,
    ] = TargetStream.Stderr

    def as_control(self) -> InscriptionControl:
        """Produces compatible inscription control"""

class CliCommand(Protocol):
    """Standard interface for CLI commands"""
    async def __call__(
        self,
        auxdata: state.Globals,
        display: DisplayOptions
    ) -> None: ...

# Enums and utilities
class DisplayFormat(enum.Enum):
    Rich = 'rich'
    Json = 'json'
    Plain = 'plain'

class TargetStream(enum.Enum):
    Stdout = 'stdout'
    Stderr = 'stderr'
```

#### 1.2 Preparation Bridge (`appcore/cli/preparation.py`)
```python
async def prepare_from_cli(
    exits: AsyncExitStack,
    inscription: CliInscriptionControl,
    configfile: Optional[Path] = None,
    **kwargs
) -> state.Globals:
    """Bridge CLI arguments to appcore preparation"""

    # Convert CLI inscription to appcore inscription
    inscription_control = inscription.as_control()

    # Build preparation arguments
    nomargs = {
        'exits': exits,
        'inscription': inscription_control,
        'environment': True,  # Default for CLI apps
        **kwargs
    }

    if configfile:
        nomargs['configfile'] = configfile

    return await appcore.prepare(**nomargs)
```

#### 1.3 Example CLI (`appcore/cli/example.py`)
```python
class InspectConfigurationCommand(CliCommand):
    """Show merged application configuration"""

    async def __call__(self, auxdata: state.Globals, display: DisplayOptions):
        data = dict(auxdata.configuration)
        await display.render(data)

class InspectEnvironmentCommand(CliCommand):
    """Show app-specific environment variables"""

    async def __call__(self, auxdata: state.Globals, display: DisplayOptions):
        prefix = f"{auxdata.application.name.upper()}_"
        env_vars = {
            k: v for k, v in os.environ.items()
            if k.startswith(prefix)
        }
        await display.render(env_vars)

class InspectDirectoriesCommand(CliCommand):
    """Show platform directories"""

    async def __call__(self, auxdata: state.Globals, display: DisplayOptions):
        dirs = {
            'cache': str(auxdata.provide_cache_location()),
            'data': str(auxdata.provide_data_location()),
            'state': str(auxdata.provide_state_location()),
            'package_data': str(auxdata.distribution.provide_data_location()),
        }
        await display.render(dirs)

class AppcoreCli(__.immut.DataclassObject):
    """Built-in appcore CLI for debugging and inspection"""

    display: DisplayOptions = DisplayOptions()
    inscription: CliInscriptionControl = CliInscriptionControl()
    configfile: Optional[Path] = None
    command: __.typx.Union[
        __.typx.Annotated[
            InspectConfigurationCommand,
            __.tyro.conf.subcommand('configuration', prefix_name=False),
        ],
        __.typx.Annotated[
            InspectEnvironmentCommand,
            __.tyro.conf.subcommand('environment', prefix_name=False),
        ],
        __.typx.Annotated[
            InspectDirectoriesCommand,
            __.tyro.conf.subcommand('directories', prefix_name=False),
        ],
    ] = InspectConfigurationCommand()

    async def __call__(self):
        async with __.ctxl.AsyncExitStack() as exits:
            auxdata = await prepare_from_cli(
                exits, self.inscription, self.configfile
            )
            await self.command(auxdata, self.display)

def execute_cli():
    """Entry point for appcore CLI"""
    config = (__.tyro.conf.EnumChoicesFromValues,)
    __.asyncio.run(__.tyro.cli(AppcoreCli, config=config)())
```

#### 1.4 Module Main Support (`appcore/cli/__main__.py`)
```python
"""Support for python -m appcore.cli execution"""

from .example import execute_cli

if __name__ == '__main__':
    execute_cli()
```

#### 1.5 Module Exports (`appcore/cli/__init__.py`)
```python
"""CLI foundation for appcore applications"""

# Guard against missing optional dependencies
try:
    import tyro
    import rich
except ImportError as exc:
    raise ImportError(
        "CLI features require optional dependencies. "
        "Install with the 'cli' extra"
    ) from exc

from .foundation import (
    DisplayOptions,
    CliInscriptionControl,
    CliCommand,
    DisplayFormat,
    TargetStream,
)
from .preparation import prepare_from_cli
```

#### 1.6 Package Configuration Updates
```toml
# pyproject.toml additions

[project.optional-dependencies]
cli = [
    "tyro~=0.9.0",
    "rich~=13.0"
]

[project.scripts]
appcore = "appcore.cli.example:execute_cli"

[tool.hatch.envs.develop]
dependencies = [
    # ... existing deps ...
    "tyro",  # For CLI testing
]
```

### Implementation Notes for Coder

#### Missing Method Implementations Needed

**DisplayOptions methods** (based on librovore patterns):
```python
async def provide_stream(self, exits: AsyncExitStack) -> TextIO:
    """Provides the target output stream"""

def decide_rich_markdown(self, stream: TextIO) -> bool:
    """Determines whether to use Rich markdown rendering"""

async def render(self, obj: Any) -> None:
    """Renders object according to display options"""
```

**Version handling**:
- Add `--version` option to main CLI class using `tyro.conf.arg`
- Extract version from `auxdata.application` or `auxdata.distribution`
- Display format: `appcore {version}` or similar

**Error handling**:
- Basic try/catch in CLI entry points with SystemExit(1)
- Structured error output for JSON format
- Consider console.print_exception() for Rich format

**Rich integration details**:
- TTY detection: `stream.isatty()`
- NO_COLOR environment variable respect
- Console creation with proper file parameter
- Markdown rendering for help/error output

#### Configuration Integration

**CLI argument precedence** (highest to lowest):
1. Explicit CLI arguments
2. Environment variables (existing appcore pattern)
3. Configuration files (existing appcore pattern)
4. CLI defaults

**Tyro integration with appcore config**:
- CLI args should be able to specify config file path
- Config file discovery should work as normal
- Environment variables should work as normal

#### Async Pattern Consistency

All CLI commands should follow:
```python
async def __call__(self):
    async with AsyncExitStack() as exits:
        auxdata = await prepare_from_cli(exits, ...)
        await self.command(auxdata, self.display)
```

#### Import Structure

**Foundation module** needs:
```python
from typing import Protocol, Optional, Literal, TextIO
from pathlib import Path
import enum
import tyro.conf
from .. import inscription, state  # appcore imports
```

**Example module** needs:
```python
import os
import asyncio
from .foundation import DisplayOptions, CliCommand, CliInscriptionControl
from .preparation import prepare_from_cli
```

### Phase 2: Testing & Integration

#### 2.1 Testing Strategy
- **Unit tests**: Foundation classes, preparation bridge
- **Integration tests**: Real CLI command execution
- **Dogfooding**: Use our own patterns for the built-in CLI
- **Example documentation**: Show CLI in action

#### 2.2 Built-in CLI Usage Examples
```bash
# Install with CLI support
pip install emcd-appcore[cli]

# Three ways to run the example CLI
appcore configuration                    # Via entry point
python -m appcore.cli configuration      # Via module main
hatch run appcore configuration          # In development

# Subcommands
appcore configuration                    # Show merged config (default)
appcore environment                     # Show app-specific env vars
appcore directories                     # Show platform directories

# Output options
appcore configuration --format json
appcore configuration --target-file config.json --format json
```

### Phase 3: Documentation & Adoption

#### 3.1 Documentation Plan
- **API documentation**: CLI foundation classes and functions
- **Usage guide**: How to build CLIs using appcore patterns
- **Migration guide**: Converting existing CLIs to use foundation
- **Examples**: Common patterns and recipes

#### 3.2 Migration Support
- **Compatibility**: Maintain existing appcore APIs unchanged
- **Incremental adoption**: Downstream projects can migrate at their own pace
- **Pattern documentation**: Show before/after examples

## Success Metrics

1. **Reduced duplication**: Downstream CLIs use common foundation
2. **Integration quality**: CLI features work seamlessly with appcore
3. **Dogfooding success**: Built-in CLI demonstrates all patterns
4. **Developer experience**: Easy to create and test new CLI applications

## Future Enhancements (Phase 2+)

### Advanced Error Handling
- Evaluate `intercept_errors` decorator patterns
- Support for custom exception families
- Structured error reporting

### Enhanced Features
- Common command patterns (serve, version, etc.)
- Configuration validation and schema support
- Testing utilities for CLI applications
- Plugin/extension support

### Performance & Usability
- **Shell completion support**: Tab completion for commands, options, and values
- Improved help text formatting
- Configuration file discovery improvements

## Timeline & Dependencies

**Prerequisites**: None (builds on existing appcore foundation)

**Phase 1 Target**: 2-3 weeks development + testing

**Integration Dependencies**:
- Tyro compatibility (>=0.8.0)
- Rich integration (>=13.0.0)
- Appcore preparation system (existing)

**Risk Mitigation**:
- Optional dependency approach minimizes impact
- Built-in CLI provides immediate testing feedback
- Incremental adoption reduces migration risk