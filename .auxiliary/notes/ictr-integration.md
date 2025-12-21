# Integration Proposal: `ictr` as First-Class Inscription System

## Overview

This proposal adds `ictr` as a first-class inscription system in `appcore`, operating
alongside `logging`. The `ictr` package becomes a required dependency.

## Design Principles

1. **First-class citizen**: `ictr` is not a separate "mode" but a parallel subsystem
2. **Coexistence**: Both `logging` and `ictr` are always prepared (logging for third-party libraries)
3. **Unified configuration**: No separate `IctrControl`—extend `Control` directly
4. **Consistent environment variables**: Use `{APP}_ACTIVE_FLAVORS` and `{APP}_TRACE_LEVELS`

## Changes to `inscription.py`

### Extended `Control` Dataclass

```python
class Control( __.immut.DataclassObject ):
    ''' Application inscription configuration. '''

    mode: Presentations = Presentations.Plain
    level: Levels = 'info'
    target: Target = __.sys.stderr

    # ictr configuration (first-class)
    trace_levels: int | __.cabc.Mapping[ str | None, int ] = -1
    # -1 globally disables traces; 0-9 enables that depth

    active_flavors: __.typx.Optional[
        __.cabc.Sequence[ str ]
        | __.cabc.Mapping[ str | None, __.cabc.Sequence[ str ] ]
    ] = None
    # None derives from level; explicit value overrides

    install_ictr: bool = True
    # Whether to install ictr dispatcher into builtins

    ictr_alias: str = 'ictr'
    # Builtins alias for ictr dispatcher
```

### Revised `prepare` Function

```python
def prepare( auxdata: _state.Globals, /, control: Control ) -> None:
    ''' Prepares various scribes in a sensible manner. '''
    target = _process_target( auxdata, control )
    # Always prepare logging (for third-party libraries)
    _prepare_scribes_logging( auxdata, control, target )
    # Always prepare ictr
    _prepare_scribes_ictr( auxdata, control, target )
```

### New `_prepare_scribes_ictr` Function

```python
def _prepare_scribes_ictr(
    auxdata: _state.Globals, control: Control, /, target: __.typx.TextIO
) -> None:
    ''' Prepares ictr dispatcher as inscription scribe. '''
    import ictr as _ictr

    # Derive environment variable name prefix from application name
    app_prefix = ''.join(
        c.upper( ) if c.isalnum( ) else '_'
        for c in auxdata.application.name )

    initargs: dict[ str, __.typx.Any ] = { }

    # Configure active flavors
    if control.active_flavors is not None:
        initargs[ 'active_flavors' ] = control.active_flavors
        initargs[ 'evname_active_flavors' ] = None  # Explicit overrides env
    else:
        evname = f"{app_prefix}_ACTIVE_FLAVORS"
        if evname in __.os.environ:
            initargs[ 'evname_active_flavors' ] = evname
        else:
            initargs[ 'active_flavors' ] = _derive_ictr_flavors( control.level )
            initargs[ 'evname_active_flavors' ] = None

    # Configure trace levels
    if control.trace_levels != -1:
        initargs[ 'trace_levels' ] = control.trace_levels
        initargs[ 'evname_trace_levels' ] = None
    else:
        initargs[ 'evname_trace_levels' ] = f"{app_prefix}_TRACE_LEVELS"

    # Configure general dispatcher settings with colorization control
    colorize = control.mode is Presentations.Rich
    initargs[ 'generalcfg' ] = _produce_ictr_generalcfg( colorize )

    # Configure printer factory from target
    initargs[ 'printer_factories' ] = (
        _ictr.produce_printer_factory_default( target ), )

    # Create and optionally install dispatcher
    if control.install_ictr:
        dispatcher = _ictr.install( alias = control.ictr_alias, **initargs )
    else:
        dispatcher = _ictr.produce_dispatcher( **initargs )

    # Register application address
    dispatcher.register_address( name = auxdata.application.name )
```

### Colorization Control via Compositor Configuration

Colorization is controlled at the configuration level via `LinearizerConfiguration.colorize`.
When `Presentations.Plain` or `Presentations.Null`, we provide a `generalcfg` with a
compositor factory that produces compositors with `colorize=False`.

