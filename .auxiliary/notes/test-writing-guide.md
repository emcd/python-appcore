# Test Writing Guide for Immutable Architectures

## Core Principle: Dependency Injection Over Monkey-Patching

This codebase uses immutable objects (`frigid`/`classcore`) that **prevent monkey-patching by design**. Use **dependency injection** patterns instead.

## Quick Reference

### ❌ Anti-Patterns
```python
# WRONG - will fail with AttributeImmutability
with patch.object(TomlAcquirer, '_some_method'): pass
with patch('appcore.configuration._some_function'): pass
```

### ✅ Preferred Patterns
```python
# 1. Real temporary directories for file operations
directories, distribution, temp_dir = create_temp_directories_and_distribution()

# 2. Dependency injection via parameters
async def process_data(data: str, processor: Callable = default_processor): pass

# 3. Constructor injection for objects
@dataclass(frozen=True)
class DataProcessor:
    validator: Callable[[str], bool] = default_validator

# 4. Third-party module patching only
with patch('importlib_metadata.packages_distributions'): pass  # ✅ OK
with patch('appcore.io.acquire_text_file_async'): pass        # ❌ Forbidden
```

## Testing Strategy by Code Type

| **Code Type** | **Strategy** | **Key Points** |
|---------------|-------------|----------------|
| **File Operations** | Real temp directories | Use `create_temp_directories_and_distribution()`, clean up with `shutil.rmtree()` |
| **Business Logic** | Dependency injection | Inject dependencies via constructor or method parameters |
| **Sync Filesystem** | `pyfakefs` with `Patcher()` | Fast, but doesn't work with `aiofiles` |
| **Async Operations** | Real temp directories | `aiofiles` bypasses `pyfakefs` thread pool |
| **Third-Party Boundaries** | Strategic patching | Only patch `importlib_metadata`, `inspect`, stdlib |
| **Abstract Methods** | `# pragma: no cover` | Apply to `NotImplementedError` lines only |

## Test Standards

### Development Environment
- **Always use `hatch --env develop run`** for all testing commands
- **Examples**:
  - `hatch --env develop run pytest` - run tests
  - `hatch --env develop run coverage report` - coverage report
  - `hatch --env develop run linters` - run linters
  - `hatch --env develop run testers` - run full test suite

