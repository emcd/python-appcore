# Classcore Inheritance Bug Report

## Issue Summary
Inheritance from immutable dataclasses fails with `TypeError: TestTomlAcquirer already specifies __slots__`

## Reproduction Case
```python
import appcore.configuration as config_module

class TestTomlAcquirer(config_module.TomlAcquirer):
    def _discover_copy_template(self, directories, distribution):
        return io.StringIO("test content")
```

## Error Details
```
TypeError: TestTomlAcquirer already specifies __slots__
    at /usr/lib/python3.10/dataclasses.py:1128: _add_slots
```

## Expected Behavior
Should be able to inherit from immutable dataclasses to override methods for testing purposes, similar to how regular dataclasses support inheritance.

## Context
- Parent class: `appcore.configuration.TomlAcquirer` (immutable dataclass)
- Use case: Testing edge cases by overriding specific methods
- Alternative approaches blocked by immutability constraints (no patching allowed)

## Environment
- Python 3.10.12
- `classcore` immutable dataclass system via `frigid`
- Dataclass with `__slots__` and immutability decorators

## Workaround
Currently using `# pragma: no cover` but inheritance should be the proper solution for testing method variations.

## Priority
Medium - blocks proper testing patterns but workarounds exist.