```python
def _produce_ictr_generalcfg( colorize: bool ) -> __.typx.Any:
    ''' Produces ictr dispatcher configuration with colorization control. '''
    import ictr as _ictr
    from ictr.standard import (
        CompositorConfiguration, LinearizerConfiguration,
    )

    if colorize:
        # Rich mode: use default configuration (TTY detection applies)
        return _ictr.configuration.DispatcherConfiguration( )

    # Plain/Null mode: configure compositor factory with colorize=False
    linearizercfg = LinearizerConfiguration( colorize = False )
    compositorcfg = CompositorConfiguration( linearizercfg = linearizercfg )

    def produce_compositor_factory(
        introducer: __.typx.Any = __.absent,
        line_prefix_initial: str = '',
        line_prefix_subsequent: str = '  ',
        trace_exceptions: bool = False,
    ) -> __.cabc.Callable[ [ str, __.typx.Any ], __.typx.Any ]:
        ''' Produces compositor factory with colorize=False. '''
        from ictr.standard import (
            Compositor, ExceptionsConfiguration,
        )

        def produce_compositor(
            address: str, flavor: __.typx.Any
        ) -> __.typx.Any:
            ecfg = ExceptionsConfiguration(
                enable_discovery = trace_exceptions,
                enable_stacktraces = trace_exceptions )
            lcfg = LinearizationConfiguration(
                colorize = False, exceptionscfg = ecfg )
            ccfg = CompositorConfiguration(
                line_prefix_initial = line_prefix_initial,
                line_prefix_subsequent = line_prefix_subsequent,
                linearizercfg = lcfg )
            if _ictr.is_absent( introducer ):
                return Compositor( configuration = ccfg )
            return Compositor( configuration = ccfg, introducer = introducer )

        return produce_compositor

    return _ictr.configuration.DispatcherConfiguration(
        compositor_factory = produce_compositor_factory( ) )
```

### Level-to-Flavor Derivation

```python
def _derive_ictr_flavors( level: Levels ) -> frozenset[ str ]:
    ''' Derives active ictr flavors from inscription level.

        Semantic flavors (future, success, advice) are always included
        as they represent message categories rather than severity levels.
    '''
    # Semantic flavors - always active
    semantic = frozenset( { 'future', 'success', 'advice' } )
    # Error-family flavors - always active
    errors = frozenset( { 'error', 'errorx', 'abort', 'abortx' } )
    base = semantic | errors

    match level:
        case 'debug':
            return base | { 'note', 'monition' }
        case 'info':
            return base | { 'note' }
        case 'warn':
            return base | { 'monition' }
        case 'error' | 'critical':
            return base
    return base
```

## Changes to `cli/core.py`

### Extended `InscriptionControl` Dataclass

```python
class InscriptionControl( __.immut.DataclassObject ):
    ''' Inscription (logging, debug prints) control. '''

    level: __.typx.Annotated[
        __.inscription.Levels, __.tyro.conf.arg( help = "Log verbosity." )
    ] = 'info'
    presentation: __.typx.Annotated[
        __.inscription.Presentations,
        __.tyro.conf.arg( help = "Log presentation mode (format)." ),
    ] = __.inscription.Presentations.Plain
    target_file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        _InscriptionTargetMutex,
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( help = "Log to specified file." ),
    ] = None
    target_stream: __.typx.Annotated[
        __.typx.Optional[ TargetStreams ],
        _InscriptionTargetMutex,
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( help = "Log to stdout or stderr." ),
    ] = TargetStreams.Stderr

    # ictr-specific CLI options
    trace_levels: __.typx.Annotated[
        int,
        __.tyro.conf.arg(
            aliases = ( '-t', '--trace', ),
            help = "Trace depth (0-9, -1 disables)." ),
    ] = -1
    active_flavors: __.typx.Annotated[
        __.typx.Optional[ tuple[ str, ... ] ],
        __.tyro.conf.arg( help = "Active ictr flavors (comma-separated)." ),
    ] = None

    def as_control(
        self, exits: __.ctxl.AsyncExitStack
    ) -> __.inscription.Control:
        ''' Produces compatible inscription control for appcore. '''
        if self.target_file is not None:
            target_location = self.target_file.resolve( )
            target_location.parent.mkdir( exist_ok = True, parents = True )
            target_stream = exits.enter_context( target_location.open( 'w' ) )
        else:
            target_stream_ = self.target_stream or TargetStreams.Stderr
            match target_stream_:
                case TargetStreams.Stdout: target_stream = __.sys.stdout
                case TargetStreams.Stderr: target_stream = __.sys.stderr
        return __.inscription.Control(
            mode = self.presentation,
            level = self.level,
            target = target_stream,
            trace_levels = self.trace_levels,
            active_flavors = self.active_flavors )
```