### Docstring Guidelines
- **Describe behavior**, not function names
- **Keep headlines single-line** (don't spill across lines)
- **Good**: `''' Error interceptor returns Value for successful awaitable. '''`
- **Bad**: `''' intercept_error_async returns Value for successful awaitable. '''`

### Code Style
- **No blank lines** in function bodies
- **Mark slow tests** with `@pytest.mark.slow`
- **Narrow try blocks** around exception-raising statements only
- **Use parentheses** for line continuations (not backslashes)

### Fixtures Available
```python
# Basic setup
directories, distribution, temp_dir = create_temp_directories_and_distribution(
    editable=False, app_name='test-app', dist_name='test-dist')

# Full globals DTO
globals_dto, temp_dir = create_globals_with_temp_dirs(
    editable=True, config_locations=['custom/path'])

# Configuration files
create_config_template_files(distribution, content='[app]\nname="test"')
```

## Advanced Patterns

### Hybrid Approaches (Sync + Async)
```python
# Fast sync operations - use pyfakefs
def test_sync_operations():
    with Patcher() as patcher:
        fs = patcher.fs
        fs.create_file('/fake/pyproject.toml', contents='[project]\nname="test"')
        result = sync_function(Path('/fake'))
        assert result.exists()

# Async operations - use real temp directories
@pytest.mark.asyncio
async def test_async_operations():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / 'pyproject.toml').write_text('[project]\nname="test"')
        result = await async_function(temp_path)
        assert result.name == 'test'
```

### Frame Inspection Testing
```python
def test_caller_discovery():
    # Mock frame chain simulating call stack
    external_frame = MagicMock()
    external_frame.f_code.co_filename = '/external/caller.py'
    external_frame.f_back = None
    
    internal_frame = MagicMock()
    internal_frame.f_code.co_filename = '/appcore/distribution.py'
    internal_frame.f_back = external_frame
    
    with patch('inspect.currentframe', return_value=internal_frame):
        result = module._discover_invoker_location()
        assert result == Path('/external')
```

### Coverage-Driven Development
```python
# Target specific uncovered lines systematically
@pytest.mark.asyncio
async def test_development_mode_missing_package():
    ''' Information.prepare triggers development mode for missing package. '''
    with patch('importlib_metadata.packages_distributions', return_value={}):
        info = await module.Information.prepare('nonexistent-package', exits)
        assert info.editable is True  # Development mode verified
```

### Resource Management
```python
# Use ExitStack for multiple temporary files
from contextlib import ExitStack

def test_multiple_temp_files():
    with ExitStack() as stack:
        temp1 = stack.enter_context(tempfile.NamedTemporaryFile(mode='w', delete=False))
        temp2 = stack.enter_context(tempfile.NamedTemporaryFile(mode='w', delete=False))
        # Both files cleaned up automatically
```

## Configuration and Error Testing

### Configuration Variants
```python
def create_config_variants():
    return {
        'minimal': '[application]\nname = "minimal-app"',
        'debug': '[application]\nname = "debug-app"\ndebug = true',
        'production': '[application]\nname = "prod-app"\ndebug = false'
    }

@pytest.mark.asyncio
async def test_config_variant(variant_name, config_content):
    config_stream = io.StringIO(config_content)
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(exits, configfile=config_stream)
        return globals_dto.configuration
```

### Error Simulation
```python
def safe_config_edit(config):
    try:
        config['application']['safe_mode'] = True
    except Exception:
        config['fallback'] = True  # Apply fallback

@pytest.mark.asyncio
async def test_error_recovery():
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(
            exits, configedits=(safe_config_edit,))
        assert globals_dto.configuration.get('application', {}).get('safe_mode')
```

## Performance Optimization

### Strategies
- **Eliminate subprocess calls** → Mock frame inspection
- **Use pyfakefs for 80%+ filesystem tests** → 60% performance improvement
- **Focus patches at third-party boundaries** → Maintain architecture integrity
- **Accept some real I/O for complex async operations** → Hybrid approach

### Benchmarking
```python
@pytest.mark.asyncio
async def benchmark_initialization(config_size='small'):
    start_time = time.time()
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(exits, configfile=config_stream)
        duration = time.time() - start_time
        return duration, len(globals_dto.configuration)
```

## Troubleshooting

### Common Issues
1. **`AttributeImmutability` errors** → Use dependency injection instead of patching
2. **`aiofiles` not working with `pyfakefs`** → Fall back to real temp directories
3. **Test parameter conflicts** → Use `Patcher()` context manager, not `@patchfs`
4. **Line number shifts in bulk editing** → Work from back to front
5. **Undefined variables after blank line removal** → Check for missing variable declarations

### When to Use `# pragma: no cover`
- **Abstract methods** with `NotImplementedError`
- **Defensive code** that's impossible to trigger
- **Platform-specific branches** that can't be tested in current environment
- **Last resort only** - prefer dependency injection

## Benefits

1. **Realistic testing** - real file operations catch more bugs
2. **Flexible code** - dependency injection improves design
3. **Maintainable tests** - less fragile than monkey-patching
4. **Preserved architecture** - immutability provides thread safety
5. **Optimized performance** - strategic use of fake filesystem and mocking
6. **Comprehensive coverage** - systematic targeting of uncovered branches

## When to Discuss

If you can't test something without monkey-patching:
1. **Try dependency injection** patterns above
2. **Check if interface supports injection** extension
3. **Consider hybrid approaches** (fake filesystem + real temp dirs)
4. **Discuss design** with team
5. **Last resort** - apply `# pragma: no cover` with justification

The goal is testable code through good design, not circumventing the architecture.