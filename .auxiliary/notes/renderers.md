# Rendering Protocol Design Document

**Status**: Ready for Implementation
**Decision Date**: 2025-11-18
**Implementation**: Deferred

This document contains the complete design specification for a rendering protocol toolkit for appcore. All design decisions have been finalized and the implementation is ready to proceed when needed.

---

# Rendering Protocol Observations

## Current State in Appcore

### CLI Module (`sources/appcore/cli.py`)
- Defines `DisplayOptions` with stream routing and colorization control
- Supports file and stream output destinations (stdout/stderr)
- Has Rich terminal detection capabilities
- No rendering protocol yet - just infrastructure

### Introspection Module (`sources/appcore/introspection.py`)
- Extends `DisplayOptions` with `Presentations` enum (Json, Plain, Rich, Toml)
- Implements `render()` method that dispatches to format-specific renderers:
  - `_render_plain()` - Simple key-value text output
  - `_render_rich()` - Rich console formatting
  - JSON via `json.dumps()`
  - TOML via `tomli_w.dumps()`
- Works with dictionary data structures
- Tightly coupled to `DisplayOptions` class

### Exceptions Module (`sources/appcore/exceptions.py`)
- Defines `Omniexception` base class inheriting from `BaseException`
- Defines `Omnierror` base class inheriting from both `Omniexception` and `Exception`
- **No rendering methods** - just standard exception behavior
- Various specialized exceptions for different failure modes

## Patterns in External Projects

### vibe-py-linter

**Exception Rendering:**
- `Omnierror` implements two rendering methods:
  - `render_as_json()` → returns `dict` with `{type, message}`
  - `render_as_text()` → returns `tuple[str, ...]` (lines)
- Specialized exceptions (e.g., `RuleExecuteFailure`) override these methods to include contextual data

**Result Protocol:**
- Defines `RenderableResult` protocol requiring:
  - `render_as_json()` → `dict`
  - `render_as_text()` → `tuple[str, ...]`
- Command results (e.g., `CheckResult`, `FixResult`) implement this protocol
- CLI uses `_render_and_print_result()` helper that checks display format and calls appropriate method

**Error Interception:**
- `intercept_errors()` context manager catches `Omnierror` exceptions
- Renders errors using the exception's own rendering methods
- Respects display format (text vs JSON)

### gh-repositor

**Exception Rendering:**
- `Omnierror` implements two rendering methods:
  - `render_as_json()` → returns `dict` with `{type, message}`
  - `render_as_markdown()` → returns `tuple[str, ...]` (lines)
- Specialized exceptions include HTTP status codes and contextual details

**Error Interception:**
- `intercept_errors()` decorator wraps CLI handlers
- Catches both `Omnierror` (rendered contextually) and generic exceptions (logged + formatted as JSON)
- Uses exception rendering methods to produce output

## Key Patterns Identified

### 1. Protocol-Based Rendering
Both projects define protocols/interfaces for renderable objects:
- Exceptions implement rendering methods directly
- Results/responses also implement the same protocol
- Allows uniform handling of different object types

### 2. Multiple Output Formats
Common formats across projects:
- **JSON** - Structured data for programmatic consumption (universal)
- **Text/Plain** - Simple human-readable output (vibe-py-linter)
- **Markdown** - Rich formatted output (gh-repositor)
- **Rich** - Terminal-specific formatting (appcore introspection)
- **TOML** - Configuration format (appcore introspection)

### 3. Dictionary as Intermediate Representation
- JSON rendering typically returns a dictionary first
- Dictionary can be serialized to JSON, TOML, or other formats
- Provides flexibility for consumers

### 4. Rendering Method Signatures
Two approaches seen:
1. **Return structured data** (vibe-py-linter, gh-repositor):
   - `render_as_json() → dict`
   - `render_as_text() → tuple[str, ...]`
   - `render_as_markdown() → tuple[str, ...]`
2. **Direct output** (appcore introspection):
   - `render(data) → None` (writes to stream)

### 5. Error Handling Integration
- Exceptions are first-class renderable objects
- Error interceptors use rendering methods to format output
- Consistent error presentation across different output modes

## Design Considerations for Appcore

### Non-Intrusive Extension Strategy

To avoid breaking existing interfaces, we should:

