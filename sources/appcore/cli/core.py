# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' CLI foundation classes and interfaces.

    Core infrastructure for building command-line interfaces. Comprehensive
    framework for creating CLI applications with rich presentation options,
    flexible output routing, and integrated logging capabilities.

    Key Components
    ==============

    Command Framework
    -----------------
    * :class:`Command` - Abstract base class for CLI command implementations
    * :class:`Application` dataclass for command-line application configuration
    * Rich integration with Tyro for automatic argument parsing and help
      generation

    Display and Output Control
    --------------------------
    * :class:`DisplayOptions` - Configuration for output presentation and
      routing
    * :class:`InscriptionControl` - Configuration for logging and diagnostic
      output
    * Stream routing (stdout/stderr) and file output capabilities
    * Rich terminal detection with colorization control

    Example Usage
    =============

    Basic CLI application with custom display options and subcommands::

        from appcore import cli, state

        class MyDisplayOptions( cli.DisplayOptions ):
            format: str = 'table'

        class StatusCommand( cli.Command ):
            async def execute( self, auxdata: state.Globals ) -> None:
                print( f"Status: Running" )

        class InfoCommand( cli.Command ):
            async def execute( self, auxdata: state.Globals ) -> None:
                print( f"App: {auxdata.application.name}" )

        class MyApplication( cli.Application ):
            cli: MyDisplayOptions = __.dcls.field(
                default_factory = MyDisplayOptions )
            command: __.typx.Union[
                __.typx.Annotated[
                    StatusCommand,
                    __.tyro.conf.subcommand( 'status', prefix_name = False ),
                ],
                __.typx.Annotated[
                    InfoCommand,
                    __.tyro.conf.subcommand( 'info', prefix_name = False ),
                ],
            ] = __.dcls.field( default_factory = StatusCommand )

            async def execute( self, auxdata: state.Globals ) -> None:
                await self.command( auxdata )

    Note: Display options are accessed via ``self.cli`` in the application, not
    through ``auxdata``. Commands receive ``auxdata`` for application state, but
    rendering is handled by the application instance
'''  # noqa: E501


from . import __


_PROTOCOL_RTC_MUTABLES = (
    '_is_runtime_protocol', '__non_callable_proto_members__' )


_DisplayTargetMutex = (
    __.tyro.conf.create_mutex_group(
        required = False, title = 'CLI display options' ) )
_InscriptionTargetMutex = (
    __.tyro.conf.create_mutex_group(
        required = False, title = 'inscription options' ) )


presentations_registry: __.accret.Dictionary[
    str, str | type[ __.ictrstd.Presentation ]
] = __.accret.Dictionary(
    json = 'clioptions_json',
    markdown = __.ictrstd.MarkdownPresentation,
    plaintext = __.ictrstd.PlaintextPresentation,
)


class TargetStreams( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Target stream selection. '''

    Stdout  = 'stdout'
    Stderr  = 'stderr'


