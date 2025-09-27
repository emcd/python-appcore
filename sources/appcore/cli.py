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

    This module provides the core infrastructure for building command-line
    interfaces. It offers a comprehensive framework for creating CLI
    applications with rich presentation options, flexible output routing, and
    integrated logging capabilities.

    Key Components
    ==============

    Command Framework
    -----------------
    * :class:`Command` - Abstract base class for CLI command implementations
    * :class:`Application` dataclass for command-line application configuration
    * Rich integration with tyro for automatic argument parsing and help
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

        class MyGlobals( state.Globals ):
            display: MyDisplayOptions

        class StatusCommand( cli.Command ):
            async def execute( self, auxdata: state.Globals ) -> None:
                if isinstance( auxdata, MyGlobals ):
                    format_val = auxdata.display.format
                    print( f"Status: Running (format: {format_val})" )

        class InfoCommand( cli.Command ):
            async def execute( self, auxdata: state.Globals ) -> None:
                print( f"App: {auxdata.application.name}" )

        class MyApplication( cli.Application ):
            display: MyDisplayOptions = __.dcls.field(
                default_factory = MyDisplayOptions )
            command: __.typx.Union[
                __.typx.Annotated[
                    StatusCommand,
                    _tyro.conf.subcommand( 'status', prefix_name = False ),
                ],
                __.typx.Annotated[
                    InfoCommand,
                    _tyro.conf.subcommand( 'info', prefix_name = False ),
                ],
            ] = __.dcls.field( default_factory = StatusCommand )

            async def execute( self, auxdata: state.Globals ) -> None:
                await self.command( auxdata )

            async def prepare( self, exits ) -> state.Globals:
                auxdata_base = await super( ).prepare( exits )
                return MyGlobals(
                    display = self.display, **auxdata_base.__dict__ )
'''


from . import __
from . import exceptions as _exceptions
from . import inscription as _inscription
from . import preparation as _preparation
from . import state as _state


try: import rich
except ImportError as _error:  # pragma: no cover
    raise _exceptions.DependencyAbsence( 'rich', 'CLI' ) from _error
else: del rich
try: import tomli_w
except ImportError as _error:  # pragma: no cover
    raise _exceptions.DependencyAbsence( 'tomli-w', 'CLI' ) from _error
else: del tomli_w
try: import tyro as _tyro
except ImportError as _error:  # pragma: no cover
    raise _exceptions.DependencyAbsence( 'tyro', 'CLI' ) from _error


_DisplayTargetMutex = _tyro.conf.create_mutex_group( required = False )
_InscriptionTargetMutex = _tyro.conf.create_mutex_group( required = False )


class TargetStreams( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Target stream selection. '''

    Stdout  = 'stdout'
    Stderr  = 'stderr'


class DisplayOptions( __.immut.DataclassObject ):
    ''' Standardized display configuration for CLI applications.

    Example::

        class MyDisplayOptions( DisplayOptions ):
            format: str = 'table'
            compact: bool = False
    '''

    colorize: __.typx.Annotated[
        bool,
        _tyro.conf.arg(
            aliases = ( '--ansi-sgr', ),
            help = "Enable colored output and terminal formatting." ),
    ] = True
    target_file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        _DisplayTargetMutex,
        _tyro.conf.DisallowNone,
        _tyro.conf.arg( help = "Render output to specified file." ),
    ] = None
    target_stream: __.typx.Annotated[
        __.typx.Optional[ TargetStreams ],
        _DisplayTargetMutex,
        _tyro.conf.DisallowNone,
        _tyro.conf.arg( help = "Render output on stdout or stderr." ),
    ] = TargetStreams.Stdout
    assume_rich_terminal: __.typx.Annotated[
        bool,
        _tyro.conf.arg(
            aliases = ( '--force-tty', ),
            help = "Assume Rich terminal capabilities regardless of TTY." ),
    ] = False

    def determine_colorization( self, stream: __.typx.TextIO ) -> bool:
        ''' Determines whether to use colorized output. '''
        if self.assume_rich_terminal: return self.colorize
        if not self.colorize: return False
        if __.os.environ.get( 'NO_COLOR' ): return False
        return hasattr( stream, 'isatty' ) and stream.isatty( )

    async def provide_stream(
        self, exits: __.ctxl.AsyncExitStack
    ) -> __.typx.TextIO:
        ''' Provides target stream from options. '''
        if self.target_file is not None:
            target_location = self.target_file.resolve( )
            target_location.parent.mkdir( exist_ok = True, parents = True )
            return exits.enter_context( target_location.open( 'w' ) )
        target_stream = self.target_stream or TargetStreams.Stderr
        match target_stream:
            case TargetStreams.Stdout: return __.sys.stdout
            case TargetStreams.Stderr: return __.sys.stderr