1. **Protocol Definition** - Create optional protocol that objects can implement
2. **Backward Compatibility** - Existing `Omniexception` classes continue to work without changes
3. **Opt-In Enhancement** - New exceptions can implement protocol for enhanced rendering
4. **Default Implementations** - Provide base implementations in `Omnierror` that can be inherited

### Proposed Protocol Interface

```python
class RenderableResult(Protocol):
    """Protocol for objects that can render themselves in multiple formats."""

    def render_dictionary(self) -> dict[str, Any]:
        """Returns dictionary representation."""
        ...

    def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
        """Returns JSON string representation.

        Args:
            compact: If True, minimize whitespace
            indent: Indentation spaces (ignored if compact=True)
        """
        ...

    def render_markdown(self) -> tuple[str, ...]:
        """Returns markdown lines for rich formatting."""
        ...
```

### Default Implementation Strategy

1. **`render_dictionary()`** - Abstract/to be overridden by subclasses
   - For exceptions: `{type, message, context_fields...}`
   - For results: domain-specific structure

2. **`render_json()`** - Default implementation wraps `render_dictionary()`
   ```python
   def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
       if compact:
           return json.dumps(self.render_dictionary(), ensure_ascii=False, separators=(',', ':'))
       return json.dumps(self.render_dictionary(), indent=indent, ensure_ascii=False)
   ```

3. **`render_markdown()`** - Default implementation formats dictionary as markdown
   - Creates simple key-value formatting
   - Can be overridden for custom markdown layouts

4. **`render_toml()`** - Default implementation wraps `render_dictionary()`
   ```python
   def render_toml(self) -> str:
       import tomli_w
       return tomli_w.dumps(self.render_dictionary())
   ```

### Integration with Introspection Module

Current `introspection.DisplayOptions.render()` method:
- Takes arbitrary data and renders based on presentation mode
- Tightly coupled to dictionary inputs

Enhanced approach:
- Check if data implements `RenderableResult` protocol
- If yes, use appropriate rendering method
- If no, fall back to current dictionary-based rendering
- Maintains backward compatibility

### Module Organization

**Decision**: New `renderers.py` module for clarity and discoverability.

This module will contain:
- `RenderableProtocol` - The protocol definition for structural typing
- `Renderable` - Base class with default implementations (see naming discussion below)
- Helper functions for common rendering tasks

## Implementation Roadmap

1. **Phase 1: Protocol and Base Class**
   - Create `renderers.py` module
   - Define `RenderableProtocol` for structural typing
   - Provide `Renderable` base class with default implementations
   - Create `DisplayOptionsDefault` as subclass of `cli.DisplayOptions` with presentations

2. **Phase 2: Exception Enhancement**
   - Add default `render_*` methods to `Omniexception` base class
   - Provide sensible defaults for exceptions (type + message)
   - Subclasses can override methods as needed
   - No protocol requirement - purely optional enhancement

3. **Phase 3: Display Integration**
   - Update `DisplayOptionsDefault.render()` to check for rendering protocol
   - Maintain backward compatibility with dictionary inputs
   - Use `determine_colorization()` to decide Rich vs plain markdown

4. **Phase 4: Documentation & Examples**
   - Add protocol usage examples
   - Document how to create custom renderable exceptions
   - Show integration patterns for CLI results

## Benefits of This Approach

1. **Non-Breaking** - Existing code continues to work unchanged
2. **Opt-In** - Projects can adopt rendering protocol incrementally
3. **Consistent** - Uniform interface across exceptions and results
4. **Flexible** - Multiple output formats from single source of truth
5. **Testable** - Easy to verify rendering output in tests
6. **Discoverable** - Protocol-based design guides usage via type hints

## Design Decisions (Resolved)

1. **`render_markdown()` return type**: `tuple[str, ...]` (lines)
   - **Rationale**: More flexible, caller decides how to join lines
   - Allows wrapping, filtering, or other transformations

2. **Plain text vs Rich rendering**: Use existing `determine_colorization()` pattern
   - **Rationale**: Following Librovore pattern - `render_markdown()` returns markdown lines
   - Display layer checks `determine_colorization(stream)` to decide Rich vs plain
   - No separate `render_plain()` or `rich` flag needed
   - See Librovore implementation for reference

3. **Nested object rendering**: Handled by `render_dictionary()`
   - **Rationale**: Responsibility of the primary render method
   - Custom `render_markdown()` implementations can handle as needed
   - Other renderers derive from dictionary representation

