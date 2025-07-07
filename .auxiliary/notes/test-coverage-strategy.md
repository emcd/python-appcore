# Test Coverage Strategy & Plan

## Current Coverage Status (39% overall)

### Coverage by Module (sorted by priority)
| Module | Coverage | Missing Lines | Priority | Reason |
|--------|----------|---------------|----------|---------|
| generics.py | 76% | 4/30 lines | **Start Here** | Foundation utilities |
| exceptions.py | 72% | 5/18 lines | **Start Here** | Error handling base |
| state.py | 53% | 12/30 lines | **Early** | Core data structures |
| io.py | 31% | 7/11 lines | **Early** | File I/O utilities |
| dictedits.py | 30% | 23/39 lines | **Medium** | Configuration editing |
| configuration.py | 30% | 22/36 lines | **Medium** | Config loading |
| preparation.py | 26% | 21/32 lines | **Late** | Main orchestration |
| inscription.py | 24% | 21/31 lines | **Medium** | Logging setup |
| distribution.py | 20% | 35/48 lines | **Medium** | Dev/prod detection |
| environment.py | 18% | 19/25 lines | **Medium** | Environment loading |
| asyncf.py | 11% | 34/41 lines | **Early** | Async utilities |

## Testing Strategy: Bottom-Up Approach

### Phase 1: Foundation (Files 100-139)
Start with fundamental utilities that other modules depend on:

#### test_100_exceptions.py
- Test all exception classes and inheritance
- Test error message formatting
- Verify exception hierarchy works correctly

#### test_110_generics.py
- Test generic utilities and type helpers
- Currently 76% coverage - identify missing edge cases
- Focus on error conditions and boundary cases

#### test_120_asyncf.py
- Test async utility functions (currently 11% coverage)
- Focus on async context managers, coroutine helpers
- Use dependency injection for async resource management

#### test_130_dictedits.py
- Test configuration editing functions
- Use examples from Advanced.ConfigTesting doctest
- Test edit function composition and error handling

### Phase 2: Core Functionality (Files 200-299)

#### test_200_application.py
- Test ApplicationInformation class
- Test application metadata and configuration
- Test name validation and defaults

#### test_210_distribution.py
- Test development vs production detection
- Test project root discovery with various scenarios
- Mock `importlib_metadata` and filesystem operations
- Test `GIT_CEILING_DIRECTORIES` respect

### Phase 3: Advanced Components (Files 300-499)

#### test_300_configuration.py
- Test configuration loading and template handling
- Test hierarchical includes and variable substitution
- Use stream-based testing to avoid filesystem dependencies
- Test TomlAcquirer and custom acquirers

#### test_400_state.py
- Test `Globals` DTO and state management
- Test convenience methods like `provide_cache_location()`
- Verify immutability and data integrity

### Phase 4: Integration (Files 500+)

#### test_500_preparation.py
- Test main `prepare()` function with full dependency injection
- Use patterns from Advanced.Fixtures and Advanced.Testing doctests
- Test all parameter combinations and error scenarios
- Integration testing with real components

## Testing Principles

### 1. Dependency Injection Patterns
```python
# Use custom components for complete control
app_info = appcore.ApplicationInformation(name='test-app')
test_dirs = platformdirs.PlatformDirs('test-app', ensure_exists=False)  
test_dist = appcore.DistributionInformation(...)
config_stream = io.StringIO("...")

async with contextlib.AsyncExitStack() as exits:
    globals_dto = await appcore.prepare(
        exits,
        application=app_info,
        directories=test_dirs, 
        distribution=test_dist,
        configfile=config_stream,
        environment={'TEST': 'true'}
    )
```

### 2. Stream-Based Configuration
```python
# Avoid filesystem dependencies
config_content = '''
[application]
name = "test-app"
debug = true
'''
config_stream = io.StringIO(config_content)
# Pass to prepare() or configuration.acquire()
```

### 3. Mock External Dependencies
```python
# Mock importlib_metadata for distribution testing
# Mock filesystem operations for template copying
# Mock environment variables for isolation
```

### 4. Async Context Management
```python
# Proper AsyncExitStack usage in all tests
async with contextlib.AsyncExitStack() as exits:
    # Test async initialization
    pass
```

### 5. Error Scenario Testing
```python
# Test all exception paths
# Use invalid inputs to trigger error conditions
# Verify proper exception types and messages
```

## Expected Outcomes

### Coverage Targets
- **Phase 1**: Bring foundation modules to 90%+ coverage
- **Phase 2**: Bring core modules to 85%+ coverage  
- **Phase 3**: Bring integration to 80%+ coverage
- **Overall**: Target 85%+ total coverage

### Test Quality Metrics
- All public API methods tested
- All error conditions covered
- All configuration scenarios tested
- All dependency injection paths verified

## Files to Create
```
tests/
├── test_100_exceptions.py
├── test_110_generics.py
├── test_120_asyncf.py
├── test_130_dictedits.py
├── test_200_application.py
├── test_210_distribution.py
├── test_300_configuration.py
├── test_400_state.py
└── test_500_preparation.py
```

## Implementation Notes
- Use existing doctest patterns from documentation examples
- Leverage `tests/test_000_appcore/__init__.py` utilities
- Follow existing test file naming conventions
- Use pytest fixtures for common test setup
- Add async test markers where needed (`@pytest.mark.asyncio`)

## Testing Conventions

### Module Import Pattern
```python
# Use cache_import_module for consistent module loading
from tests.test_000_appcore import PACKAGE_NAME, cache_import_module

MODULE_QNAME = f"{PACKAGE_NAME}.exceptions"
module = cache_import_module( MODULE_QNAME )
```

### Test Function Docstrings
```python
# Write docstrings as assertions, not descriptions
def test_100_template_copy_custom_name( ):
    ''' Copies configuration template with non-default name. '''
    # Test implementation
    
def test_200_exception_hierarchy( ):
    ''' All custom exceptions inherit from base exception. '''
    # Test implementation
```

### Coding Conventions
- Follow project style: spaces inside delimiters `( foo )`, not `(foo)`
- Use single quotes for strings, double quotes for f-strings
- Pad binary operators with spaces: `foo = 42`, not `foo=42`
- Use triple single quotes for docstrings: `''' description '''`