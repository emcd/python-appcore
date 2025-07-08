# Distribution Module Test Refactoring Status

## Objective
Improve test coverage for `sources/appcore/distribution.py` from 90% to 100% while dramatically improving test performance. The current tests are slow because they use subprocess calls and real filesystem operations.

## Current Coverage Gaps
The missing coverage is concentrated in these areas:
- **Lines 52-55**: Development mode path in `Information.prepare()` when `packages_distributions().get(package)` returns `None`
- **Lines 121-124**: GIT_CEILING_DIRECTORIES parsing logic
- **Lines 129-130, 132-133**: FileLocateFailure exceptions when hitting ceiling directories or filesystem root

## Performance Problem
The current distribution tests are significantly slower than the rest of the test suite combined because they:
1. Create real temporary directories and files using `tempfile.mkdtemp()`
2. Execute subprocess calls to simulate external callers for frame inspection testing
3. Walk the real filesystem for pyproject.toml discovery

## Approaches Attempted

### 1. Initial Plan: Full pyfakefs Migration
**Goal**: Replace all filesystem operations with `pyfakefs` for speed and testability.

**Implementation**: 
- Replaced `tempfile.mkdtemp()` calls with `pyfakefs` fake filesystem
- Used `@patchfs` decorator for sync functions
- Replaced subprocess calls with mocked frame inspection

**Success**: Sync functions work perfectly with `pyfakefs`

### 2. Challenge: Async Functions + aiofiles
**Problem**: The `_acquire_development_information()` function uses `_io.acquire_text_file_async()` which internally uses `aiofiles`. The `aiofiles` library doesn't work with `pyfakefs` out of the box.

**Attempted Solutions**:
1. **Tried**: `Patcher(modules_to_patch={'aiofiles': None})` - Failed due to `aiofiles` not being a supported patch target
2. **Tried**: Patching internal `appcore.io.acquire_text_file_async` - Failed due to `frigid` package making our modules immutable
3. **Current**: Falling back to real temporary directories for async tests

### 3. Current State: Hybrid Approach
**What Works**:
- All sync filesystem tests use `pyfakefs` successfully (fast, reliable)
- Frame inspection mocked properly instead of subprocess calls
- GIT_CEILING_DIRECTORIES and filesystem root traversal tests work with `pyfakefs`

**What Still Uses Real Filesystem**:
- Async functions that call `_acquire_development_information()`
- Only 2-3 async test functions out of ~15 total distribution tests

## Why Disk I/O Seems Necessary

### The Core Issue
The distribution module's async functions use `aiofiles` for file I/O, which is a third-party library that provides async file operations. Our internal `_io.acquire_text_file_async()` function wraps `aiofiles` calls.

### Integration Challenges
1. **aiofiles + pyfakefs**: `aiofiles` uses a thread pool executor that bypasses `pyfakefs`'s patching mechanism
2. **Immutable Modules**: Our `frigid` package makes internal modules immutable, preventing monkey-patching of our own I/O functions
3. **Testing Guidelines**: We should only patch third-party modules, not our own internal modules

### Potential Solutions to Explore

#### Option 1: Accept Limited Real I/O
- Keep 2-3 async tests using real temporary directories
- 90%+ of tests still use `pyfakefs` (major performance win)
- Real I/O limited to testing actual async file operations

#### Option 2: Dependency Injection in Distribution Module
- Modify `_acquire_development_information()` to accept optional file reader function
- Inject mock file reader in tests
- Requires code changes to production code for testability

#### Option 3: aiofiles-compatible Mock
- Create a custom async file reader that works with `pyfakefs`
- Replace `aiofiles` usage in test context only
- May require understanding `aiofiles` threading model

#### Option 4: Synchronous File I/O for Tests
- Create test-specific code path that uses sync I/O instead of async
- Would require conditional logic or test doubles

## Performance Impact Analysis
Even with the hybrid approach:
- **Before**: ~2.5 seconds for distribution tests (subprocess heavy)
- **Current**: ~0.8-1.0 seconds (major improvement from removing subprocess calls)
- **With full pyfakefs**: Would likely be ~0.3-0.5 seconds

The performance improvement from removing subprocess calls is already substantial.

## Recommendations for Discussion