4. **TOML support**: Yes, add `render_toml()` to the protocol
   - **Rationale**: Useful for configuration introspection
   - Can use pygments for colored output eventually
   - Uncolored tomli-w output is fine to start

5. **Error handling in rendering methods**: Use `intercept_errors` context manager
   - **Rationale**: Consistent error handling approach
   - Prevents rendering failures from crashing the application
   - Allows graceful degradation

6. **Compact JSON**: Use `compact: bool` parameter on `render_json()`
   - **Rationale**: Simpler API than separate method
   - **Presentation**: Add `CompactJson` variant to `Presentations` enum
   - Both `Json` and `CompactJson` route through `render_json()` with different `compact` flag

7. **Naming Convention**: `RenderableProtocol` + `Renderable`
   - **RenderableProtocol**: For structural typing (objects not using immutable dataclasses)
   - **Renderable**: Immutable base dataclass with rendering methods
   - **Usage**: Choose based on whether using appcore's immutable dataclasses or not

8. **Presentation Modes**: Simplified enum without redundancy
   - **Keep**: `Json`, `CompactJson`, `Markdown`, `Toml`
   - **Remove**: `Plain`, `Rich` (redundant with `Markdown`)
   - **Decision**: Use `colorize` boolean + TTY + `NO_COLOR` detection to determine Rich vs plain rendering
   - Markdown presentation automatically adapts based on terminal capabilities

9. **No Legacy Fallbacks**: Strict rendering protocol enforcement
   - **Rationale**: Either object is renderable or it's not
   - **Implementation**: Attempting to render non-renderable object is a failure
   - **Benefit**: Clear contracts, no hidden complexity

## Detailed Design Specification

### Rendering Protocol Design

Based on the analysis above, here's a concrete design for the rendering toolkit:

#### Core Protocol

```python
# sources/appcore/renderers.py

from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class RenderableProtocol(Protocol):
    """Protocol for objects that can render themselves in multiple formats.

    This protocol defines a standard interface for objects that need to
    present themselves in different output formats. It provides a
    dictionary-centric approach where `render_dictionary()` serves as the
    source of truth, and other formats derive from it.

    Note: Objects don't need to explicitly implement this protocol.
    Having the required methods is sufficient (structural subtyping).

    Example::

        class MyResult:
            def __init__(self, status: str, count: int):
                self.status = status
                self.count = count

            def render_dictionary(self) -> dict[str, Any]:
                return {'status': self.status, 'count': self.count}

            # Other methods can be inherited from Renderable base class
    """

    def render_dictionary(self) -> dict[str, Any]:
        """Returns dictionary representation.

        This is the primary rendering method. All other formats should
        derive from this representation for consistency.

        Nested objects that also implement RenderableProtocol should be
        handled here by calling their render_dictionary() methods.

        Returns:
            Dictionary containing all relevant data for rendering.
        """
        ...

    def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
        """Returns JSON string representation.

        Args:
            compact: If True, minimize whitespace for size optimization
            indent: Number of spaces for indentation (default: 2, ignored if compact=True)

        Returns:
            JSON string, formatted or compact based on parameters.
        """
        ...

    def render_markdown(self) -> tuple[str, ...]:
        """Returns markdown lines for rendering.

        The caller decides whether to render with Rich terminal formatting
        or as plain text based on terminal capabilities (TTY detection,
        NO_COLOR environment variable, and colorize setting).

        Returns:
            Tuple of strings, each representing a line of markdown output.
            Caller joins lines and optionally renders with Rich or strips
            formatting for plain text output.
        """
        ...

    def render_toml(self) -> str:
        """Returns TOML string representation.

        Useful for configuration-related results and introspection.

        Returns:
            TOML-formatted string.
        """
        ...
```

#### Base Class with Default Implementations

