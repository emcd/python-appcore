# Configuration Acquirer Design

## Current State
- `general.toml` template name is hardcoded in `configuration.py:_discover_copy_template()`
- Configuration loading is handled by module-level `acquire()` function
- Users cannot easily customize configuration sources or template names

## Proposed Solution: Configuration.Acquirer Class

### Design Overview
Convert the module-level `acquire()` function to a method on a `configuration.Acquirer` class:

```python
class Acquirer:
    def __init__(
        self,
        template_name: str = 'general.toml',
        # Future extensibility:
        # loader: Callable[[str], dict] = tomli.loads,
        # source_type: Literal['toml', 'yaml', 'json'] = 'toml'
    ):
        self.template_name = template_name
    
    async def acquire(
        self,
        application_name: str,
        directories: PlatformDirs,
        distribution: DistributionInformation,
        edits: Edits = (),
        file: Absential[Path | io.TextIOBase] = absent,
    ) -> Dictionary[str, Any]:
        # Move current acquire() logic here
        # Use self.template_name instead of hardcoded 'general.toml'
```

### Integration with prepare()
Add `acquirer` parameter to `prepare()`:

```python
async def prepare(
    exits: AsyncExitStack,
    application: Information = _application_information,
    acquirer: Absential[configuration.Acquirer] = absent,
    configedits: Edits = (),
    configfile: Absential[Path | io.TextIOBase] = absent,
    # ... other parameters
) -> Globals:
    if is_absent(acquirer):
        acquirer = configuration.Acquirer()  # Uses default 'general.toml'
    
    configuration_dict = await acquirer.acquire(
        application_name=application.name,
        directories=directories,
        distribution=distribution,
        edits=configedits,
        file=configfile
    )
```

### Benefits
1. **Dependency Injection**: Users can provide custom `Acquirer` instances
2. **Template Customization**: Easy to specify different template names
3. **Future Extensibility**: Can add support for YAML, JSON, etc.
4. **Testing**: Easy to mock/inject test configurations
5. **Backward Compatibility**: Default behavior unchanged

### Usage Examples

#### Custom Template Name
```python
acquirer = appcore.configuration.Acquirer(template_name='myapp.toml')
async with AsyncExitStack() as exits:
    globals_dto = await appcore.prepare(exits, acquirer=acquirer)
```

#### Future: Custom Loader
```python
# Future possibility
acquirer = appcore.configuration.Acquirer(
    template_name='config.yaml',
    loader=yaml.safe_load,
    source_type='yaml'
)
```

## Implementation Steps
1. Create `Acquirer` class in `configuration.py`
2. Move `acquire()` logic to `Acquirer.acquire()` method
3. Update `_discover_copy_template()` to use `self.template_name`
4. Add `acquirer` parameter to `prepare()`
5. Update tests and documentation
6. Maintain backward compatibility by keeping module-level `acquire()` as wrapper

## Files to Modify
- `sources/appcore/configuration.py` - Add Acquirer class
- `sources/appcore/preparation.py` - Add acquirer parameter  
- `sources/appcore/__init__.py` - Export Acquirer class
- `documentation/examples/configuration.rst` - Add custom acquirer examples