# Distribution Module Coverage Analysis

## Missing Lines Analysis (7 lines, 19% uncovered)

### **Line 45: PyInstaller Path Assignment** 
```python
project_anchor = __.Path( getattr( sys, '_MEIPASS' ) )
```
**Issue:** Existing test patches `sys.frozen` and `sys._MEIPASS` but doesn't call `Information.prepare()` 
**Solution:** ✅ **Testable** - Fix existing test to actually call `prepare()` method
**Effort:** Low

### **Lines 56-58: Production Distribution Path**
```python
editable = False
name = name[ 0 ]  
location = await _acquire_production_location( package, exits )
```
**Issue:** This requires `packages_distributions().get(package)` to return a non-None value
**Challenge:** Would need to mock `importlib_metadata.packages_distributions` to simulate installed package
**Solution:** 🟡 **Complex but doable** - Mock the metadata lookup 
**Effort:** Medium

### **Line 97: GIT_CEILING_DIRECTORIES Processing**
```python
limits.update(
    __.Path( limit ).resolve( )
    for limit in limits_value.split( ':' ) if limit.strip( ) )
```
**Issue:** Requires setting `GIT_CEILING_DIRECTORIES` environment variable
**Solution:** ✅ **Testable** - Set environment variable in test
**Effort:** Low

### **Line 104: Git Ceiling Error**
```python
raise _exceptions.FileLocateFailure( 
    'project root discovery', 'pyproject.toml' )
```
**Issue:** Error when project search hits git ceiling directory  
**Solution:** 🟡 **Testable but complex** - Create temp directory structure with ceiling
**Effort:** Medium

### **Line 107: Filesystem Root Error**  
```python
raise _exceptions.FileLocateFailure(
    'project root discovery', 'pyproject.toml' )
```
**Issue:** Error when project search reaches filesystem root
**Solution:** 🔴 **Very difficult** - Would need to simulate filesystem traversal to root
**Effort:** High

## Recommendations

### **Approach 1: Target Easy Wins (Recommended)**
Focus on lines that are straightforward to test:

1. **Line 45** (PyInstaller) - Fix existing test ✅ 
2. **Line 97** (GIT_CEILING) - Add environment variable test ✅
3. **Lines 56-58** (Production) - Mock metadata if worthwhile 🟡

**Expected Coverage Gain:** ~60% of missing lines → **~88-90% module coverage**

### **Approach 2: Use `# pragma: no cover` for Edge Cases**
Mark untestable/extreme edge cases:

1. **Line 104** - Git ceiling hit (rare edge case)
2. **Line 107** - Filesystem root reached (should never happen in practice)

**Rationale:** 
- These are defensive error conditions for extreme scenarios
- Testing them would require complex filesystem mocking
- The value of testing them is low vs. implementation cost

### **Approach 3: Hybrid (Recommended)**
- Test lines 45, 97 (easy wins)
- Consider testing lines 56-58 if metadata mocking is clean
- Use `# pragma: no cover` for lines 104, 107

**Expected Result:** **~95-97% module coverage** with clean, maintainable tests

## Implementation Strategy

### **Phase 1: Easy Wins**
```python
# Fix PyInstaller test to actually call prepare()
@pytest.mark.asyncio
async def test_pyinstaller_prepare():
    with patch('sys.frozen', True), patch('sys._MEIPASS', '/bundle'):
        exits = AsyncExitStack()
        result = await Information.prepare('test-package', exits)
        # Line 45 now covered
        
# Test GIT_CEILING_DIRECTORIES processing  
def test_git_ceiling_processing():
    with patch.dict('os.environ', {'GIT_CEILING_DIRECTORIES': '/tmp:/var'}):
        # Line 97 now covered
```

### **Phase 2: Production Path (Optional)**
```python
# Mock importlib_metadata to simulate installed package
with patch('importlib_metadata.packages_distributions') as mock_pkg:
    mock_pkg.return_value = {'test-package': ['dist-name']}
    # Lines 56-58 now covered
```

### **Phase 3: Pragma Annotations**
```python
# In distribution.py
if current in limits:
    raise _exceptions.FileLocateFailure(  # pragma: no cover
        'project root discovery', 'pyproject.toml' )
        
# At filesystem root
raise _exceptions.FileLocateFailure(  # pragma: no cover  
    'project root discovery', 'pyproject.toml' )
```

## Decision Matrix

| Line | Effort | Value | Recommendation |
|------|--------|-------|----------------|
| 45   | Low    | High  | ✅ Test it     |
| 56-58| Medium | Medium| 🟡 Consider    |
| 97   | Low    | Medium| ✅ Test it     |
| 104  | High   | Low   | 🚫 Pragma     |
| 107  | High   | Low   | 🚫 Pragma     |

## Final Recommendation

**Implement Phase 1 + Phase 3** for the best effort/value ratio:
- Test the easy cases (lines 45, 97) 
- Use `# pragma: no cover` for extreme edge cases (lines 104, 107)
- Consider production path testing (lines 56-58) based on available time

**Expected outcome:** 95%+ coverage with maintainable, valuable tests.