```python
# sources/appcore/renderers.py

import json
from abc import abstractmethod

class Renderable(__.immut.DataclassObject):
    """Immutable base dataclass providing rendering methods.

    Subclasses only need to implement `render_dictionary()`. All other
    rendering methods are provided with sensible defaults.

    Use this base class when creating result objects or other renderable
    entities that should be immutable dataclasses.

    For structural typing without inheritance, use RenderableProtocol.

    Example::

        class MyResult(Renderable):
            status: str
            count: int

            def render_dictionary(self) -> dict[str, Any]:
                return {'status': self.status, 'count': self.count}

            # render_json, render_markdown, render_toml inherited
    """

    @abstractmethod
    def render_dictionary(self) -> dict[str, Any]:
        """Returns dictionary representation.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
        """Returns JSON string representation."""
        if compact:
            return json.dumps(
                self.render_dictionary(),
                ensure_ascii=False,
                separators=(',', ':'),
            )
        return json.dumps(
            self.render_dictionary(),
            indent=indent,
            ensure_ascii=False,
        )

    def render_markdown(self) -> tuple[str, ...]:
        """Returns markdown lines for rich formatting.

        Default implementation creates a simple key-value table.
        Subclasses can override for custom markdown formatting.

        The caller decides whether to render with Rich or as plain text
        using DisplayOptions.determine_colorization().
        """
        data = self.render_dictionary()
        lines = []

        # Add type header if present
        if 'type' in data:
            lines.append(f"## {data['type']}")
            lines.append("")

        # Add key-value pairs
        for key, value in data.items():
            if key == 'type':
                continue  # Already handled
            # Format the key as bold
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"**{formatted_key}**: {value}")

        return tuple(lines)

    def render_toml(self) -> str:
        """Returns TOML string representation.

        Default implementation uses tomli_w to dump the dictionary.
        """
        import tomli_w
        return tomli_w.dumps(self.render_dictionary())
```

### Enhanced Exception Classes

**Key Decision**: Default rendering methods are added to `Omniexception`, not `Omnierror`.
This makes rendering available to all exceptions, not just errors.

```python
# sources/appcore/exceptions.py

from . import renderers
import json

class Omniexception(
    __.immut.Object, BaseException,
    instances_mutables = ( '__cause__', '__context__' ),
    instances_visibles = (
        '__cause__', '__context__', __.immut.is_public_identifier ),
):
    """Base for all exceptions raised by package API.

    Provides default rendering methods that subclasses can override.
    Does NOT explicitly implement RenderableProtocol - just provides the methods.
    """

    def render_dictionary(self) -> dict[str, Any]:
        """Returns dictionary representation of the exception.

        Default implementation includes exception type and message.
        Subclasses can override to add context fields.

        Example::

            def render_dictionary(self) -> dict[str, Any]:
                base = super().render_dictionary()
                base.update({'field': self.field, 'value': self.value})
                return base
        """
        return {
            'type': type(self).__name__,
            'message': str(self),
        }

    def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
        """Returns JSON string representation."""
        if compact:
            return json.dumps(
                self.render_dictionary(),
                ensure_ascii=False,
                separators=(',', ':'),
            )
        return json.dumps(
            self.render_dictionary(),
            indent=indent,
            ensure_ascii=False,
        )

    def render_markdown(self) -> tuple[str, ...]:
        """Returns markdown lines for exception display.

        Default implementation provides simple formatting.
        Subclasses can override for custom presentation.
        """
        data = self.render_dictionary()
        lines = []

        if 'type' in data:
            lines.append(f"## {data['type']}")
            lines.append("")

        for key, value in data.items():
            if key == 'type':
                continue
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"**{formatted_key}**: {value}")

        return tuple(lines)

    def render_toml(self) -> str:
        """Returns TOML string representation."""
        import tomli_w
        return tomli_w.dumps(self.render_dictionary())


class Omnierror(Omniexception, Exception):
    """Base for error exceptions raised by package API.

    Inherits all rendering methods from Omniexception.
    No additional rendering functionality needed here.

    Example of custom rendering::

        class ValidationError(Omnierror):
            def __init__(self, field: str, value: Any, constraint: str):
                super().__init__(
                    f"Validation failed for '{field}': {constraint}"
                )
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
    """
```

### Display Options Enhancement

**Key Decision**: Create `DisplayOptionsDefault` as a subclass of `cli.DisplayOptions`
with presentations enum, rather than modifying the base `DisplayOptions` class.

This will likely be moved to the `renderers.py` module or remain in introspection.