## Environment Variable Scheme

For an application named `my-app`:

| Variable | Purpose |
|----------|---------|
| `MY_APP_INSCRIPTION_LEVEL` | Controls logging level (existing) |
| `MY_APP_LOG_LEVEL` | Controls logging level (existing alias) |
| `MY_APP_ACTIVE_FLAVORS` | Controls ictr active flavors |
| `MY_APP_TRACE_LEVELS` | Controls ictr trace depths |

The `ictr` package's native `ICTR_*` vars remain available as global defaults
when app-specific vars are not set.

## Colorization Behavior

| Presentation Mode | `logging` | `ictr` |
|-------------------|-----------|--------|
| `Null` | External management | `colorize=False` |
| `Plain` | `StreamHandler` | `colorize=False` |
| `Rich` | `RichHandler` | TTY-detected colors |

## Dependency Changes

Add `ictr` as a required dependency in `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "ictr >= 1.0a1",
]
```

## Summary of File Changes

### `sources/appcore/inscription.py`

1. **Extend `Control`**: Add `trace_levels`, `active_flavors`, `install_ictr`, `ictr_alias`
2. **Modify `prepare()`**: Call both `_prepare_scribes_logging` and `_prepare_scribes_ictr`
3. **Add `_prepare_scribes_ictr()`**: Configure and install ictr dispatcher
4. **Add `_derive_ictr_flavors()`**: Map inscription level to ictr flavor set
5. **Add `_produce_ictr_generalcfg()`**: Produce dispatcher configuration with colorization control

### `sources/appcore/cli/core.py`

1. **Extend `InscriptionControl`**: Add `trace_levels` and `active_flavors` with CLI annotations
2. **Update `as_control()`**: Pass new fields to `inscription.Control`

### `pyproject.toml`

1. Add `ictr >= 1.0a1` to dependencies

## Presentation Integration

The `ictr` package now provides `Presentation` protocol and concrete implementations
(`PlaintextPresentation`, `JsonPresentation`, `MarkdownPresentation`) for rendering
objects that implement the corresponding renderable protocols.

### Display Architecture Decision

**DisplayOptions removed from Globals/auxdata**: Commands return renderable results that
bubble up to the `Application` instance. The application handles presentation using its
own `DisplayOptions`, eliminating the need to thread display context through command
execution.

```python
# Application handles rendering
class Application:
    display: DisplayOptions

    async def execute_command(self, command: Command) -> None:
        result = await command.execute(auxdata)  # No display options needed
        await self.render_result(result)  # Application controls presentation

    async def render_result(self, obj: object) -> None:
        # Select presentation based on display options
        presentation = self._select_presentation()

        # Create linearizer state from printer
        printer = self._create_printer()
        control = printer.provide_textualization_control()
        auxdata = ictr.standard.LinearizerState.from_configuration(
            ictr.standard.LinearizerConfiguration(), control)

        # Render
        text = presentation.render(auxdata, obj)
        await self._write_output(text)
```

### Progress Reporting

For commands that need progress updates, the application provides a callback:

```python
class Globals:
    progress_reporter: Optional[Callable[[str], None]] = None

class Application:
    def create_progress_reporter(self) -> Callable[[str], None]:
        """Creates progress callback bound to application's display settings."""
        def report(message: str) -> None:
            if self.display.colorize:
                # Use ictr or rich formatting
                ictr('note')(message)
            else:
                print(message, file=self.display.target)
        return report
```

## Open Questions

None - architecture aligned with ictr Presentation pattern.
