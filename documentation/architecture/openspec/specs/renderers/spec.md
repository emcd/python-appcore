# Rendering

## Requirements

### Requirement: Renderable Protocol

The `Renderable` protocol SHALL be owned by `ictr` and imported by appcore.
The protocol uses the `as_` prefix naming convention.

#### Scenario: Protocol compliance
- **WHEN** a class implements `render_as_dictionary()` returning a `dict[str, Any]`
- **THEN** it satisfies the `DictionaryRenderable` protocol
- **AND** to also support JSON/Markdown rendering, it must additionally satisfy
  `JsonRenderable` and/or `MarkdownRenderable`

#### Scenario: Runtime checkability
- **WHEN** `isinstance(obj, Renderable)` is evaluated
- **THEN** structural typing is checked at runtime
- **AND** objects implementing the protocol are recognized without explicit inheritance

#### Scenario: Appcore TOML extension
- **WHEN** appcore needs TOML rendering
- **THEN** it extends the ictr `Renderable` protocol with `render_as_toml()`
- **AND** the extension is appcore-specific, not part of ictr's protocol

### Requirement: Dictionary Rendering

`render_as_dictionary()` SHALL be the primary method from which all other
rendering formats derive.

#### Scenario: Default dictionary structure
- **WHEN** `render_as_dictionary()` is called on a `Renderable`
- **THEN** it returns a `dict[str, Any]` with the object's key attributes
- **AND** nested `Renderable` objects have their `render_as_dictionary()` called recursively

### Requirement: JSON Rendering

`render_as_json()` SHALL produce JSON output from the dictionary representation.

#### Scenario: Pretty-printed JSON
- **WHEN** `render_as_json()` is called with default arguments
- **THEN** JSON is produced with 2-space indentation
- **AND** non-ASCII characters are preserved (`ensure_ascii=False`)

#### Scenario: Compact JSON
- **WHEN** `render_as_json(compact=True)` is called
- **THEN** JSON is produced with minimal whitespace (no indentation)
- **AND** separators are `(',', ':')`

### Requirement: TOML Rendering

`render_as_toml()` SHALL produce TOML output from the dictionary representation.
This is an appcore-specific extension to ictr's `Renderable` protocol.

#### Scenario: TOML serialization
- **WHEN** `render_as_toml()` is called
- **THEN** the dictionary is serialized to a valid TOML string
- **AND** uses `tomli_w.dumps()` for serialization

### Requirement: Exception Rendering

`Omniexception` SHALL provide rendering methods that all package exceptions
inherit. Exception rendering for structured output (JSON/Markdown/TOML) is
distinct from ictr's linearizer-based exception rendering for diagnostic
messages — the two coexist and serve different purposes.

#### Scenario: Exception dictionary rendering
- **WHEN** `render_as_dictionary()` is called on any package exception
- **THEN** the result contains `class`, `fqclass`, and `message` keys
- **AND** subclasses can override to add context fields

#### Scenario: Exception JSON rendering
- **WHEN** `render_as_json()` is called on a package exception
- **THEN** the exception is serialized to JSON via its dictionary representation

#### Scenario: Exception Markdown rendering
- **WHEN** `render_as_markdown()` is called on a package exception
- **THEN** a single-line summary is returned in `[**fqclass**] message` format

### Requirement: Display-Driven Rendering

`render_and_print()` SHALL render objects according to display options and
write to the configured output stream (stdout). This is separate from ictr's
diagnostic pipeline which targets stderr.

#### Scenario: JSON presentation
- **WHEN** `render_and_print()` is called with `presentation=Json`
- **THEN** `render_as_json(compact=display.compact)` is called
- **AND** the result is printed to the display stream

#### Scenario: Markdown presentation
- **WHEN** `render_and_print()` is called with `presentation=Markdown`
- **THEN** `render_as_markdown(display)` is called
- **AND** lines are joined with newlines and printed to the display stream

#### Scenario: TOML presentation
- **WHEN** `render_and_print()` is called with `presentation=Toml`
- **THEN** `render_as_toml()` is called
- **AND** the result is printed to the display stream
