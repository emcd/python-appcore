# Design: CLI Command Routing

## Context

CLI applications need flexible command routing that supports subcommands,
argument parsing, and help generation. Traditional approaches use string-based
routing or complex decorator patterns that lack type safety and IDE support.

The framework integrates with `tyro` for argument parsing and needs routing
patterns that work with type annotations, support `isinstance()` checks, and
enable clean command composition patterns.

## Goals / Non-Goals

**Goals:**
- Type-safe command routing with full IDE support
- Clean integration with `tyro` argument parsing
- Commands are regular classes enabling standard inheritance patterns
- Easy testing through direct class instantiation

**Non-Goals:**
- Decorator-based command registration
- Dynamic command discovery at runtime
- Plugin-based command loading
- Shell completion (deferred to future work)

## Decisions

### Type Guard Command Routing

**Decision:** Use `isinstance()` type guards for command routing within CLI
applications. Commands inherit from base `Command` class and applications
route using type checks, following the Liskov Substitution Principle.

**Alternatives considered:**
- String-based command routing — Rejected: lacks type safety and IDE
  integration, requires manual argument parsing
- Decorator-based routing — Rejected: creates coupling between routing logic
  and command implementation, complicates testing
- Registry-based command discovery — Rejected: requires explicit registration,
  creates hidden dependencies, complicates module organization

### Tyro Integration for Argument Parsing

**Decision:** Use `tyro` for automatic argument parsing and help generation
based on type annotations. Command classes define their arguments as typed
fields with optional defaults and docstrings.

**Rationale:** `tyro` provides type-safe argument parsing with excellent IDE
support. It generates help text automatically from type annotations and
docstrings, reducing boilerplate.

### Display Options as Dataclass

**Decision:** `DisplayOptions` is an immutable dataclass controlling output
presentation (format, colorization, stream routing). It integrates with
`inscription.Control` for logging configuration.

**Rationale:** Display configuration is a natural data structure, not behavior.
A dataclass provides clear, typed configuration with sensible defaults.

### Call-Based Application Lifecycle

**Decision:** `Application` instances are callable. Calling an application
triggers argument parsing, preparation, and execution in sequence.

**Rationale:** Simple, predictable lifecycle. The callable pattern is familiar
in Python and works naturally with `asyncio.run()`.

## Risks / Trade-offs

- **Risk:** Requires explicit `isinstance()` checks in application routing logic
  → Mitigation: Pattern is explicit and readable; IDE support for type narrowing
- **Risk:** Command inheritance hierarchy must be carefully designed
  → Mitigation: Clear base class documentation and examples
- **Risk:** Learning curve for developers expecting decorator-based routing
  → Mitigation: Comprehensive examples showing common patterns

## Implementation Notes

Core class relationships:

```python
class Command(ABC):
    async def execute(self, auxdata: Globals) -> None: ...

class Application(immut.DataclassObject):
    commands: tuple[type[Command], ...]

    async def prepare(self, exits: AsyncExitStack) -> Globals: ...
    async def execute(self, auxdata: Globals) -> None: ...

    def __call__(self) -> None:
        # tyro.cli() parses arguments, then execute()
        ...
```

Display options integrate with `inscription` for logging and `rich` for
terminal-aware formatting. The `DisplayOptions` class provides
`determine_colorization()` to check terminal capabilities.
