# Test Writing Guide for Immutable Architectures

## Core Principle: Dependency Injection Over Monkey-Patching

This codebase uses an immutable object architecture (`frigid`/`classcore`) that **prevents monkey-patching by design**. Instead of patching, we use **dependency injection** patterns for testing.

## ❌ Anti-Patterns (Don't Do This)

### 1. Instance Patching
```python
# WRONG - will fail with AttributeImmutability
acquirer = TomlAcquirer()
with patch.object(acquirer, '_some_method'):
    # ...
```

### 2. Class Patching
```python
# WRONG - will fail with AttributeImmutability
with patch.object(TomlAcquirer, '_some_method'):
    # ...
```

### 3. Module-Level Patching
```python
# WRONG - too invasive, breaks encapsulation
with patch('appcore.configuration._some_function'):
    # ...
```

## ✅ Preferred Patterns (Do This)

### 1. Real Temporary Directories
When testing file operations, create real temp directories:

```python
from .fixtures import create_temp_directories_and_distribution, create_config_template_files

def test_file_operations():
    directories, distribution, temp_dir = create_temp_directories_and_distribution()

    # Create real files for testing
    create_config_template_files(distribution, content='[app]\nname="test"')

    try:
        # Test with real file operations
        result = await some_function(directories, distribution)
        assert result.is_valid()
    finally:
        shutil.rmtree(temp_dir)
```

### 2. Dependency Injection via Parameters
If a function needs configurable behavior, inject it via parameters:

```python
# GOOD - allows testing different behaviors
async def process_data(
    data: str,
    processor: Callable[[str], str] = default_processor
) -> str:
    return processor(data)

# Test with injected behavior
def test_process_data():
    def test_processor(data): return f"processed: {data}"
    result = await process_data("input", processor=test_processor)
    assert result == "processed: input"
```

### 3. Constructor Injection for Objects
Configure behavior at object creation time:

```python
@dataclass(frozen=True)
class DataProcessor:
    validator: Callable[[str], bool] = default_validator

    def process(self, data: str) -> str:
        if self.validator(data):
            return f"valid: {data}"
        return "invalid"

# Test with injected validator
def test_data_processor():
    def always_valid(data): return True
    processor = DataProcessor(validator=always_valid)
    result = processor.process("test")
    assert result == "valid: test"
```

### 4. Standard Test Fixtures
Use centralized fixtures for common setup patterns:

```python
# Available fixtures in tests/test_000_appcore/fixtures.py:

# 1. Basic temp directories + distribution
directories, distribution, temp_dir = create_temp_directories_and_distribution(
    editable=False,  # or True for editable installs
    app_name='test-app',
    dist_name='test-dist'
)

# 2. Full globals DTO for environment testing
globals_dto, temp_dir = create_globals_with_temp_dirs(
    editable=True,
    config_locations=['custom/path']
)

# 3. Configuration template files
create_config_template_files(
    distribution,
    main_filename='general.toml',
    content='[app]\nname="test-app"'
)
```

## Testing Strategy by Code Type

### File Operations
- **Use real temporary directories**
- Create actual files and directories
- Test actual file system interactions
- Clean up with `shutil.rmtree()` in `finally` blocks

### Business Logic
- **Inject dependencies** via constructor or method parameters
- Pass test doubles for external dependencies
- Focus on pure functions when possible

### Abstract Methods
- **Apply `# pragma: no cover`** to `NotImplementedError` lines
- Abstract methods are meant to be overridden, not tested directly

### Edge Cases in Immutable Objects
- **Design for testability** by adding optional parameters
- **Prefer real scenarios** over complex mocking
- **Use pragmas sparingly** only when dependency injection isn't feasible

## Docstring Guidelines

### Write Behavior-Focused Docstrings
- **Describe what behavior is being tested**, not function names
- **Good**: `''' Error interceptor returns Value for successful awaitable. '''`
- **Bad**: `''' intercept_error_async returns Value for successful awaitable. '''`

### Keep Headlines Concise
- **Single-line headlines only** - don't let headlines spill across multiple lines
- **Good**: `''' Configuration acquirer handles absent file parameter. '''`
- **Bad**: `''' Configuration acquirer handles absent file parameter by discovering template. '''`

### Add Context When Needed
- Use a blank line to separate headline from additional context
- Indent context to same level as headline
```python
def test_complex_behavior():
    ''' Error interceptor handles complex scenarios.

        Tests behavior when multiple error conditions overlap
        and recovery mechanisms are triggered.
    '''
```

### Benefits of Good Docstrings
- **Function renaming doesn't require docstring updates**
- **Shorter, more readable test descriptions**
- **Focus on the "why" rather than the "what"**

### Mark Slow Tests
- **Use `@pytest.mark.slow`** for tests with deliberate delays or sleeps
- **Allows filtering** with `pytest -m "not slow"` for faster test runs
```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_many_concurrent_operations():
    ''' Async gatherer handles many concurrent operations. '''
    async def operation(n):
        await asyncio.sleep(0.001)  # Simulate delay
        return n * 2
```

## Benefits of This Approach

1. **Tests are more realistic** - using real file operations catches more bugs
2. **Code is more flexible** - dependency injection improves design
3. **Tests are more maintainable** - less fragile than monkey-patching
4. **Architecture is preserved** - immutability provides thread safety and predictability

## When to Discuss

If you can't see how to test something without monkey-patching:
1. **First** - try dependency injection patterns above
2. **Second** - check if the interface can be extended to support injection
3. **Third** - discuss with the team whether the design needs adjustment
4. **Last resort** - apply `# pragma: no cover` with detailed justification

The goal is to make code testable through good design, not by circumventing the architecture.
