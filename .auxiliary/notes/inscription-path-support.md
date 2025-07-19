# Inscription Path Support Enhancement

**Date**: 2025-07-16
**Context**: Post-1.2 release - immediate improvement
**Status**: Design proposal

## Problem Statement

Current inscription control objects expect `target` to be a stream (`TextIO`),
but typical CLI usage involves specifying log file paths. This creates a burden
where CLI applications must manually convert paths to streams before
configuring inscription services.

**Pain Points:**
1. CLI apps receive paths from command line args, configs, or environment variables
2. Manual path-to-stream conversion required
3. Stream lifecycle management complexity
4. Error handling for file access issues

## Current Usage Pattern (Painful)

```python
# Current: Manual path-to-stream conversion
log_file_path = Path("/path/to/logfile.log")
with log_file_path.open('w') as log_stream:
    inscription_control = appcore.inscription.Control(
        target = log_stream
    )
    # Must use within context manager scope
```

## Proposed Solution: TargetDescriptor Structure

### Design Rationale

**Option C** was chosen over alternatives:
- **Option A** (bundled TargetControl): More complex nesting
- **Option B** (separate attributes): Clutters Control class interface
- **Option C** (TargetDescriptor): ✅ Clean, backward compatible, compact

**Key advantages of Option C:**
1. **Perfect backward compatibility**: Existing `target = sys.stderr` usage unchanged
2. **Compact representation**: Related fields bundled in logical structure
3. **Type safety**: Union type clearly distinguishes stream vs descriptor
4. **Extensibility**: Easy to add new TargetDescriptor fields later
5. **Clean API**: Control class interface stays focused

### New TargetDescriptor Class

```python
class TargetModes( __.enum.Enum ):
    ''' Target file mode control. '''
    Append = 'append'
    Truncate = 'truncate'

class TargetDescriptor( __.immut.DataclassObject ):
    ''' Descriptor for file-based inscription targets. '''
    name: __.typx.Union[ bytes, str, __.os.PathLike ]
    mode: TargetModes = TargetModes.Truncate
    codec: str = 'utf-8'
```

### Enhanced Control Class

```python
class Control( __.immut.DataclassObject ):
    mode: Modes = Modes.Plain
    level: str = 'info'
    target: __.typx.Union[ __.io.TextIO, TargetDescriptor ] = __.sys.stderr
```

### Desired Usage Pattern (Convenient)

```python
# Simple path (using defaults: truncate mode, utf-8 encoding)
inscription_control = appcore.inscription.Control(
    mode = appcore.inscription.Modes.Rich,
    level = 'debug',
    target = appcore.inscription.TargetDescriptor(name="/path/to/logfile.log")
)

# Path with custom mode and encoding
inscription_control = appcore.inscription.Control(
    target = appcore.inscription.TargetDescriptor(
        name = Path("/path/to/logfile.log"),
        mode = appcore.inscription.TargetModes.Append,
        codec = 'utf-8'
    )
)

# Stream (backward compatible)
inscription_control = appcore.inscription.Control(
    target = sys.stdout
)
```

## Implementation Strategy

### 1. Target Resolution Function

```python
def _resolve_target(
    target: __.typx.Union[ __.io.TextIO, TargetDescriptor ],
    exits: __.ctxl.AsyncExitStack
) -> __.io.TextIO:
    """Resolve target to TextIO, handling lifecycle management."""
    if isinstance(target, TargetDescriptor):
        path = __.Path(target.name)
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        # Determine file mode
        file_mode = 'a' if target.mode == TargetModes.Append else 'w'
        # Open file and register cleanup with exits.enter_context
        file_stream = exits.enter_context(
            path.open(file_mode, encoding=target.codec)
        )
        return file_stream
    else:
        # Already a stream, use as-is
        return target
```

### 2. Modified Preparation Functions

