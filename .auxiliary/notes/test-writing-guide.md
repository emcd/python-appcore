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

## Advanced Testing Patterns

### 5. Hybrid Approaches for Complex Operations
When working with modules that have both sync and async operations, use a hybrid approach:

```python
from pyfakefs.fake_filesystem_unittest import Patcher

def test_sync_filesystem_operations():
    ''' Fast sync operations using fake filesystem. '''
    with Patcher() as patcher:
        fs = patcher.fs
        # Create fake filesystem structure
        project_root = Path('/fake/project')
        fs.create_dir(project_root)
        fs.create_file(project_root / 'pyproject.toml', contents='...')
        
        # Test sync operations against fake filesystem
        result = sync_function(project_root)
        assert result.exists()

@pytest.mark.asyncio
async def test_async_file_operations():
    ''' Async operations using real temporary directories. '''
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pyproject_path = temp_path / 'pyproject.toml'
        pyproject_path.write_text('[project]\nname = "test"\n')
        
        # Test async operations against real filesystem
        result = await async_function(temp_path)
        assert result.name == 'test'
```

### 6. pyfakefs Integration Patterns
Use `Patcher()` context manager instead of `@patchfs` decorator for pytest compatibility:

```python
# ❌ Problematic - parameter conflicts with pytest
@patchfs
def test_something(fs):  # 'fs' parameter conflicts

# ✅ Working approach
def test_something():
    with Patcher() as patcher:
        fs = patcher.fs
        # Use fs.create_file(), fs.create_dir(), etc.
```

**Key aiofiles Limitation**: `aiofiles` doesn't work with `pyfakefs` due to thread pool execution bypassing the patching mechanism. For async file operations, fall back to real temporary directories.

### 7. Frame Inspection Testing
When testing caller discovery functions, mock frame chains properly:

```python
def test_caller_discovery():
    ''' Frame inspection finds external caller location. '''
    # Create mock frame chain simulating call stack
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

### 8. Third-Party Module Patching Only
**Critical Rule**: Only patch third-party modules and Python stdlib, never internal modules:

```python
# ✅ Allowed - third-party module
with patch('importlib_metadata.packages_distributions'):
    # Test code

# ✅ Allowed - Python stdlib
with patch('inspect.currentframe'):
    # Test code

# ❌ Forbidden - internal module (frigid prevents this anyway)
with patch('appcore.io.acquire_text_file_async'):
    # This violates testing guidelines
```

### 9. Performance Optimization Strategies
Monitor test performance and optimize systematically:

- **Subprocess elimination**: Replace subprocess calls with mocked frame inspection
- **Fake filesystem usage**: Use `pyfakefs` for 80%+ of filesystem tests
- **Boundary testing**: Focus patches at third-party boundaries
- **Hybrid approaches**: Accept some real I/O for complex async operations

Example performance impact:
- Before: 2.5s (subprocess heavy)
- After: 1.0s (60% improvement with hybrid approach)

### 10. Coverage-Driven Test Development
Target specific uncovered lines systematically:

```python
# Target development mode path (lines 52-55 in distribution.py)
@pytest.mark.asyncio
async def test_development_mode_missing_package():
    ''' Information.prepare triggers development mode for missing package. '''
    # Mock packages_distributions to return empty (no installed package)
    with patch('importlib_metadata.packages_distributions', return_value={}):
        # This triggers development mode because package not found
        info = await module.Information.prepare('nonexistent-package', exits)
        assert info.editable is True  # Development mode verified
```

## High-Level Testing Strategies

### 11. Mock Globals Creation
Create complete test doubles for the global application state:

```python
import appcore
import platformdirs
from pathlib import Path

class MockGlobals:
    ''' Mock globals object for unit testing. '''
    def __init__(self, app_name='test-app'):
        self.application = appcore.ApplicationInformation(name=app_name)
        self.configuration = {'test': True}
        self.directories = platformdirs.PlatformDirs(app_name, ensure_exists=False)
        self.distribution = appcore.DistributionInformation(
            name=app_name,
            location=Path('/tmp/test'),
            editable=True
        )
    
    def provide_data_location(self, *appendages):
        base = Path(f"/tmp/test-data/{self.application.name}")
        if appendages:
            return base.joinpath(*appendages)
        return base

# Usage in tests
mock_globals = MockGlobals('unit-test')
assert mock_globals.application.name == 'unit-test'
```

### 12. Configuration Variant Testing
Test different configuration scenarios systematically:

```python
def create_config_variants():
    ''' Generate different configuration scenarios for testing. '''
    return {
        'minimal': '''
        [application]
        name = "minimal-app"
        ''',
        'debug_enabled': '''
        [application]
        name = "debug-app"
        debug = true
        timeout = 30
        
        [logging]
        level = "debug"
        ''',
        'production': '''
        [application]
        name = "prod-app"
        debug = false
        timeout = 300
        
        [logging]
        level = "info"
        
        [security]
        strict_mode = true
        '''
    }

