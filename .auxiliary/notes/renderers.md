# Rendering Protocol Design Document

**Status**: In Progress
**Last Updated**: 2025-11-18

This document defines the architecture and key design decisions for a rendering protocol toolkit in appcore. It provides guidance for implementation without over-specifying implementation details.

---

## Overview

A protocol-based rendering system that allows objects (exceptions, results, data structures) to render themselves in multiple formats (JSON, Markdown, TOML). The system is non-intrusive and works through structural typing.

### Goals

1. **Uniform Interface**: Single protocol for rendering any object type
2. **Multiple Formats**: JSON, Markdown, TOML support
3. **Non-Intrusive**: Objects gain rendering without forced inheritance
4. **Flexible**: Works with exceptions, dataclasses, and custom objects
5. **Terminal-Aware**: Adapts markdown rendering to terminal capabilities

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Renderable Protocol                      │
│  - render_dictionary() -> dict                               │
│  - render_json(compact: bool) -> str                        │
│  - render_markdown() -> tuple[str, ...]                     │
│  - render_toml() -> str                                      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ implements (structurally)
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
┌───────┴────────┐                      ┌───────────┴──────────┐
│  Omniexception │                      │     Renderable       │
│  (exceptions)  │                      │  (base dataclass)    │
└────────────────┘                      └──────────────────────┘
```

### Module Organization

- **`cli/core.py`**: Base CLI infrastructure (DisplayOptions, streams)
- **`cli/standard.py`**: Rendering extensions (Renderable protocol, Presentations enum)
- **`exceptions.py`**: Exception rendering methods on Omniexception
- **Future**: Consider separate `renderables.py` for protocol if used outside CLI

---

## Key Design Decisions

### 1. Protocol-Based Approach

**Decision**: Use `@runtime_checkable` Protocol for structural typing.

**Rationale**:
- No forced inheritance required
- Works with any object that implements the methods
- Type checkers can verify compliance
- Exceptions and result objects use same interface

### 2. Rendering Methods on Exceptions

**Decision**: Add rendering methods directly to `Omniexception` base class.

**Rationale**:
- All exceptions automatically gain rendering capability
- Non-breaking change (methods are new)
- Subclasses can override for custom rendering
- No protocol requirement - just providing methods

**Constraint**: Cannot pass `DisplayOptions` to `render_markdown()` due to cyclic import.

### 3. Dictionary as Source of Truth

**Decision**: `render_dictionary()` is primary method, others derive from it.

**Rationale**:
- Single place to define object structure
- Consistent across all formats
- Easy to override with custom data
- Default implementations for other formats

### 4. Markdown Rendering Strategy

**Decision**: `render_markdown()` returns lines; caller handles Rich vs plain.

**Rationale**:
- Avoids cyclic imports
- Keeps rendering methods simple
- Caller has terminal context
- Overrides don't need colorization logic

**Implementation**: Use `determine_colorization()` in display layer to decide whether to use `rich.markdown.Markdown` or strip formatting.

### 5. Presentation Modes

**Decision**: Enum with `Json`, `Markdown`, `Toml`. Use `compact` boolean flag, not separate `CompactJson`.

**Rationale**:
- Simpler than multiple JSON variants
- `compact` flag could apply to other formats
- Cleaner API: `render_json(compact=True)`

### 6. No Legacy Fallbacks

**Decision**: Objects must implement protocol to be rendered. No dictionary fallback.

**Rationale**:
- Clear contracts
- Fails fast on incorrect usage
- Avoids hidden complexity

---

## Interface Contracts

### Renderable Protocol

```python
@runtime_checkable
class Renderable(Protocol):
    """Protocol for objects that render themselves."""

    def render_dictionary(self) -> dict[str, Any]:
        """Returns dictionary representation.

        This is the primary method - all others derive from it.
        Handle nested renderables by calling their render_dictionary().
        """
        ...

    def render_json(self, compact: bool = False, indent: int = 2) -> str:
        """Returns JSON string.

        Args:
            compact: Minimize whitespace if True
            indent: Spaces per level (ignored if compact)
        """
        ...

    def render_markdown(self) -> tuple[str, ...]:
        """Returns markdown lines.

        Caller decides Rich vs plain based on terminal capabilities.
        Returns tuple of lines for maximum flexibility.
        """
        ...

    def render_toml(self) -> str:
        """Returns TOML string."""
        ...
```

### Omniexception Rendering

All exceptions inherit these from `Omniexception`:

```python
def render_dictionary(self) -> dict[str, Any]:
    """Default: {class: str, message: str}

    Override to add context fields:
        base = super().render_dictionary()
        base.update({'field': self.field, ...})
        return base
    """

