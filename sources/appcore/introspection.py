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


''' Application for configuration introspection. '''


import json as _json

from . import __
from . import cli as _cli
from . import exceptions as _exceptions
from . import state as _state


try: import rich.console as _rich_console
except ImportError as _error:
    raise _exceptions.DependencyAbsence( 'rich', 'CLI' ) from _error
try: import tomli_w as _tomli_w
except ImportError as _error:
    raise _exceptions.DependencyAbsence( 'tomli-w', 'CLI' ) from _error
try: import tyro as _tyro
except ImportError as _error:
    raise _exceptions.DependencyAbsence( 'tyro', 'CLI' ) from _error


class Presentations( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Presentation mode (format) for CLI output. '''

    Json    = 'json'
    Plain   = 'plain'
    Rich    = 'rich'
    Toml    = 'toml'


class DisplayOptions( _cli.DisplayOptions ):
    ''' Display options, including presentation mode. '''

    presentation: __.typx.Annotated[
        Presentations,
        _tyro.conf.arg( help = "Output presentation mode (format)." ),
    ] = Presentations.Rich

    async def render( self, data: __.typx.Any ) -> None:
        ''' Renders data according to display options. '''
        async with __.ctxl.AsyncExitStack( ) as exits:
            target = await self.provide_stream( exits )
            match self.presentation:
                case Presentations.Json:
                    content = _json.dumps(
                        data, indent = 2, ensure_ascii = False )
                    print( content, file = target )
                case Presentations.Plain:
                    self._render_plain( data, target )
                case Presentations.Rich:
                    if self.determine_colorization( target ):
                        self._render_rich( data, target)
                    else: self._render_plain( data, target )
                case Presentations.Toml:
                    content = _tomli_w.dumps( data )
                    print( content, file = target )

    def _render_plain(
        self, objct: __.typx.Any, target: __.typx.TextIO
    ) -> None:
        ''' Renders object in plain text format. '''
        if isinstance( objct, __.cabc.Mapping ):
            for key, value in objct.items( ):  # pyright: ignore
                print( f"{key}: {value}", file = target )
        else: print( objct, file = target )

    def _render_rich(
        self, objct: __.typx.Any, target: __.typx.TextIO
    ) -> None:
        ''' Renders object using Rich formatting. '''
        console = _rich_console.Console(
            file = target,
            color_system = 'auto' if self.colorize else None )
        if isinstance( objct, __.cabc.Mapping ):
            console.print( objct )
        else: console.print( str( objct ) )


class ApplicationGlobals( _state.Globals ):
    ''' Includes display options. '''

    display: DisplayOptions = __.dcls.field( default_factory = DisplayOptions )


class IntrospectConfigurationCommand( _cli.Command ):
    ''' Shows finalized application configuration. '''

    async def execute( self, auxdata: _state.Globals ) -> None:
        if not isinstance( auxdata, ApplicationGlobals ):
            raise _exceptions.ContextInvalidity( auxdata )
        data = dict( auxdata.configuration )
        await auxdata.display.render( data )


class IntrospectDirectoriesCommand( _cli.Command ):
    ''' Shows application and package directories. '''

    async def execute( self, auxdata: _state.Globals ):
        if not isinstance( auxdata, ApplicationGlobals ):
            raise _exceptions.ContextInvalidity( auxdata )
        directories = {
            'application-cache': str( auxdata.provide_cache_location( ) ),
            'application-data': str( auxdata.provide_data_location( ) ),
            'application-state': str( auxdata.provide_state_location( ) ),
            'package-data': str(
                auxdata.distribution.provide_data_location( )
            ),
        }
        await auxdata.display.render( directories )


class IntrospectEnvironmentCommand( _cli.Command ):
    ''' Shows application-specific environment variables. '''

    async def execute( self, auxdata: _state.Globals ) -> None:
        if not isinstance( auxdata, ApplicationGlobals ):
            raise _exceptions.ContextInvalidity( auxdata )
        name = auxdata.application.name.upper( )
        envvars = {
            k: v for k, v in __.os.environ.items( )
            if k.startswith( f"{name}_" ) }
        await auxdata.display.render( envvars )


class Application( _cli.Application ):
    ''' Application for introspection of configuration. '''

    display: DisplayOptions = __.dcls.field( default_factory = DisplayOptions )
    command: __.typx.Union[
        __.typx.Annotated[
            IntrospectConfigurationCommand,
            _tyro.conf.subcommand( 'configuration', prefix_name = False ),
        ],
        __.typx.Annotated[
            IntrospectEnvironmentCommand,
            _tyro.conf.subcommand( 'environment', prefix_name = False ),
        ],
        __.typx.Annotated[
            IntrospectDirectoriesCommand,
            _tyro.conf.subcommand( 'directories', prefix_name = False ),
        ],
    ] = __.dcls.field( default_factory = IntrospectConfigurationCommand )

    async def execute( self, auxdata: _state.Globals ) -> None:
        await self.command( auxdata )

    async def prepare( self, exits: __.ctxl.AsyncExitStack ) -> _state.Globals:
        auxdata_base = await super( ).prepare( exits )
        nomargs = {
            field.name: getattr( auxdata_base, field.name )
            for field in __.dcls.fields( auxdata_base )
            if not field.name.startswith( '_' ) }
        return ApplicationGlobals( display = self.display, **nomargs )


def execute_cli( ) -> None:
    ''' Synchronous entrypoint. '''
    if (
        any( arg in ( '--help', '-h' ) for arg in __.sys.argv )
        and _handle_windows_unicode_help_limitation( )
    ):
        return
    configuration = ( _tyro.conf.EnumChoicesFromValues, )
    __.asyncio.run( _tyro.cli( Application, config = configuration )( ) )


def _handle_windows_unicode_help_limitation( ) -> bool:
    ''' Handles Git Bash/Mintty terminals with cp1252 encoding limitations.

    Returns True if help was displayed with mitigation, False if normal
    help should proceed.
    '''
    is_windows_cp1252 = (
        __.sys.platform == 'win32'
        and getattr( __.sys.stdout, 'encoding', '' ).lower( ) == 'cp1252' )
    if not is_windows_cp1252:
        return False
    encoding = getattr( __.sys.stdout, 'encoding', 'unknown' )
    message = (
        f"Help display is not available in this terminal "
        f"(encoding: {encoding}).\n"
        "Unicode characters required by the help system are not supported.\n\n"
        "To view help, try running this command in:\n"
        "- Windows Terminal\n"
        "- PowerShell\n"
        "- Command Prompt with UTF-8 support\n"
        "- WSL\n\n"
        "For basic usage: appcore <subcommand>\n"
        "Available subcommands: configuration, environment, directories" )
    print( message, file = __.sys.stderr )
    raise SystemExit( 0 )
