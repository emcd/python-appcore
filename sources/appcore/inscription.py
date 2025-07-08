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


''' Application logging configuration and management. '''
# TODO: Add structured logging support (JSON formatting for log aggregation)
# TODO: Add distributed tracing support (correlation IDs, execution IDs)
# TODO: Add metrics collection and reporting
# TODO: Add OpenTelemetry integration


from . import __
import logging as _logging


class Modes( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Possible modes for logging output. '''

    Null = 'null'  # minimal logging setup
    Plain = 'plain'  # standard Python logging
    Rich = 'rich'  # enhanced logging with Rich (graceful degradation)


class Control( __.immut.DataclassObject ):
    ''' Application logging configuration. '''

    mode: Modes = Modes.Plain
    level: __.typx.Literal[
        'debug', 'info', 'warn', 'error', 'critical'  # noqa: F821
    ] = 'info'
    target: __.Absential[
        __.typx.Union[ __.Path, __.typx.TextIO ]
    ] = __.absent


def prepare( control: Control ) -> None:
    ''' Configures application logging based on control settings. '''
    prepare_scribe_logging( control )


def prepare_scribe_logging( control: Control ) -> None:
    ''' Configures Python logging based on control settings. '''
    level_name = _discover_inscription_level_name( control )
    level = getattr( _logging, level_name.upper( ) )
    _logging.basicConfig( level = level, force = True )
    match control.mode:
        case Modes.Null:
            _configure_null_mode( level, control.target )
        case Modes.Plain:
            _configure_plain_mode( level, control.target )
        case Modes.Rich:
            _configure_rich_mode( level, control.target )


def _configure_null_mode(
    level: int,
    target: __.Absential[ __.typx.Union[ __.Path, __.typx.TextIO ] ]
) -> None:
    ''' Configures minimal logging setup with basic handler. '''
    handler = _create_handler( target )
    handler.setLevel( level )
    formatter = _logging.Formatter( '%(levelname)s: %(message)s' )
    handler.setFormatter( formatter )
    _logging.getLogger( ).addHandler( handler )


def _configure_plain_mode(
    level: int,
    target: __.Absential[ __.typx.Union[ __.Path, __.typx.TextIO ] ]
) -> None:
    ''' Configures standard Python logging with optional target. '''
    handler = _create_handler( target )
    handler.setLevel( level )
    formatter = _logging.Formatter( '%(levelname)s: %(message)s' )
    handler.setFormatter( formatter )
    _logging.getLogger( ).addHandler( handler )


def _configure_rich_mode(
    level: int,
    target: __.Absential[ __.typx.Union[ __.Path, __.typx.TextIO ] ]
) -> None:
    ''' Configures Rich logging with graceful degradation to plain mode. '''
    try:
        from rich.console import Console  # type: ignore
        from rich.logging import RichHandler  # type: ignore
    except ImportError:
        # Gracefully degrade to plain mode
        _configure_plain_mode( level, target )
        return
    if __.is_absent( target ):
        console = Console( stderr = True )  # type: ignore
    elif isinstance( target, __.Path ):
        # Rich doesn't support file paths directly, fall back to plain
        _configure_plain_mode( level, target )
        return
    else:
        console = Console( file = target )  # type: ignore
    handler = RichHandler(  # type: ignore
        console = console,
        rich_tracebacks = True,
        show_time = True,
        show_path = False
    )
    handler.setLevel( level )  # type: ignore
    formatter = _logging.Formatter( '%(message)s' )
    handler.setFormatter( formatter )  # type: ignore
    _logging.getLogger( ).addHandler( handler )  # type: ignore


def _create_handler(
    target: __.Absential[ __.typx.Union[ __.Path, __.typx.TextIO ] ]
) -> _logging.Handler:
    ''' Creates appropriate logging handler based on target. '''
    if __.is_absent( target ):
        return _logging.StreamHandler( )
    if isinstance( target, __.Path ):
        return _logging.FileHandler( target )
    return _logging.StreamHandler( target )


def _discover_inscription_level_name( control: Control ) -> str:
    ''' Discovers logging level from control or environment variables. '''
    # Check environment variables for level override
    for envvar_name_base in ( 'INSCRIPTION', 'LOG' ):
        envvar_name = (
            "{name}_{base}_LEVEL".format(
                base = envvar_name_base,
                name = __.package_name.upper( ) ) )
        if envvar_name in __.os.environ:
            return __.os.environ[ envvar_name ]
    return control.level