class DisplayOptions( __.immut.DataclassObject ):
    ''' Display configuration for command line interfaces. '''

    colorize: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Render with color and other attributes? ''' ),
        __.tyro.conf.arg( aliases = ( '--ansi-sgr', ) )
    ] = True
    # TODO? 'columns_max' and other fields from linearizer configuration
    force_colorize: __.typx.Annotated[
        bool,
        __.ddoc.Doc(
            ''' Forcibly render with color and other attributes? ''' ),
        __.tyro.conf.arg( aliases = ( '--force-ansi-sgr', ) ),
    ] = False
    presentation: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            ''' Name of a presentation mode (format).

                E.g., 'json', 'markdown', etc....
            ''' ),
        # TODO: Generate Tyro help string dynamically from registry.
        __.tyro.conf.arg( aliases = ( '--cli-format', ) ),
    ] = 'markdown'
    target_file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.ddoc.Doc( ''' Render CLI display to specified file. ''' ),
        _DisplayTargetMutex,
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( aliases = ( '--console-redirect-file', ) ),
    ] = None
    target_stream: __.typx.Annotated[
        __.typx.Optional[ TargetStreams ],
        __.ddoc.Doc( ''' Render CLI display on stdout or stderr. ''' ),
        _DisplayTargetMutex,
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( aliases = ( '--console-stream', ) ),
    ] = TargetStreams.Stdout

    async def provide_printer(
        self, exits: __.ctxl.AsyncExitStack
    ) -> __.ictr.standard.Printer:
        ''' Provides printer from options. '''
        # TODO: Cache printer or make it a __post_init__ attribute.
        target: __.typx.TextIO
        if self.target_file is not None:
            location = self.target_file.resolve( )
            location.parent.mkdir( exist_ok = True, parents = True )
            target = exits.enter_context( location.open( 'w' ) )
        else:
            sname = self.target_stream or TargetStreams.Stderr
            match sname:
                case TargetStreams.Stdout: target = __.sys.stdout
                case TargetStreams.Stderr: target = __.sys.stderr
        return __.ictr.standard.Printer(
            target = target, force_colorize = self.force_colorize )


class InscriptionControl( __.immut.DataclassObject ):
    ''' Inscription (logging, debug prints) control. '''

    # TODO? Way to activate/deactivate all flavors (globally or per-address).
    #       Format: --activate-all-flavors
    #       Format: --activate-all-flavors-for <address>
    #       Format: --deactivate-all-flavors
    #       Format: --deactivate-all-flavors-for <address>
    active_flavors: __.typx.Annotated[
        __.typx.Optional[ list[ str ] ],
        __.ddoc.Doc(
            ''' Inscription flavors to activate.

                Flavor names, prefixed by "<address>:", apply to that address
                rather than globally.

                Available global flavor names are determined by the
                application. Available per-address flavor names are determined
                by the library associated with the address.
            ''' ),
        __.tyro.conf.DisallowNone,
        __.tyro.conf.UseAppendAction,
        __.tyro.conf.arg(
            name = 'active-flavor', aliases = ( '--scribe-flavor', ) ),
    ] = None
    level: __.typx.Annotated[
        # TODO: Drop. Infer from active flavors and trace level.
        #       DEBUG if trace level >= 0.
        #       'note' -> INFO, 'monition' -> WARN, 'error' -> ERROR
        __.inscription.Levels, __.ddoc.Doc( ''' Log verbosity. ''' )
    ] = 'info'
    presentation: __.typx.Annotated[
        # TODO: Drop. If colorization desired, try to use Rich.
        __.inscription.Presentations,
        __.ddoc.Doc( ''' Log presentation mode (format). ''' ),
    ] = __.inscription.Presentations.Plain
    target_file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        _InscriptionTargetMutex,
        __.ddoc.Doc( ''' Log to specified file. ''' ),
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( aliases = ( '--log-file', ) ),
    ] = None
    target_stream: __.typx.Annotated[
        __.typx.Optional[ TargetStreams ],
        _InscriptionTargetMutex,
        __.ddoc.Doc( ''' Log to stdout or stderr. ''' ),
        __.tyro.conf.DisallowNone,
        __.tyro.conf.arg( aliases = ( '--log-stream', ) ),
    ] = TargetStreams.Stderr
    trace_levels: __.typx.Annotated[
        __.typx.Optional[ list[ str ] ],
        __.ddoc.Doc(
            ''' Inscription trace levels to activate.

                Trace levels, prefixed by "<address>:", apply to that address
                rather than globally.

                Levels are from 0 to 9. Negative integers disable debug traces.
            ''' ),
        __.tyro.conf.DisallowNone,
        __.tyro.conf.UseAppendAction,
        __.tyro.conf.arg(
            name = 'trace-level', aliases = ( '--trace-level', ) ),
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
        active_flavors = _parse_active_flavors( self.active_flavors )
        trace_levels = _parse_trace_levels( self.trace_levels )
        return __.inscription.Control(
            active_flavors = active_flavors,
            mode = self.presentation,
            level = self.level,
            target = target_stream,
            trace_levels = trace_levels )


@__.typx.runtime_checkable
class Command(
    __.immut.DataclassProtocol, __.typx.Protocol,
    class_mutables = _PROTOCOL_RTC_MUTABLES,
):
    ''' Standard interface for command implementations.

        Example::

            class StatusCommand( Command ):
                async def execute( self, auxdata: state.Globals ) -> None:
                    print( f"Application: {auxdata.application.name}" )
    '''

    async def __call__( self, auxdata: __.Globals ) -> object:
        ''' Prepares session context and executes command. '''
        raise NotImplementedError  # pragma: no cover


@__.typx.runtime_checkable
class Application(
    __.immut.DataclassProtocol, __.typx.Protocol,
    class_mutables = _PROTOCOL_RTC_MUTABLES,
):
    ''' Common infrastructure and standard interface for applications.

        Example::

            class MyApplication( Application ):

                cli: DisplayOptions = __.dcls.field(
                    default_factory = DisplayOptions )

                async def execute( self, auxdata: state.Globals ) -> None:
                    # Use self.cli for display options
                    printer = await self.cli.provide_printer( auxdata.exits )
                    print( f"Application: {auxdata.application.name}",
                           file = printer.target )
    '''

    clioptions: __.typx.Annotated[
        DisplayOptions,
        __.ddoc.Doc( ''' CLI display options. ''' ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    clioptions_json: __.typx.Annotated[
        __.ictrstd.JsonPresentation,
        __.ddoc.Doc( ''' CLI JSON display options. ''' ),
    ] = __.dcls.field( default_factory = __.ictrstd.JsonPresentation )
    configfile: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.ddoc.Doc( ''' Path to configuration file. ''' ),
    ] = None
    environment: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Load environment from dotfiles? ''' ),
    ] = True
    inscription: InscriptionControl = __.dcls.field(
        default_factory = InscriptionControl )

    async def __call__( self ) -> None:
        ''' Prepares session context and executes command. '''
        async with __.ctxl.AsyncExitStack( ) as exits:
            auxdata = await self.prepare( exits )
            await self.execute( auxdata )

    @__.abc.abstractmethod
    async def execute( self, auxdata: __.Globals ) -> None:
        ''' Executes command. '''
        raise NotImplementedError  # pragma: no cover

    async def prepare( self, exits: __.ctxl.AsyncExitStack ) -> __.Globals:
        ''' Prepares session context. '''
        nomargs: __.NominativeArguments = dict(
            environment = self.environment,
            inscription = self.inscription.as_control( exits ) )
        if self.configfile is not None:
            nomargs[ 'configfile' ] = self.configfile
        return await __.prepare( exits, **nomargs )


class Result( __.ictrstd.DictionaryRenderableDataclass ):
    ''' Base result. '''


def _parse_active_flavors(
    flavors: __.typx.Optional[ list[ str ] ]
) -> __.Absential[ __.ictr.ActiveFlavorsRegistry ]:
    if not flavors: return __.absent
    registry: dict[ __.typx.Optional[ str ], set[ str ] ] = { }
    for item in flavors:
        if ':' in item: address, flavor = item.split( ':', 1 )
        else: address, flavor = None, item
        registry.setdefault( address, set( ) ).add( flavor )
    return __.immut.Dictionary( {
        addr: frozenset( flavors_ )
        for addr, flavors_ in registry.items( ) } )


def _parse_trace_levels(
    levels: __.typx.Optional[ list[ str ] ]
) -> __.Absential[ __.ictr.TraceLevelsRegistry ]:
    if not levels: return __.absent
    registry: dict[ __.typx.Optional[ str ], int ] = { }
    for item in levels:
        if ':' in item: address, level_s = item.split( ':', 1 )
        else: address, level_s = None, item
        try: level = int( level_s )
        except ValueError:
            # TODO: Warn about invalid level.
            continue
        registry[ address ] = level
    return __.immut.Dictionary( registry )
