# Design: Rendering Protocol

## Context

CLI applications need objects (exceptions, results, data structures) to render
themselves in multiple formats (JSON, Markdown, TOML). The system must be
non-intrusive, working through structural typing rather than forced inheritance.

## Goals / Non-Goals

**Goals:**
- Uniform interface for rendering any object type
- Multiple output formats: JSON, Markdown, TOML
- Non-intrusive: objects gain rendering without forced inheritance
- Works with exceptions, dataclasses, and custom objects

**Non-Goals:**
- Rich markdown rendering in `render_markdown()` (caller handles Rich vs plain)
- Automatic rendering for arbitrary third-party objects
- Streaming or incremental rendering

## Decisions

### Protocol-Based Approach

**Decision:** The `Renderable` protocol is owned by `ictr` and imported by appcore.
It uses the `as_` prefix naming convention (`render_as_dictionary()`,
`render_as_json()`, `render_as_markdown()`).

**Rationale:**
- Renderables are the shared primitive between ictr and appcore
- ictr owns the protocol as the cross-package contract
- appcore extends it with `render_as_toml()` (appcore-specific)
- No forced inheritance required; structural typing via `@runtime_checkable`

**Location:** The protocol lives in ictr (considering move to package level).
appcore's `cli/standard.py` imports it and extends with TOML rendering.

### Dictionary as Source of Truth

**Decision:** `render_as_dictionary()` is the primary method; `render_as_json()`,
`render_as_markdown()`, and `render_as_toml()` derive from it.

**Rationale:**
- Single place to define object structure
- Consistent across all formats
- Easy to override with custom data
- Default implementations reduce boilerplate

### Rendering Methods on Exceptions

**Decision:** `Omniexception` in `exceptions.py` provides concrete rendering
methods that all package exceptions inherit.

**Rationale:**
- All exceptions automatically gain rendering capability
- Non-breaking change (methods are additive)
- Subclasses can override for custom rendering
- Separate from ictr's linearizer-based exception rendering — different purposes:
  appcore's rendering is for structured output (JSON/Markdown/TOML), ictr's is
  for human-readable diagnostic messages

### Markdown Rendering Takes DisplayOptions

**Decision:** `render_as_markdown(display: DisplayOptions)` takes display options
as a parameter, unlike `render_as_json()` and `render_as_toml()`.

**Rationale:**
- Markdown rendering may need colorization context
- Avoids storing display state on the renderable object
- Exception `render_markdown()` is simpler (no display param) since it doesn't
  need colorization control

### Presentation Enum

**Decision:** `Presentations` enum in `cli/standard.py` with `Json`, `Markdown`,
`Toml` values. Use `compact` boolean flag rather than separate `CompactJson`.

**Rationale:**
- Simpler than multiple JSON variants
- `compact` flag could apply to other formats
- Cleaner API: `render_json(compact=True)`

## Risks / Trade-offs

- **Risk:** `render_as_markdown()` is a stub on `Renderable` (returns empty tuple)
  → Mitigation: Subclasses must override; exception rendering is concrete
- **Risk:** Two rendering method signatures (with/without `display`)
  → Mitigation: Exceptions are a separate concern from CLI renderables
- **Risk:** Protocol owned by ictr creates cross-package dependency
  → Mitigation: ictr is already a required dependency; protocol is stable

## Implementation Notes

The `Renderable` protocol is owned by ictr. The protocol hierarchy:
- `DictionaryRenderable` — defines `render_as_dictionary()` (base)
- `JsonRenderable(DictionaryRenderable)` — adds `render_as_json()`
- `MarkdownRenderable(DictionaryRenderable)` — adds `render_as_markdown()`

ictr is considering hoisting `DictionaryRenderable` to package level as `Renderable`.
appcore imports and extends with TOML rendering:

```python
# In cli/standard.py — extends ictr's protocols
class AppcoreRenderable(ictr.JsonRenderable, ictr.MarkdownRenderable):
    def render_as_toml(self) -> str: ...
```

The `Omniexception` rendering methods in `exceptions.py`:

```python
class Omniexception(immut.exceptions.Omniexception):
    def render_as_dictionary(self) -> dict[str, Any]: ...
    def render_as_json(self, compact: bool = False, indent: int = 2) -> str: ...
    def render_as_markdown(self) -> tuple[str, ...]: ...
    def render_as_toml(self) -> str: ...
```

The `render_and_print()` function dispatches on `display.presentation` to
select the appropriate rendering method. stdout rendering is separate from
ictr's diagnostic pipeline which targets stderr.
