# Package Detection Improvements

## Executive Summary

Investigation revealed fundamental flaws in the current `_discover_invoker_location()` implementation. The user's interconnected analysis identified critical issues and provided an elegant solution that properly handles namespace packages, installed packages, and edge cases.

## Key Findings

### 1. `__module__` Check is Completely Useless
**Evidence**: Comprehensive testing across all execution contexts (functions, methods, modules, etc.) showed `__module__` is always `None` in frame globals.

**Current Code Problem**: 
```python
mname = frame.f_globals.get('__module__')
if not mname: continue  # This always triggers!
```

**Solution**: Remove `__module__` check entirely.

### 2. `__package__` Fallback is Unnecessary 
**Evidence**: `__name__` is always available and provides the right information. Even for `__init__.py` files, `__name__` contains the package name.

**Current Code Problem**: Added unnecessary complexity with `__package__` fallback when `__name__` is sufficient.

**Solution**: Use `__name__` directly, eliminate `__package__` fallback.

### 3. Namespace Package Issue is Critical
**Evidence**: Current logic uses naive splitting on first dot:
- `mynamespace.subpkg.module` → `mynamespace` (namespace root, no `pyproject.toml`)
- But should detect → `mynamespace.subpkg` (actual package with `pyproject.toml`)

**Real-World Impact**: Namespace packages can have separate `pyproject.toml` files in subpackages. Current detection fails to find resources.

**Solution**: Use sys.modules backward detection to find actual package boundaries.

### 4. sys.modules Backward Detection Algorithm
**Key Insight**: Work backwards through dotted names, checking sys.modules for things that are actual packages (have `__path__` attribute).

**Algorithm**:
```python
def find_package_boundary(full_name):
    components = full_name.split('.')
    for i in range(len(components), 0, -1):
        candidate = '.'.join(components[:i])
        if candidate in sys.modules:
            module = sys.modules[candidate]
            if hasattr(module, '__path__'):  # It's a package
                return candidate
            # else: continue searching for containing package
    return components[0]  # Fallback
```

**Test Results**:
- `collections.abc` → `collections` ✓
- `importlib.metadata` → `importlib` ✓  
- `mynamespace.subpkg.module` → `mynamespace.subpkg` ✓ (not `mynamespace`)

## Revised Implementation Plan

### Phase 1: Core Algorithm Replacement
Replace the current `_discover_invoker_location()` logic:

**FROM** (current):
```python
# Try __module__ first, fallback to __package__
mname = frame.f_globals.get('__module__')
if mname:
    pname = mname.split('.', maxsplit=1)[0]
else:
    package_name = frame.f_globals.get('__package__')
    if package_name:
        pname = package_name.split('.', maxsplit=1)[0]
    else:
        continue
```

**TO** (improved):
```python
# Get __name__ (always available) and find actual package boundary
name_val = frame.f_globals.get('__name__')
if not name_val or name_val == '__main__':
    continue

pname = find_package_boundary(name_val)
if not pname:
    continue
```

### Phase 2: Add Package Boundary Detection
Add new helper function:
```python
def find_package_boundary(full_name):
    """Find actual package boundary using sys.modules backward detection."""
    if not full_name or full_name == '__main__':
        return None
    
    components = full_name.split('.')
    for i in range(len(components), 0, -1):
        candidate = '.'.join(components[:i])
        if candidate in sys.modules:
            module = sys.modules[candidate]
            if hasattr(module, '__path__'):
                return candidate
    return components[0]  # Fallback for edge cases
```

### Phase 3: Update Tests
Add comprehensive test coverage for:
1. `__name__` detection (replace `__package__` fallback test)
2. Namespace package scenarios
3. sys.modules boundary detection
4. Coverage for missing branches (lines 53→65, 139→126)

### Phase 4: Validation
Verify the fix works with:
- UV tool `emcdproj` calling appcore ✓ (already tested)
- Namespace packages with separate `pyproject.toml` files
- Regular packages and modules
- Edge cases like `__main__` and missing modules

## Supporting Evidence

### Cross-Environment Clarification
**User's Correction**: UV's `emcdproj` uses UV's `appcore` (same environment). Cross-environment mixing only happens via working directory fallback, not different sys.path. The sys.path-based detection approach doesn't provide significant advantages over frame globals + sys.modules.

### Coverage Analysis
**Current State**: 98% coverage with 2 missing branches
- Line 53→65: Package absent scenario (condition always True in tests)
- Line 139→126: stdlib detection continue (never executed in tests)

**Target**: Restore 100% coverage by adding missing test scenarios.

## Implementation Priority
1. **High**: Core algorithm replacement (Phase 1-2)
2. **High**: Namespace package test scenarios  
3. **Medium**: Coverage completion
4. **Low**: Performance optimization (if needed)

## Risk Assessment
**Low Risk**: Changes are isolated to `_discover_invoker_location()` function with comprehensive test coverage. Backwards compatibility maintained through same return signature.

## Success Criteria
1. ✅ UV tool `emcdproj` works correctly
2. ✅ Namespace packages with separate `pyproject.toml` files detected correctly
3. ✅ All existing tests pass
4. ✅ 100% test coverage restored
5. ✅ No performance regression

---

**Date**: 2025-07-13  
**Status**: Ready for implementation  
**Next**: Implement Phase 1-2 changes in source code