1. **Is the hybrid approach acceptable?** (Most tests fast, few async tests use real I/O)
2. **Should we modify production code for testability?** (Dependency injection)
3. **Is the current performance improvement sufficient?** (60% faster already)
4. **Are there alternative async file I/O libraries** that work better with `pyfakefs`?

## Final Implementation Status ✅ COMPLETED

### What Was Successfully Achieved
- ✅ **100% test coverage** for `sources/appcore/distribution.py`
- ✅ **60% performance improvement** (2.5s → 1.0s)
- ✅ **Hybrid approach** works effectively in practice
- ✅ **All tests pass** with no regressions
- ✅ **Code quality maintained** (all linters pass)

### Final Architecture: Hybrid Approach
- **Sync functions**: Use `pyfakefs` context manager (`Patcher()`) for fast, reliable testing
- **Async functions**: Use real `tempfile.TemporaryDirectory()` for ~4 tests
- **Frame inspection**: Mock `inspect.currentframe()` instead of subprocess calls
- **Only patch third-party modules**: `importlib_metadata`, `inspect`, `os.environ`

## Key Learnings and Technical Insights

### 1. pyfakefs Integration Challenges
**Issue**: `@patchfs` decorator conflicts with pytest's parameter injection
**Solution**: Use `Patcher()` context manager instead
```python
# ❌ Problematic approach
@patchfs
def test_something(fs):  # Parameter conflict

# ✅ Working approach  
def test_something():
    with Patcher() as patcher:
        fs = patcher.fs
```

### 2. aiofiles + pyfakefs Incompatibility
**Root Cause**: `aiofiles` uses thread pool executor that bypasses `pyfakefs` patching
**Attempted Solutions**:
- `Patcher(modules_to_patch={'aiofiles': None})` → Failed (unsupported)
- Patching internal `appcore.io` → Violates testing guidelines (module immutability)
**Final Solution**: Accept hybrid approach - only 4 async tests use real temp directories

### 3. Frame Inspection Mocking Strategy
**Challenge**: Complex call stack simulation for `_discover_invoker_location()`
**Key Insight**: Must create proper frame chain that simulates external caller:
```python
# External frame (simulates test caller)
external_frame = MagicMock()
external_frame.f_code.co_filename = str(nested_dir / 'caller.py')
external_frame.f_back = None

# Internal frame (simulates appcore package)
appcore_frame = MagicMock()
appcore_frame.f_code.co_filename = str(package_location / 'some_file.py')
appcore_frame.f_back = external_frame

# Mock returns appcore frame, which walks back to external frame
patch('inspect.currentframe', return_value=appcore_frame)
```

### 4. Testing Guidelines Adherence
**Critical Rule**: Only patch third-party modules, never internal modules
**Implication**: Cannot mock `appcore.io.acquire_text_file_async()` or `appcore.distribution._discover_invoker_location()`
**Workaround**: Mock at the boundary (`inspect.currentframe`, `importlib_metadata`)

### 5. Performance vs Purity Trade-offs
**Insight**: Perfect test isolation isn't always worth the complexity cost
**Result**: 60% performance improvement with hybrid approach vs theoretical 80% with full mocking
**Benefit**: Simpler, more maintainable tests that still achieve primary goals

### 6. Coverage-Driven Development Effectiveness
**Approach**: Target specific uncovered lines (52-55, 121-124, 129-130, 132-133)
**Success**: Created focused tests for exact missing branches
**Key Test**: `test_590_prepare_development_mode_missing_package()` directly targets development mode path

## Files Modified
- `tests/test_000_appcore/test_210_distribution.py`: Complete refactoring (32 tests)
- `pyproject.toml`: Added `pyfakefs` dependency  
- `.auxiliary/notes/distribution-test-refactoring.md`: Documentation updates

## Recommendations for Future Similar Work

1. **Start with hybrid approach** rather than attempting perfect mocking
2. **Use `Patcher()` context manager** instead of `@patchfs` decorator for pytest compatibility
3. **Focus on boundary mocking** (third-party APIs) rather than internal module mocking
4. **Measure performance early** to validate optimization efforts
5. **Target specific coverage gaps** rather than broad refactoring
6. **Accept real I/O for complex async operations** when mocking becomes too complex

## Archive Status
This refactoring is **COMPLETE** and ready for removal after integration into permanent documentation.