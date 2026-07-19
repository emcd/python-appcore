# Design: Immutable State Management

## Context

Application frameworks must manage global state including configuration,
platform directories, distribution information, and resource handles. Mutable
global state creates thread safety issues, debugging complexity, and unexpected
side effects.

Python's dataclass system provides immutable patterns, and accretive data
structures offer append-only dictionary implementations. The framework needs
predictable state management that supports concurrent access patterns.

## Goals / Non-Goals

**Goals:**
- Thread-safe global state without explicit locking
- Predictable behavior and easy debugging
- State updates are explicit and traceable
- Testing isolation through independent state instances

**Non-Goals:**
- Mutable state with change notification
- Context-based state isolation (would complicate CLI patterns)
- State persistence across process boundaries

## Decisions

### Immutable Dataclass Architecture

**Decision:** Use immutable dataclasses for all application state management.
The `Globals` dataclass contains all framework state as immutable fields.
Configuration is stored as accretive dictionary objects that are immutable
after assignment. State updates create new instances rather than modifying
existing ones.

**Alternatives considered:**
- Mutable global state with locking — Rejected: complex locking strategies,
  error-prone thread safety, debugging difficulties
- Traditional singleton patterns — Rejected: prevents testing with different
  configurations, creates hidden dependencies
- Context manager state isolation — Rejected: complicates API, complex context
  propagation, integration complexity with CLI patterns

### Accretive Configuration Containers

**Decision:** Configuration dictionaries use `accretive.Dictionary` which can
grow but never shrink. Once assigned to `Globals`, the configuration reference
cannot be replaced.

**Rationale:** Prevents accidental configuration loss while maintaining the
immutability guarantee. Configuration merging happens during `prepare()`, not
after state assembly.

### Location Resolution with Template Variables

**Decision:** `Globals` provides `provide_*_location()` methods that resolve
platform directories with optional configuration overrides. Template variables
allow flexible path customization.

**Rationale:** Applications need to customize storage locations without
subclassing or modifying framework code. Template approach keeps configuration
declarative.

## Risks / Trade-offs

- **Risk:** Slight memory overhead from creating new instances for updates
  → Mitigation: State updates are rare (typically only at initialization)
- **Risk:** Learning curve for developers expecting mutable global state
  → Mitigation: Clear documentation, explicit API naming
- **Risk:** Requires careful design of state update patterns
  → Mitigation: All updates go through `prepare()`, no post-init mutation

## Implementation Notes

The `Globals` dataclass:

```python
class Globals(immut.DataclassObject):
    application: Information
    configuration: accret.Dictionary[str, Any]
    directories: PlatformDirs
    distribution: Information
    exits: AsyncExitStack
```

All fields are frozen. The `accret.Dictionary` type allows initial population
during `prepare()` but prevents subsequent mutation.