@pytest.mark.asyncio
async def test_config_variant(variant_name, config_content):
    ''' Test a specific configuration variant. '''
    config_stream = io.StringIO(config_content)
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(
            exits,
            configfile=config_stream,
            directories=platformdirs.PlatformDirs('test', ensure_exists=False)
        )
        config = globals_dto.configuration
        app_name = config['application']['name']
        return config
```

### 13. Error Simulation and Recovery Testing
Test error conditions and recovery strategies:

```python
class ConfigurationError(Exception):
    ''' Custom configuration error for testing. '''
    pass

def failing_config_edit(config):
    ''' Configuration edit that fails for testing. '''
    raise ConfigurationError('Simulated configuration failure')

def safe_config_edit(config):
    ''' Configuration edit with error handling. '''
    try:
        if 'application' not in config:
            config['application'] = {}
        config['application']['safe_mode'] = True
    except Exception as e:
        # Apply fallback configuration
        config['fallback'] = True

@pytest.mark.asyncio
async def test_error_recovery():
    ''' Test configuration error recovery. '''
    config_content = '''
    [application]
    name = "error-test"
    '''
    config_stream = io.StringIO(config_content)
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(
            exits,
            configfile=config_stream,
            configedits=(safe_config_edit,),
            directories=platformdirs.PlatformDirs('test', ensure_exists=False)
        )
        config = globals_dto.configuration
        has_safe_mode = config.get('application', {}).get('safe_mode', False)
        assert has_safe_mode
```

### 14. Performance Benchmarking
Measure initialization performance with different configurations:

```python
import time

@pytest.mark.asyncio
async def benchmark_initialization(config_size='small'):
    ''' Benchmark appcore initialization performance. '''
    if config_size == 'small':
        config_content = '''
        [application]
        name = "benchmark"
        '''
    elif config_size == 'large':
        # Generate larger configuration
        sections = []
        for i in range(10):
            sections.append(f'''
            [section_{i}]
            value_{i} = {i}
            setting_{i} = "config_{i}"
            ''')
        config_content = '''
        [application]
        name = "benchmark"
        ''' + '\n'.join(sections)
    
    start_time = time.time()
    config_stream = io.StringIO(config_content)
    async with contextlib.AsyncExitStack() as exits:
        globals_dto = await appcore.prepare(
            exits,
            configfile=config_stream,
            directories=platformdirs.PlatformDirs('benchmark', ensure_exists=False)
        )
        end_time = time.time()
        duration = end_time - start_time
        config_keys = len(globals_dto.configuration)
        return duration, config_keys
```

### 15. Resource Management with AsyncExitStack
Advanced patterns for managing resources with automatic cleanup:

```python
import tempfile
import contextlib

@pytest.mark.asyncio
async def test_with_temporary_resources():
    ''' Test using temporary resources that are cleaned up automatically. '''
    async with contextlib.AsyncExitStack() as exits:
        # Create temporary directory for test
        temp_dir = exits.enter_context(tempfile.TemporaryDirectory())
        
        # Use custom directories pointing to temp location
        test_dirs = platformdirs.PlatformDirs('temp-test', ensure_exists=False)
        
        # Initialize appcore with temporary resources
        globals_dto = await appcore.prepare(
            exits,
            directories=test_dirs,
            configfile=io.StringIO('''
            [application]
            name = "temp-test"
            [testing]
            temporary = true
            ''')
        )
        
        # Use the globals object
        config = globals_dto.configuration
        is_temporary = config['testing']['temporary']
        assert is_temporary == True
        return globals_dto
    # temp_dir is automatically cleaned up when exiting the context
```

## Benefits of This Approach

1. **Tests are more realistic** - using real file operations catches more bugs
2. **Code is more flexible** - dependency injection improves design
3. **Tests are more maintainable** - less fragile than monkey-patching
4. **Architecture is preserved** - immutability provides thread safety and predictability
5. **Performance is optimized** - strategic use of fake filesystem and mocking
6. **Coverage is comprehensive** - systematic targeting of uncovered branches

## When to Discuss

If you can't see how to test something without monkey-patching:
1. **First** - try dependency injection patterns above
2. **Second** - check if the interface can be extended to support injection
3. **Third** - consider hybrid approaches (fake filesystem + real temp dirs)
4. **Fourth** - discuss with the team whether the design needs adjustment
5. **Last resort** - apply `# pragma: no cover` with detailed justification

The goal is to make code testable through good design, not by circumventing the architecture.