def render_json(self, compact: bool = False, indent: int = 2) -> str:
    """Standard JSON rendering from dictionary."""

def render_markdown(self) -> tuple[str, ...]:
    """Default: Simple formatted message.

    Override for custom markdown formatting.
    """

def render_toml(self) -> str:
    """Standard TOML rendering from dictionary."""
```

---

## Usage Patterns

### Exception with Context

```python
class ValidationError(Omnierror):
    def __init__(self, field: str, value: Any, constraint: str):
        super().__init__(f"Validation failed for '{field}': {constraint}")
        self.field = field
        self.value = value
        self.constraint = constraint

    def render_dictionary(self) -> dict[str, Any]:
        base = super().render_dictionary()
        base.update({
            'field': self.field,
            'value': repr(self.value),
            'constraint': self.constraint,
        })
        return base
```

### Result Object

```python
class AnalysisResult(Renderable):
    """Implements protocol structurally."""

    files_checked: int
    issues_found: int

    def render_dictionary(self) -> dict[str, Any]:
        return {
            'files_checked': self.files_checked,
            'issues_found': self.issues_found,
            'status': 'pass' if self.issues_found == 0 else 'fail',
        }

    # render_json, render_markdown, render_toml inherited if base class provides
```

### Rendering in CLI

```python
async def render_and_print(auxdata: Globals, renderable: Renderable):
    display = auxdata.display
    stream = await display.provide_stream(auxdata.exits)

    match display.presentation:
        case Presentations.Json:
            text = renderable.render_json(compact=display.compact)
        case Presentations.Markdown:
            lines = renderable.render_markdown()
            if display.determine_colorization(stream):
                # Use rich.markdown.Markdown
                pass
            else:
                # Strip markdown formatting
                text = '\n'.join(strip_markdown(line) for line in lines)
        case Presentations.Toml:
            text = renderable.render_toml()

    print(text, file=stream)
```

---

## Integration with unreleased library

Consider adopting:

### High Priority

1. **`remove_ansi_c1_sequences()`** - Strip ANSI codes for plain text output
2. **`_count_columns_visual()`** - Accurate column counting with wide chars
3. **Rich console pattern** - Consistent Rich console configuration

### Medium Priority

4. **Exception formatting template** - Configurable exception display
5. **Text wrapping with ANSI** - Sophisticated markdown wrapping

### Low Priority

6. **TextualizerControl** - Consider as alternative to DisplayOptions for render methods (avoids cyclic imports)

---

## Implementation Notes

### Default `render_markdown()` Implementation

Simple key-value formatting:
```python
def render_markdown(self) -> tuple[str, ...]:
    data = self.render_dictionary()
    lines = []

    if 'class' in data:
        lines.append(f"## {data['class']}")
        lines.append("")

    for key, value in data.items():
        if key == 'class':
            continue
        formatted_key = key.replace('_', ' ').title()
        lines.append(f"**{formatted_key}**: {value}")

    return tuple(lines)
```

Subclasses override for better control.

### Exception Rendering Considerations

- **Exception groups**: Handle in future iteration
- **Tracebacks**: Optional, via separate method or flag
- **Context fields**: Include via `render_dictionary()` override

### Testing Strategy

```python
def test_rendering():
    error = ValidationError('email', 'bad', 'must be valid')

    # Dictionary
    data = error.render_dictionary()
    assert data['field'] == 'email'

    # JSON round-trip
    json_str = error.render_json()
    assert json.loads(json_str) == data

    # Compact JSON
    compact = error.render_json(compact=True)
    assert '\n' not in compact

    # Markdown
    lines = error.render_markdown()
    assert any('email' in line for line in lines)
```

---

## Migration Guide

For projects like vibe-py-linter and gh-repositor:

1. **Update exception base**: Inherit from appcore's `Omniexception`
2. **Rename methods**: `render_as_json()` → override `render_dictionary()`, use inherited `render_json()`
3. **Update display**: Use `DisplayOptions` subclass with `render_and_print()`

---

## Open Questions

1. **Module location**: Keep in `cli.standard` or create separate `renderables` module?
2. **Control object**: Use `DisplayOptions` or adopt `TextualizerControl` pattern from unreleased library?
3. **Default markdown**: How sophisticated should the default key-value formatting be?

---

## References

- **Librovore**: Markdown rendering with colorization detection
- **vibe-py-linter**: Exception and result rendering patterns
- **gh-repositor**: Error interception and markdown output
- Unreleased Library: Text wrapping, ANSI handling, Rich console configuration
