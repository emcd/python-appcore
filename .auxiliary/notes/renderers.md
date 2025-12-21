# Rendering Protocol Design Document

**Status**: Aligned with ictr v1.0a1
**Last Updated**: 2025-12-20

This document defines how appcore uses `ictr` renderable protocols and presentations for CLI output.

---

## Overview

Appcore uses `ictr.standard` renderable protocols (`DictionaryRenderable`, `JsonRenderable`,
`MarkdownRenderable`) and presentation classes (`PlaintextPresentation`, `JsonPresentation`,
`MarkdownPresentation`) for flexible CLI output formatting.

### Architecture

Appcore objects implement `ictr.standard` renderable protocols. The `Application`
class uses `ictr.standard` presentations to render results for CLI output.

```
┌──────────────────────────────────────────────────────────────┐
│                    ictr.standard Protocols                    │
│  DictionaryRenderable  ->  render_as_dictionary() -> dict    │
│  JsonRenderable        ->  render_as_json(...) -> str        │
│  MarkdownRenderable    ->  render_as_markdown(...) -> str    │
└──────────────────────────────────────────────────────────────┘
                              ▲
                              │ implements
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                            │
┌───────┴────────┐                      ┌────────────┴─────────┐
│  Omniexception │                      │  Command Results     │
│  (exceptions)  │                      │  (dataclasses)       │
└────────────────┘                      └──────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                 ictr.standard Presentations                   │
│  PlaintextPresentation  ->  linearize_omni fallback          │
│  JsonPresentation       ->  render_as_json with config       │
│  MarkdownPresentation   ->  render_as_markdown with Rich     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     Application renders output
```

### Module Organization

- **`exceptions.py`**: Omniexception implements ictr renderable protocols
- **`cli/core.py`**: Application uses ictr presentations for output
- **`cli/standard.py`**: Exception interceptor, result printer (uses ictr)

---

## Key Decisions

### 1. Use ictr Protocols Directly

Appcore implements `ictr.standard` protocols rather than defining its own. This provides:
- Consistent rendering across ictr-aware tools
- Linearization and colorization handled by ictr
- Presentations strategy pattern for format selection

### 2. DisplayOptions Stays in Application

**Decision**: Don't thread DisplayOptions through auxdata/Globals.

**Rationale**:
- Commands return renderable results
- Application controls presentation
- Cleaner separation of concerns
- Progress reporting via callback instead

### 3. Omniexception Implements ictr Protocols

Add default implementations to `Omniexception` base class:
- `render_as_dictionary()` - base exception data
- `render_as_json()` - uses default from DictionaryRenderable mixin
- `render_as_markdown()` - uses default from MarkdownRenderable mixin

Subclasses override `render_as_dictionary()` to add context fields.

---

## Using ictr Protocols in Appcore

### Omniexception Implementation

```python
from ictr.standard import (
    DictionaryRenderableDataclass,
    JsonRenderableDataclass,
    MarkdownRenderableDataclass,
)

class Omniexception(
    Exception,
    DictionaryRenderableDataclass,
    JsonRenderableDataclass,
    MarkdownRenderableDataclass,
):
    """Base exception with rendering support."""

    def render_as_dictionary(self) -> dict[str, Any]:
        """Override for custom fields."""
        return {
            'exception_class': self.__class__.__name__,
            'message': str(self),
        }

    # render_as_json() and render_as_markdown() inherited from mixins
```

### Command Result Implementation

```python
@dataclass
class AnalysisResult(
    DictionaryRenderableDataclass,
    JsonRenderableDataclass,
    MarkdownRenderableDataclass,
):
    files_checked: int
    issues_found: int

    def render_as_dictionary(self) -> dict[str, Any]:
        return {
            'files_checked': self.files_checked,
            'issues_found': self.issues_found,
            'status': 'pass' if self.issues_found == 0 else 'fail',
        }
```

---

## Application Rendering Pattern

### Presentation Registry

Third-party extensible registry mapping presentation names to either:
- **String**: Attribute name on Application containing configured Presentation instance
- **Class**: Presentation subclass to instantiate with defaults

```python
# In cli/standard.py or cli/core.py
PRESENTATION_REGISTRY: dict[ str, str | type[ __.ictrstd.Presentation ] ] = {
    'json': 'clioptions_json',           # Has CLI options
    'markdown': __.ictrstd.MarkdownPresentation,  # No CLI options
    'plaintext': __.ictrstd.PlaintextPresentation,
}
```

### Application with Presentation Selection

```python
class Application( _cli.Application ):
    clioptions: DisplayOptions = ...
    presentation: str = 'plaintext'  # String for extensibility

    # Per-presentation options (Tyro exposes as --clioptions-json.compact, etc.)
    clioptions_json: __.ictrstd.JsonPresentation = __.dcls.field(
        default_factory = __.ictrstd.JsonPresentation )
```

### render_and_print Implementation

```python
async def render_and_print(
    application: _core.Application, auxdata: __.Globals, entity: object
) -> None:
    printer = await application.clioptions.provide_printer( auxdata.exits )
    control = printer.provide_textualization_control( )

    # Lookup presentation from registry
    entry = PRESENTATION_REGISTRY.get(
        application.presentation, __.ictrstd.PlaintextPresentation )
    if isinstance( entry, str ):
        presentation = getattr( application, entry )
    else:
        presentation = entry( )  # Instantiate class

    # Render
    linstate = __.ictrstd.LinearizerState.from_configuration(
        __.ictrstd.LinearizerConfiguration( colorize = control.colorize ),
        control )
    text = presentation.render( linstate, entity )
    printer( text )
```

---

## Implementation Status

### ✅ Completed (in ictr)

- DictionaryRenderable, JsonRenderable, MarkdownRenderable protocols
- DictionaryRenderableDataclass, etc. mixin classes
- PlaintextPresentation, JsonPresentation, MarkdownPresentation
- LinearizerConfiguration and LinearizerState
- Default render_as_json() and render_as_markdown() implementations

### 🎯 To Do (in appcore)

1. **Omniexception**: Add ictr renderable mixin inheritance
2. **Application**: Implement presentation selection and rendering
3. **DisplayOptions**: Add format, compact, indent fields
4. **Progress callback**: Add to Globals for command progress reporting

### 📚 References

- **ictr appcore-integration.md**: Presentation architecture details
- **ictr/standard/presentations.py**: Presentation implementations
- **ictr/standard/renderables.py**: Protocol definitions and defaults
