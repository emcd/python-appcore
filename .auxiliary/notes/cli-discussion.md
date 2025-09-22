# CLI Architecture Discussion: Contravariance and Inheritance

## Problem Statement

We encountered a fundamental type theory issue when designing the CLI command interface. The challenge was enabling commands to accept subclasses of `__.Globals` (for specialized data) while maintaining protocol compliance and type safety.

### The Core Dilemma

**What we wanted:** Commands that accept specialized `Globals` subclasses
```python
class MyAppGlobals(__.Globals):
    special_data: SomeType

class MyAppCommand(CliCommand):
    async def execute(self, auxdata: MyAppGlobals) -> None:  # More specific type
        auxdata.special_data.do_something()
```

**The problem:** Protocol parameters are contravariant - a protocol expecting `__.Globals` should accept any `__.Globals` or broader, not narrower subclasses. This violates the Liskov Substitution Principle.

**Why LSP matters:** If you have a list of commands and call each with `__.Globals`, commands requiring `MyAppGlobals` would fail at runtime.

## Solutions Explored

### 1. Generic Protocol with TypeVar
```python
_GlobalsT = TypeVar('_GlobalsT', bound=__.Globals)
class CliCommand(Protocol[_GlobalsT]):
    async def execute(self, auxdata: _GlobalsT) -> None: ...
```
**Rejected:** Pyright error: "Type variable should be covariant in generic Protocol"

### 2. Use `Any` for display parameter
```python
async def execute(self, auxdata: __.Globals, display: __.typx.Any) -> None: ...
```
**Rejected:** Loses type safety, considered "sloppy"

### 3. Context Accumulator Pattern
```python
class CommandContext:
    def extend(self, **kwargs) -> 'CommandContext': ...
    def get(self, attr: str) -> Any: ...
```
**Rejected:** Unnatural API requiring `get()` calls instead of normal attribute access

### 4. Dependency Injection Pattern
```python
class DIContainer:
    def require(self, type_: Type[T]) -> T: ...
```
**Rejected:** Heavy-weight, unnatural, contrived feeling

### 5. Monadic Pipeline
```python
async def transform(self, state: Dict[str, Any]) -> Dict[str, Any]: ...
```
**Rejected:** Loses type information with generic dictionaries

### 6. Metaclass-based Interface Generation
**Rejected:** Half-formed idea, would likely break static analysis

### 7. Runtime Type Checking with isinstance
```python
class MyAppCommand(CliCommand):
    async def execute(self, auxdata: __.Globals) -> None:
        if not isinstance(auxdata, MyAppGlobals):
            raise TypeError(f"Expected MyAppGlobals, got {type(auxdata)}")
        # Type checker knows auxdata is MyAppGlobals from here
        auxdata.special_data.do_something()
```
**Selected:** Natural Python pattern, type guards work with static analysis, fails fast with clear errors

## Final Architecture Decision

### Core Pattern: isinstance Type Guards
- Commands declare broad parameter types (`__.Globals`)
- Commands use `isinstance()` checks to narrow types at runtime
- Type checkers understand `isinstance()` as type guards
- Both statically and dynamically safe

### Snowball Pattern: Accumulating Context
Instead of separate `display` parameters, roll everything into enriched `Globals` subclasses:

```python
class ExampleGlobals(__.Globals):
    display: ExampleDisplayOptions

class ExampleCommand(CliCommand):
    async def execute(self, auxdata: __.Globals) -> None:
        if not isinstance(auxdata, ExampleGlobals):
            raise TypeError("Example commands require ExampleGlobals")
        await auxdata.display.render(data)
```

### Template Method Pattern
Commands use prepare/execute split with omissible auxdata for composition:

```python
class CliCommand(Protocol):
    async def __call__(self, auxdata: __.Absential[__.Globals] = __.absent) -> None:
        if __.is_absent(auxdata):
            async with __.ctxl.AsyncExitStack() as exits:
                base_auxdata = await self.prepare_base_globals(exits)
                await self.execute(base_auxdata)
        else:
            enriched_auxdata = await self.enrich_globals(auxdata)
            await self.execute(enriched_auxdata)

    async def execute(self, auxdata: __.Globals) -> None: ...
```

## Alternative Patterns Considered

### Context Manager Approach (Rejected)
Explored `__aenter__`/`__aexit__` for session management:
```python
async with command as auxdata:
    await command.execute(auxdata)
```
**Rejected:** `async with self as auxdata` is confusing - makes it seem like the command is the globals DTO

## Key Insights

1. **Type theory exists for good reasons** - Contravariance protects against real runtime failures
2. **isinstance is not dirty** - It's a natural Python pattern that works with type checkers
3. **The "snowball" metaphor works** - Data accumulates as it flows down the command hierarchy
4. **Simple is better** - Natural Python patterns beat clever abstractions
5. **Framework magic should feel natural** - Users shouldn't feel they're learning a special mechanism

## Impact on Existing Projects

This pattern requires refactoring existing projects like `aiwb` and `librovore` that use inheritance-based command hierarchies, but provides much better type safety and clearer error messages.