```python
def prepare_scribes_logging(
    auxdata: _state.Globals, control: Control
) -> None:
    """Prepares Python standard logging system."""
    level_name = _discover_inscription_level_name( auxdata, control )
    level = getattr( _logging, level_name.upper( ) )
    formatter = _logging.Formatter( "%(name)s: %(message)s" )

    # Resolve target to stream with lifecycle management
    target_stream = _resolve_target(control.target, auxdata.exits)

    match control.mode:
        case Modes.Plain:
            _prepare_logging_plain( level, target_stream, formatter )
        case Modes.Rich:
            _prepare_logging_rich( level, target_stream, formatter )
        case _: pass
```

### 3. Error Handling with Custom Exception

```python
class InscriptionTargetError( Omnierror, OSError ):
    """Failed to configure inscription target."""

    def __init__(self, target: TargetDescriptor, cause: Exception):
        super().__init__(
            f"Failed to configure inscription target '{target.name}': {cause}"
        )

def _resolve_target(
    target: __.typx.Union[ __.io.TextIO, TargetDescriptor ],
    exits: __.ctxl.AsyncExitStack
) -> __.io.TextIO:
    """Resolve target to TextIO, handling lifecycle management."""
    if isinstance(target, TargetDescriptor):
        try:
            path = __.Path(target.name)
            path.parent.mkdir(parents=True, exist_ok=True)
            file_mode = 'a' if target.mode == TargetModes.Append else 'w'
            file_stream = exits.enter_context(
                path.open(file_mode, encoding=target.codec)
            )
            return file_stream
        except (OSError, PermissionError) as error:
            raise InscriptionTargetError(target, error) from error
    else:
        return target
```

## Benefits

### 1. **Backward Compatibility**
- Existing stream-based usage continues to work
- No breaking changes to current API

### 2. **CLI Convenience**
- Direct path support eliminates manual conversion
- Automatic stream lifecycle management
- Built-in error handling with fallbacks

### 3. **Configuration Integration**
- Easy integration with command-line arguments
- Seamless TOML/JSON configuration support
- Environment variable compatibility

### 4. **Safety and Reliability**
- Automatic directory creation
- Proper stream cleanup via exits stack
- Error handling with fallback to stderr

## Implementation Plan

### Phase 1: Core Enhancement (1.3.0)
- [ ] Update `Control` class with union type target
- [ ] Implement `_resolve_target` function
- [ ] Modify preparation functions to use target resolution
- [ ] Add comprehensive tests

### Phase 2: CLI Integration (1.4.0)
- [ ] Add CLI helper functions for common patterns
- [ ] Document best practices for CLI applications
- [ ] Create example CLI applications

### Phase 3: Advanced Features (Future)
- [ ] Log rotation support
- [ ] Multiple target support (fan-out logging)
- [ ] Structured logging integration

## Testing Strategy

### Unit Tests
- Path resolution functionality
- Stream lifecycle management
- Error handling and fallbacks
- Backward compatibility verification

### Integration Tests
- CLI application scenarios
- Configuration file integration
- Error recovery behaviors

## Migration Impact

### Existing Code
- **No changes required**: All existing code continues to work
- **Optional adoption**: Can gradually migrate to path-based usage

### New Code
- **Simplified setup**: Direct path specification
- **Reduced boilerplate**: No manual stream management
- **Better error handling**: Built-in fallback mechanisms

## Example CLI Integration

```python
# CLI argument parsing
@dataclass
class CliArgs:
    log_file: str = "app.log"
    log_level: str = "info"
    rich_logging: bool = False
    log_append: bool = False

# Simple inscription setup
def setup_logging(args: CliArgs) -> appcore.inscription.Control:
    target_mode = (
        appcore.inscription.TargetModes.Append
        if args.log_append
        else appcore.inscription.TargetModes.Truncate
    )
    return appcore.inscription.Control(
        mode = appcore.inscription.Modes.Rich if args.rich_logging else appcore.inscription.Modes.Plain,
        level = args.log_level,
        target = appcore.inscription.TargetDescriptor(
            name = args.log_file,
            mode = target_mode
        )
    )
```

This enhancement eliminates the stream conversion burden while maintaining full backward compatibility and adding robust error handling.
