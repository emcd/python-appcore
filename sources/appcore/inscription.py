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


''' Application inscription management.

    Logging and, potentially, debug printing.
'''
# TODO? Add structured logging support (JSON formatting for log aggregation)
# TODO? Add distributed tracing support (correlation IDs, execution IDs)
# TODO? Add metrics collection and reporting
# TODO? Add OpenTelemetry integration
# TODO: Add TOML configuration support for inscription control settings


import logging as _logging

from . import __
from . import state as _state


class Modes( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Format control modes. '''

    Null =  'null'      # deferred to external management
    Plain = 'plain'     # standard
    Rich =  'rich'      # enhanced with Rich


class Control( __.immut.DataclassObject ):
    ''' Application inscription configuration. '''

    mode: Modes = Modes.Plain
    level: __.typx.Literal[
        'debug', 'info', 'warn', 'error', 'critical'  # noqa: F821
    ] = 'info'
    target: __.typx.TextIO = __.sys.stderr


def prepare( auxdata: _state.Globals, /, control: Control ) -> None:
    ''' Prepares various scribes in a sensible manner. '''
    prepare_scribes_logging( auxdata, control )


def prepare_scribes_logging(
    auxdata: _state.Globals, control: Control
) -> None:
    ''' Prepares Python standard logging system. '''
    level_name = _discover_inscription_level_name( auxdata, control )
    level = getattr( _logging, level_name.upper( ) )
    formatter = _logging.Formatter( "%(name)s: %(message)s" )
    match control.mode:
        case Modes.Plain:
            _prepare_logging_plain( level, control.target, formatter )
        case Modes.Rich:
            _prepare_logging_rich( level, control.target, formatter )
        case _: pass


def _discover_inscription_level_name(
    auxdata: _state.Globals, control: Control
) -> str:
    application_name = ''.join(
        c.upper( ) if c.isalnum( ) else '_'
        for c in auxdata.application.name )
    for envvar_name_base in ( 'INSCRIPTION', 'LOG' ):
        envvar_name = (
            "{name}_{base}_LEVEL".format(
                base = envvar_name_base, name = application_name ) )
        if envvar_name in __.os.environ:
            return __.os.environ[ envvar_name ]
    return control.level


def _prepare_logging_plain(
    level: int, target: __.typx.TextIO, formatter: _logging.Formatter
) -> None:
    handler = _logging.StreamHandler( target )
    handler.setFormatter( formatter )
    _logging.basicConfig(
        force = True, level = level, handlers = ( handler, ) )


def _prepare_logging_rich(
    level: int, target: __.typx.TextIO, formatter: _logging.Formatter
) -> None:
    try:
        from rich.console import Console
        from rich.logging import RichHandler
    except ImportError:
        # Gracefully degrade to plain mode
        _prepare_logging_plain( level, target, formatter )
        return
    console = Console( file = target )
    handler = RichHandler(
        console = console,
        rich_tracebacks = True,
        show_time = True,
        show_path = False
    )
    handler.setFormatter( formatter )
    _logging.basicConfig(
        force = True, level = level, handlers = ( handler, ) )