class InscriptionControl( __.immut.DataclassObject ):
    ''' Inscription (logging, debug prints) control. '''

    level: __.typx.Annotated[
        _inscription.Levels, _tyro.conf.arg( help = "Log verbosity." )
    ] = 'info'
    presentation: __.typx.Annotated[
        _inscription.Presentations,
        _tyro.conf.arg( help = "Log presentation mode (format)." ),
    ] = _inscription.Presentations.Plain
    target_file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        _InscriptionTargetMutex,
        _tyro.conf.DisallowNone,
        _tyro.conf.arg( help = "Log to specified file." ),
    ] = None
    target_stream: __.typx.Annotated[
        __.typx.Optional[ TargetStreams ],
        _InscriptionTargetMutex,
        _tyro.conf.DisallowNone,
        _tyro.conf.arg( help = "Log to stdout or stderr." ),
    ] = TargetStreams.Stderr

    def as_control(
        self, exits: __.ctxl.AsyncExitStack
    ) -> _inscription.Control:
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
        return _inscription.Control(
            mode = self.presentation,
            level = self.level,
            target = target_stream )


class Command(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Standard interface for command implementations.

    Example::

        class StatusCommand( Command ):
            async def execute( self, auxdata: state.Globals ) -> None:
                print( f"Application: {auxdata.application.name}" )
    '''

    async def __call__( self, auxdata: _state.Globals ) -> None:
        ''' Prepares session context and executes command. '''
        await self.execute( await self.prepare( auxdata ) )

    @__.abc.abstractmethod
    async def execute( self, auxdata: _state.Globals ) -> None:
        ''' Executes command. '''
        raise NotImplementedError  # pragma: no cover

    async def prepare( self, auxdata: _state.Globals ) -> _state.Globals:
        ''' Prepares session context. '''
        return auxdata


class Application(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Common infrastructure and standard interface for applications.

    Example::

        class MyApplication( Application ):
            display: DisplayOptions = __.dcls.field(
                default_factory = DisplayOptions )

            async def execute( self, auxdata: state.Globals ) -> None:
                print( f"Application: {auxdata.application.name}" )
    '''

    configfile: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        _tyro.conf.arg( help = "Path to configuration file." ),
    ] = None
    environment: __.typx.Annotated[
        bool, _tyro.conf.arg( help = "Load environment from dotfiles?" )
    ] = True
    inscription: InscriptionControl = __.dcls.field(
        default_factory = InscriptionControl )

    async def __call__( self ) -> None:
        ''' Prepares session context and executes command. '''
        async with __.ctxl.AsyncExitStack( ) as exits:
            auxdata = await self.prepare( exits )
            await self.execute( auxdata )

    @__.abc.abstractmethod
    async def execute( self, auxdata: _state.Globals ) -> None:
        ''' Executes command. '''
        raise NotImplementedError  # pragma: no cover

    async def prepare( self, exits: __.ctxl.AsyncExitStack ) -> _state.Globals:
        ''' Prepares session context. '''
        nomargs: __.NominativeArguments = dict(
            environment = self.environment,
            inscription = self.inscription.as_control( exits ) )
        if self.configfile is not None:
            nomargs[ 'configfile' ] = self.configfile
        return await _preparation.prepare( exits, **nomargs )
