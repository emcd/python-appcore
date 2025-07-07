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

### Phase 1: Foundation (Files 100-109)
Start with fundamental utilities that other modules depend on:

#### test_100_generics.py
- Test generic utilities and type helpers
- Currently 76% coverage - identify missing edge cases
- Focus on error conditions and boundary cases

#### test_101_exceptions.py  
- Test all exception classes and inheritance
- Test error message formatting
- Verify exception hierarchy works correctly

#### test_102_asyncf.py
- Test async utility functions (currently 11% coverage)
- Focus on async context managers, coroutine helpers
- Use dependency injection for async resource management

#### test_103_io.py
- Test file I/O utilities
- Mock filesystem operations
- Test both sync and async file operations

#### test_104_state.py
- Test `Globals` DTO and state management
- Test convenience methods like `provide_cache_location()`
- Verify immutability and data integrity

### Phase 2: Core Functionality (Files 110-119)

#### test_110_dictedits.py
- Test configuration editing functions
- Use examples from Advanced.ConfigTesting doctest
- Test edit function composition and error handling

#### test_111_configuration.py
- Test configuration loading and template handling
- Test hierarchical includes and variable substitution
- Use stream-based testing to avoid filesystem dependencies
- Test the future `Acquirer` class

#### test_112_distribution.py
- Test development vs production detection
- Test project root discovery with various scenarios
- Mock `importlib_metadata` and filesystem operations
- Test `GIT_CEILING_DIRECTORIES` respect

#### test_113_environment.py
- Test environment variable injection and .env loading
- Test precedence rules for environment sources
- Use custom environment dictionaries for isolation

#### test_114_inscription.py
- Test logging configuration and setup
- Test log level management and scribe preparation
- Mock logging infrastructure

### Phase 3: Integration (Files 120-129)

#### test_120_preparation.py
- Test main `prepare()` function with full dependency injection
- Use patterns from Advanced.Fixtures and Advanced.Testing doctests
- Test all parameter combinations and error scenarios
- Integration testing with real components

#### test_121_integration_scenarios.py
- Test complete application initialization scenarios
- Test error recovery and fallback mechanisms
- Use patterns from Advanced.ErrorTesting doctest

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
├── test_100_generics.py
├── test_101_exceptions.py
├── test_102_asyncf.py
├── test_103_io.py
├── test_104_state.py
├── test_110_dictedits.py
├── test_111_configuration.py
├── test_112_distribution.py
├── test_113_environment.py
├── test_114_inscription.py
├── test_120_preparation.py
└── test_121_integration_scenarios.py
```

## Implementation Notes
- Use existing doctest patterns from documentation examples
- Leverage `tests/test_000_appcore/__init__.py` utilities
- Follow existing test file naming conventions
- Use pytest fixtures for common test setup
- Add async test markers where needed (`@pytest.mark.asyncio`)