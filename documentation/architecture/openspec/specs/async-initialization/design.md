# Design: Async-First Initialization

## Context

Python applications increasingly use async patterns for I/O operations, network
requests, and concurrent processing. Traditional synchronous initialization
patterns create barriers for applications that need to coordinate async resource
setup with framework initialization.

Framework initialization typically involves file system operations, configuration
loading, and logging setup that could benefit from async patterns while maintaining
deterministic initialization order.

## Goals / Non-Goals

**Goals:**
- Single `prepare()` function for all framework initialization
- Async-native design that integrates with modern Python application patterns
- Proper resource lifecycle management through `AsyncExitStack`
- Deterministic initialization order with concurrent external resource setup

**Non-Goals:**
- Synchronous initialization API (would double API surface)
- Lazy initialization (framework state must be complete after `prepare()`)
- Plugin-based initialization (keep initialization sequence explicit)

## Decisions

### Async-First Design Pattern

**Decision:** Adopt async-first design for all initialization and resource
management patterns. The primary `prepare()` function and all derived
initialization methods use async patterns with `AsyncExitStack` integration.

**Alternatives considered:**
- Synchronous initialization with async adaptation layer — Rejected: complex
  adaptation patterns, prevents clean integration with async application code
- Dual sync/async APIs — Rejected: doubles API surface, creates maintenance
  overhead and inconsistent patterns
- Mixed approach with sync core and async extensions — Rejected: unclear
  boundaries and inconsistent usage patterns

### Deterministic Initialization Order

**Decision:** `prepare()` executes initialization in a fixed sequence:
distribution → directories → configuration → inscription → state assembly.
This ensures each step can depend on outputs from previous steps.

**Rationale:** Configuration may reference platform directories. Inscription
may reference configuration settings. State assembly needs all components.

## Risks / Trade-offs

- **Risk:** Requires `asyncio.run()` wrapper for simple synchronous applications
  → Mitigation: Document common patterns; `prepare()` is the only async entry point
- **Risk:** Learning curve for developers unfamiliar with async patterns
  → Mitigation: Clear documentation and examples in README

## Implementation Notes

The `prepare()` function signature:

```python
async def prepare(
    exits: AsyncExitStack,
    acquirer: AcquirerAbc = TomlAcquirer(),
    application: Absential[Information] = absent,
    configedits: Edits = (),
    inscription: Absential[InscriptionControl] = absent,
) -> Globals:
```

Each initialization step is isolated in its own module. `prepare()` acts as
the orchestrator, passing intermediate results between steps.