```python
# sources/appcore/renderers.py (or introspection.py)

from . import cli as _cli
from . import renderers as _renderers

class Presentations(__.enum.Enum):  # TODO: Python 3.11: StrEnum
    """Presentation mode (format) for display output."""

    Json        = 'json'
    CompactJson = 'compact-json'
    Markdown    = 'markdown'  # Adapts to terminal: Rich or plain
    Toml        = 'toml'


class DisplayOptionsDefault(_cli.DisplayOptions):
    """Display options with presentation mode support.

    Extends base DisplayOptions with format selection and rendering
    protocol support. Applications can subclass this or use as-is.
    """

    presentation: __.typx.Annotated[
        Presentations,
        _tyro.conf.arg(help="Output presentation mode (format)."),
    ] = Presentations.Markdown

    async def render(self, data: __.typx.Any) -> None:
        """Renders data according to display options.

        Args:
            data: Object implementing RenderableProtocol

        Raises:
            TypeError: If data does not implement RenderableProtocol
        """
        if not isinstance(data, _renderers.RenderableProtocol):
            raise TypeError(
                f"Object must implement RenderableProtocol to be rendered. "
                f"Got {type(data).__name__} instead."
            )

        async with __.ctxl.AsyncExitStack() as exits:
            target = await self.provide_stream(exits)
            self._render_protocol_object(data, target)

    def _render_protocol_object(
        self, data: _renderers.RenderableProtocol, target: __.typx.TextIO
    ) -> None:
        """Renders an object that implements RenderableProtocol."""
        match self.presentation:
            case Presentations.Json:
                print(data.render_json(compact=False), file=target)

            case Presentations.CompactJson:
                print(data.render_json(compact=True), file=target)

            case Presentations.Markdown:
                # Use determine_colorization to decide Rich vs plain
                lines = data.render_markdown()
                if self.determine_colorization(target):
                    # Rich markdown rendering
                    from rich.console import Console
                    from rich.markdown import Markdown
                    console = Console(
                        file=target,
                        force_terminal=True,
                        color_system='auto' if self.colorize else None
                    )
                    markdown_text = '\n'.join(lines)
                    console.print(Markdown(markdown_text))
                else:
                    # Plain text - strip markdown formatting
                    for line in lines:
                        plain_line = line.replace('**', '').replace('##', '').strip()
                        if plain_line:
                            print(plain_line, file=target)

            case Presentations.Toml:
                print(data.render_toml(), file=target)
```

### Complete Usage Patterns

#### 1. Exception with Custom Context

```python
class ValidationError(exceptions.Omnierror):
    """Validation error with field context."""

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

#### 2. Result Object as Immutable Dataclass

```python
from appcore import renderers

class AnalysisResult(renderers.Renderable):
    """Immutable result from analysis operation."""

    files_checked: int
    issues_found: int
    duration: float

    def render_dictionary(self) -> dict[str, Any]:
        return {
            'files_checked': self.files_checked,
            'issues_found': self.issues_found,
            'duration_seconds': round(self.duration, 2),
            'status': 'pass' if self.issues_found == 0 else 'fail',
        }
```

#### 3. Structural Typing Without Inheritance

```python
# Object that implements protocol without inheriting
class CustomResult:
    def __init__(self, data: dict):
        self.data = data

    def render_dictionary(self) -> dict[str, Any]:
        return self.data

    def render_json(self, *, compact: bool = False, indent: int = 2) -> str:
        # Custom JSON implementation
        pass

    def render_markdown(self) -> tuple[str, ...]:
        # Custom markdown implementation
        pass

    def render_toml(self) -> str:
        # Custom TOML implementation
        pass

# Type checker recognizes this as RenderableProtocol
result: RenderableProtocol = CustomResult({'status': 'ok'})
```

#### 4. CLI Integration

```python
class MyCommand(cli.Command):
    async def execute(self, auxdata: state.Globals) -> None:
        result = AnalysisResult(
            files_checked=42,
            issues_found=3,
            duration=1.234
        )

        # Render using display options
        await auxdata.display.render(result)
```

#### 5. Error Interception

```python
async def intercept_errors(coro):
    """Catches and renders errors appropriately."""
    try:
        return await coro
    except exceptions.Omniexception as error:
        # All exceptions have rendering methods
        print(error.render_json(), file=sys.stderr)
        raise SystemExit(1)
