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


''' Application for configuration introspection.

    This module provides a complete CLI application for introspecting
    configuration, environment variables, and platform directories. It serves
    as both a practical utility and a comprehensive example of building CLI
    applications with the :mod:`appcore.cli` framework.

    Command-Line Interface
    ======================

    The ``appcore`` command provides three main introspection capabilities:

    Configuration Inspection
    ------------------------
    Display finalized application configuration from TOML files::

        appcore configuration                    # Default rich format
        appcore --display.presentation json configuration
        appcore --display.presentation toml configuration

    Environment Variables
    ---------------------
    Show application-specific environment variables::

        appcore environment                      # All APPCORE_* variables
        appcore --display.presentation plain environment

    Platform Directories
    ---------------------
    Display platform-specific directories for the application::

        appcore directories                      # Show all directory paths
        appcore --display.target-file dirs.txt directories

    Presentation Formats
    ====================

    Multiple output formats are supported through the presentation option:

    * ``rich`` (default) - Rich formatted output with syntax highlighting
    * ``json`` - JSON format for programmatic consumption
    * ``toml`` - TOML format matching input configuration files
    * ``plain`` - Plain text format for simple displays

    Output Routing
    ==============

    Flexible output destinations:

    Stream Routing
    --------------
    * ``--display.target-stream stdout`` (default) - Main output to stdout
    * ``--display.target-stream stderr`` - Main output to stderr
    * ``--inscription.target-stream stderr`` (default) - Logging to stderr
    * ``--inscription.target-stream stdout`` - Logging to stdout

    File Output
    -----------
    * ``--display.target-file path`` - Save main output to file
    * ``--inscription.target-file path`` - Save logging to file

    Terminal Control
    ================

    Rich terminal behavior can be controlled:

    * ``--display.colorize`` / ``--display.no-colorize`` - Control colorization
    * ``--display.assume-rich-terminal`` - Force Rich capabilities (testing)

    Implementation Architecture
    ===========================

    Command Structure
    -----------------
    * :class:`IntrospectConfigurationCommand` - Configuration introspection
    * :class:`IntrospectEnvironmentCommand` - Environment variable inspection
    * :class:`IntrospectDirectoriesCommand` - Platform directories inspection
    * :class:`Globals` - Extended state for CLI context

    Usage as Implementation Example
    ================================

    This module demonstrates comprehensive CLI application patterns:

    * Command inheritance from :class:`appcore.cli.Command`
    * Async execution with proper error handling
    * Integration with appcore preparation and configuration systems
    * File and stream output routing capabilities
    * Rich terminal integration with automatic capability detection

    The source code serves as a reference implementation for building similar
    CLI applications with the appcore framework.
'''


from . import __
from . import cli as _cli
from . import exceptions as _exceptions
from . import state as _state


try: import tyro as _tyro
except ImportError as _error:  # pragma: no cover
    raise _exceptions.DependencyAbsence( 'tyro', 'CLI' ) from _error


class ConfigurationResult( _cli.Result ):
    ''' Result from configuration introspection. '''

    configuration: dict[ str, __.typx.Any ]


class DirectoriesResult( _cli.Result ):
    ''' Result from directories introspection. '''

    directories: dict[ str, __.typx.Any ]
    # application_cache: str
    # application_data: str
    # application_state: str
    # package_data: str


class EnvironmentResult( _cli.Result ):
    ''' Result from environment introspection. '''

    environment: dict[ str, __.typx.Any ]


class IntrospectConfigurationCommand( _cli.Command ):
    ''' Shows finalized application configuration. '''

    async def __call__( self, auxdata: _state.Globals ) -> object:
        return ConfigurationResult(
            configuration = dict( auxdata.configuration ) )


class IntrospectDirectoriesCommand( _cli.Command ):
    ''' Shows application and package directories. '''

    async def __call__( self, auxdata: _state.Globals ) -> object:
        directories = {
            'application-cache': str( auxdata.provide_cache_location( ) ),
            'application-data': str( auxdata.provide_data_location( ) ),
            'application-state': str( auxdata.provide_state_location( ) ),
            'package-data': str(
                auxdata.distribution.provide_data_location( )
            ),
        }
        return DirectoriesResult( directories = directories )


class IntrospectEnvironmentCommand( _cli.Command ):
    ''' Shows application-specific environment variables. '''

    async def __call__( self, auxdata: _state.Globals ) -> object:
        name = auxdata.application.name.upper( )
        envvars = {
            k: v for k, v in __.os.environ.items( )
            if k.startswith( f"{name}_" ) }
        return EnvironmentResult( environment = envvars )


class Application( _cli.Application ):
    ''' Application for introspection of configuration. '''

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


def execute_cli( ) -> None:
    ''' Synchronous entrypoint. '''
    if (    any( arg in ( '--help', '-h' ) for arg in __.sys.argv )
        and _avoid_non_utf_terminals( )
    ): return
    configuration = ( _tyro.conf.EnumChoicesFromValues, )
    __.asyncio.run( _tyro.cli( Application, config = configuration )( ) )


def _avoid_non_utf_terminals( ) -> bool:
    ''' Avoids terminals which do not support UTF charset encoding.

        E.g., Git Bash Mintty terminals with cp1252 charset encoding.
    '''
    is_windows_cp1252 = (
        __.sys.platform == 'win32'
        and getattr( __.sys.stdout, 'encoding', '' ).lower( ) == 'cp1252' )
    if not is_windows_cp1252: return False
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
