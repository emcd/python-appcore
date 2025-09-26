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


Levels: __.typx.TypeAlias = __.typx.Literal[
    'debug', 'info', 'warn', 'error', 'critical' ]


class Presentations( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Scribe presentation modes. '''

    Null =  'null'      # deferred to external management
    Plain = 'plain'     # standard
    Rich =  'rich'      # enhanced with Rich

Modes = Presentations  # deprecated


class TargetModes( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Target file mode control. '''

    Append =    'append'
    Truncate =  'truncate'


class TargetDescriptor( __.immut.DataclassObject ):
    ''' Descriptor for file-based inscription targets. '''

    location: bytes | str | __.os.PathLike[ bytes ] | __.os.PathLike[ str ]
    mode: TargetModes = TargetModes.Truncate
    codec: str = 'utf-8'


Target: __.typx.TypeAlias = __.typx.Union[
    __.io.TextIOWrapper, __.typx.TextIO, TargetDescriptor ]


class Control( __.immut.DataclassObject ):
    ''' Application inscription configuration. '''

    mode: Presentations = Presentations.Plain
    level: Levels = 'info'
    target: Target = __.sys.stderr


def prepare( auxdata: _state.Globals, /, control: Control ) -> None:
    ''' Prepares various scribes in a sensible manner. '''
    target = _process_target( auxdata, control )
    _prepare_scribes_logging( auxdata, control, target )


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
        # Gracefully degrade to plain mode.
        _prepare_logging_plain( level, target, formatter )
        return
    console = Console( file = target )
    handler = RichHandler(
        console = console,
        rich_tracebacks = True,
        show_path = False, show_time = True )
    handler.setFormatter( formatter )
    _logging.basicConfig(
        force = True, level = level, handlers = ( handler, ) )


def _prepare_scribes_logging(
    auxdata: _state.Globals, control: Control, /, target: __.typx.TextIO
) -> None:
    level_name = _discover_inscription_level_name( auxdata, control )
    level = getattr( _logging, level_name.upper( ) )
    formatter = _logging.Formatter( "%(name)s: %(message)s" )
    match control.mode:
        case Presentations.Plain:
            _prepare_logging_plain( level, target, formatter )
        case Presentations.Rich:
            _prepare_logging_rich( level, target, formatter )
        case _: pass


def _process_target(
    auxdata: _state.Globals, control: Control
) -> __.typx.TextIO:
    target = control.target
    if isinstance( target, __.typx.TextIO ): # pragma: no cover
        return target
    if isinstance( target, ( __.io.StringIO, __.io.TextIOWrapper ) ):
        return target
    location = target.location
    if isinstance( location, __.os.PathLike ):
        location = location.__fspath__( )
    if isinstance( location, bytes ):
        location = location.decode( )
    location = __.Path( location )
    location.parent.mkdir( exist_ok = True, parents = True )
    mode = 'w' if target.mode is TargetModes.Truncate else 'a'
    return auxdata.exits.enter_context( open(
        location, mode = mode, encoding = target.codec ) )