```

### Migration Path for Existing Projects

For projects like vibe-py-linter and gh-repositor:

1. **Update exception base classes**:
   - Change to inherit from appcore's `Omniexception`/`Omnierror`
   - Remove local `render_as_json()` and `render_as_markdown()` implementations
   - Override `render_dictionary()` to provide context

2. **Update result objects**:
   - Inherit from `renderers.Renderable`
   - Implement `render_dictionary()` method
   - Remove other render methods (inherited automatically)

3. **Update display layer**:
   - Use `DisplayOptionsDefault` or subclass it
   - Call `display.render(result)` instead of manual rendering
   - Remove format detection logic (handled by display options)

### Testing Strategy

```python
# tests/test_rendering.py

def test_exception_rendering():
    """Test that exceptions render correctly in all formats."""
    error = ValidationError('email', 'bad-email', 'must be valid email')

    # Test dictionary rendering
    data = error.render_dictionary()
    assert data['type'] == 'ValidationError'
    assert data['field'] == 'email'

    # Test JSON rendering
    json_str = error.render_json()
    assert 'ValidationError' in json_str
    assert json.loads(json_str) == data  # Round-trip validation

    # Test compact JSON
    compact = error.render_json(compact=True)
    assert '\n' not in compact
    assert json.loads(compact) == data

    # Test markdown rendering
    lines = error.render_markdown()
    assert any('email' in line for line in lines)
```

### Documentation Requirements

1. **Protocol documentation** - Explain the rendering protocol and its benefits
2. **Migration guide** - How to adopt in existing projects
3. **Best practices** - When to override default implementations
4. **Examples** - Comprehensive examples for common use cases

### Performance Considerations

1. **Lazy rendering** - Only render when needed, not on exception construction
2. **Caching** - Consider caching rendered output if rendering is expensive
3. **Memory efficiency** - Dictionary representation should be lightweight

---

## Final Design Summary

This design incorporates all feedback and represents the implementation-ready specification:

### 1. Module Naming
- **Decision**: `renderers.py` instead of `rendering.py`
- **Rationale**: More concise, follows common naming patterns

### 2. Exception Protocol Implementation
- **Decision**: Default render methods on `Omniexception`, not requiring protocol implementation
- **Implementation**: All exceptions get rendering methods automatically
- **Benefit**: Completely non-intrusive - no changes needed to existing exception classes

### 3. Display Options Architecture
- **Decision**: Create `DisplayOptionsDefault` as subclass of `cli.DisplayOptions`
- **Rationale**: Keeps base `DisplayOptions` clean and minimal
- **Location**: To be determined (renderers.py or introspection.py)

### 4. Markdown Rendering Return Type
- **Decision**: `render_markdown()` returns `tuple[str, ...]` (lines)
- **Rationale**: Maximum flexibility - caller can join, wrap, or transform
- **Pattern**: Matches approach used in Librovore

### 5. Rich vs Plain Text Handling
- **Decision**: Use existing `determine_colorization()` pattern
- **Implementation**:
  - `render_markdown()` returns markdown lines
  - Display layer decides Rich vs plain based on terminal capabilities
  - No separate `render_plain()` or `rich` flag
- **Reference**: Librovore CLI implementation

### 6. Nested Object Rendering
- **Decision**: Handled by `render_dictionary()` implementation
- **Rationale**: Primary render method's responsibility
- **Flexibility**: Custom `render_markdown()` can handle differently if needed

### 7. TOML Support
- **Decision**: Yes, include `render_toml()` in protocol
- **Implementation**: Default uses tomli_w.dumps()
- **Future**: Consider pygments for colored output
- **Initial**: Uncolored output is acceptable

### 8. Error Handling
- **Decision**: Use `intercept_errors` context manager pattern
- **Application**: Wrap rendering methods to prevent failures
- **Benefit**: Graceful degradation if rendering fails

### 9. Compact JSON Parameter
- **Decision**: Use `compact: bool` parameter on `render_json()`
- **API**: `render_json(compact=True)` instead of separate method
- **Rationale**: Simpler, more Pythonic API

### 10. Default Implementations Location
- **Decision**: Place on `Omniexception`, not `Omnierror`
- **Rationale**: Makes rendering available to all exceptions
- **Impact**: `Omnierror` simply inherits, no additional code needed

### 11. Naming Convention
- **Decision**: `RenderableProtocol` + `Renderable`
- **RenderableProtocol**: For structural typing (objects not using immutable dataclasses)
- **Renderable**: Immutable base dataclass (inherits from `__.immut.DataclassObject`)
- **Exceptions**: Get render methods directly from `Omniexception`
- **Benefit**: Clear separation between protocol and concrete implementation
