# Configuration Acquirer Design

## Current State
- `general.toml` template name is hardcoded in `configuration.py:_discover_copy_template()`
- Configuration loading is handled by module-level `acquire()` function
- Users cannot easily customize configuration sources or template names

## Proposed Solution: Protocol-Based Acquirer Design

### Design Overview
Create an `AbstractAcquirer` protocol and implement `TomlAcquirer` as a dataclass:

```python
from typing import Protocol
from dataclasses import dataclass

class AbstractAcquirer(Protocol):
    async def __call__(
        self,
        application_name: str,
        directories: PlatformDirs,
        distribution: DistributionInformation,
        edits: Edits = (),
        file: Absential[Path | io.TextIOBase] = absent,
    ) -> Dictionary[str, Any]:
        ...

@dataclass
class TomlAcquirer:
    filename: str = 'general.toml'
    
    async def __call__(
        self,
        application_name: str,
        directories: PlatformDirs,
        distribution: DistributionInformation,
        edits: Edits = (),
        file: Absential[Path | io.TextIOBase] = absent,
    ) -> Dictionary[str, Any]:
        # Move current acquire() logic here
        # Use self.filename instead of hardcoded 'general.toml'
```

### Integration with prepare()
Add `acquirer` parameter to `prepare()`:

```python
async def prepare(
    exits: AsyncExitStack,
    application: Information = _application_information,
    acquirer: Absential[AbstractAcquirer] = absent,
    configedits: Edits = (),
    configfile: Absential[Path | io.TextIOBase] = absent,
    # ... other parameters
) -> Globals:
    if is_absent(acquirer):
        acquirer = configuration.TomlAcquirer()  # Uses default 'general.toml'
    
    configuration_dict = await acquirer(
        application_name=application.name,
        directories=directories,
        distribution=distribution,
        edits=configedits,
        file=configfile
    )
```

### Benefits
1. **Dependency Injection**: Users can provide custom acquirer instances
2. **Template Customization**: Easy to specify different template names
3. **Future Extensibility**: Can add support for YAML, JSON, etc.
4. **Testing**: Easy to mock/inject test configurations
5. **Backward Compatibility**: Default behavior unchanged
6. **Protocol-Based**: Supports any callable with correct signature

### Usage Examples

#### Custom Template Name
```python
acquirer = appcore.configuration.TomlAcquirer(filename='myapp.toml')
async with AsyncExitStack() as exits:
    globals_dto = await appcore.prepare(exits, acquirer=acquirer)
```

#### Future: Custom Acquirer Types
```python
# Future YAML acquirer
@dataclass
class YamlAcquirer:
    filename: str = 'general.yaml'
    
    async def __call__(self, ...):
        # YAML loading logic
        pass

acquirer = YamlAcquirer(filename='config.yaml')
```

#### Testing: Custom Acquirer
```python
# Custom acquirer for testing
@dataclass
class TestAcquirer:
    config_data: dict
    
    async def __call__(self, *args, **kwargs):
        return self.config_data

acquirer = TestAcquirer(config_data={'app': {'name': 'test'}})
```

## Implementation Steps
1. Create `AbstractAcquirer` protocol in `configuration.py`
2. Create `TomlAcquirer` dataclass in `configuration.py`
3. Move `acquire()` logic to `TomlAcquirer.__call__()` method
4. Update `_discover_copy_template()` to use `self.filename`
5. Add `acquirer` parameter to `prepare()`
6. Update tests and documentation
7. Maintain backward compatibility by keeping module-level `acquire()` as wrapper

## Files to Modify
- `sources/appcore/configuration.py` - Add AbstractAcquirer protocol and TomlAcquirer class
- `sources/appcore/preparation.py` - Add acquirer parameter  
- `sources/appcore/__init__.py` - Export AbstractAcquirer and TomlAcquirer
- `documentation/examples/configuration.rst` - Add custom acquirer examples