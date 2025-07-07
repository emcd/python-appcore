# Remaining Coverage Analysis - Path to 100%

Current coverage: **96%** (11 missing lines)
Target: **100%**

## Missing Lines by Category

### Abstract Methods (4 lines)
These are `NotImplementedError` lines in abstract base classes:

1. **configuration.py:63** - `AcquirerAbc.__call__()` abstract method
2. **dictedits.py:43** - `EditAbc.__call__()` abstract method  
3. **generics.py:51** - `Result.extract()` abstract method
4. **generics.py:61** - `Result.transform()` abstract method

**Recommendation**: Apply `# pragma: no cover` to these lines. Testing abstract methods that are designed to raise `NotImplementedError` provides no value and would require creating broken concrete implementations.

### Edge Cases - Testable (4 lines)

5. **configuration.py:81** - `file = self._discover_copy_template(...)` when file is absent
   - **Action**: Create test calling `TomlAcquirer` with absent file parameter
   
6. **inscription.py:70-71** - `Modes.Pass` case in logging setup
   - **Action**: Create test with `Control(mode=Modes.Pass)` 
   
7. **inscription.py:94** - Environment variable return in logging level discovery
   - **Action**: Create test with `APPCORE_INSCRIPTION_LEVEL` or `APPCORE_LOG_LEVEL` set
   
8. **io.py:40** - Return path when deserializer is absent
   - **Action**: Create test calling `acquire_text_file_async` without deserializer

### Edge Cases - Pragma Candidates (3 lines)

The distribution.py lines 106, 110 were already handled with pragmas as they represent filesystem traversal error conditions that are extremely difficult to test reliably.

## Implementation Strategy

### Phase 1: Apply Pragmas to Abstract Methods (immediate)
- Quick wins for 4 lines
- Philosophically correct (abstract methods shouldn't be tested)

### Phase 2: Test Remaining Edge Cases (moderate effort)  
- 4 additional tests to achieve 100% coverage
- All represent legitimate code paths that can be tested

## Expected Outcome
- **Phase 1**: 96% → 97% (pragmas don't count against coverage)
- **Phase 2**: 97% → 100% (testing edge cases)

This approach balances testing value with implementation effort, focusing testing on meaningful code paths while pragmatically excluding abstract method stubs.