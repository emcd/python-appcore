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

    Logging and diagnostic printing.

    Configuration precedence (highest first):

    1. Explicit ``Control`` fields (``active_flavors``, ``trace_levels``)
    2. Application-specific environment (``{APP}_ACTIVE_FLAVORS``,
       ``{APP}_TRACE_LEVELS``)
    3. Ictr environment (``ICTR_ACTIVE_FLAVORS``, ``ICTR_TRACE_LEVELS``)
    4. Defaults (level-derived flavors; ictr built-in trace defaults)
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

# Flavor base, active at every level: failures always print, and the
# semantic flavors sit outside the level system (active means print).
_ICTR_ERROR_FAMILY_FLAVORS = frozenset( {
    'error', 'errorx', 'abort', 'abortx',
} )
_ICTR_SEMANTIC_FLAVORS = frozenset( {
    'future', 'success', 'advice',
} )


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

    active_flavors: __.Absential[ __.ictr.ActiveFlavorsArgument ] = __.absent
    ictr_alias: __.Absential[ str ] = __.absent
    install_ictr: __.Absential[ bool ] = __.absent
    level: Levels = 'info'
    mode: Presentations = Presentations.Plain
    target: Target = __.sys.stderr
    trace_levels: __.Absential[ __.ictr.TraceLevelsArgument ] = __.absent


def prepare( auxdata: _state.Globals, /, control: Control ) -> None:
    ''' Prepares various scribes in a sensible manner. '''
    target = _process_target( auxdata, control )
    _prepare_scribes_logging( auxdata, control, target )
    _prepare_scribes_ictr( auxdata, control, target )


def _application_name_normalized( auxdata: _state.Globals ) -> str:
    return ''.join(
        c.upper( ) if c.isalnum( ) else '_'
        for c in auxdata.application.name )


def _derive_ictr_flavors( level_name: str ) -> frozenset[ str ]:
    ''' Maps inscription level name to default active ictr flavors. '''
    base = _ICTR_ERROR_FAMILY_FLAVORS | _ICTR_SEMANTIC_FLAVORS
    match level_name.lower( ):
        case 'debug':
            return base | frozenset( { 'note', 'monition' } )
        case 'info':
            return base | frozenset( { 'note' } )
        case 'warn' | 'warning':
            return base | frozenset( { 'monition' } )
        case _:
            return base


def _discover_inscription_level_name(
    auxdata: _state.Globals, control: Control
) -> str:
    application_name = _application_name_normalized( auxdata )
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


def _prepare_scribes_ictr(
    auxdata: _state.Globals, control: Control, /, target: __.typx.TextIO
) -> __.ictr.Dispatcher:
    ''' Configures ictr dispatcher; installs into builtins when enabled. '''
    active_flavors, evname_active_flavors = (
        _resolve_ictr_active_flavors( auxdata, control ) )
    trace_levels, evname_trace_levels = (
        _resolve_ictr_trace_levels( auxdata, control ) )
    printer_factories = _produce_ictr_generalcfg( control, target )
    nomargs: dict[ str, __.typx.Any ] = dict(
        active_flavors = active_flavors,
        printer_factories = printer_factories,
        trace_levels = trace_levels,
        evname_active_flavors = evname_active_flavors,
        evname_trace_levels = evname_trace_levels )
    do_install = (
        True if __.is_absent( control.install_ictr )
        else control.install_ictr )
    if do_install:
        alias = (
            __.ictr.builtins_alias_default
            if __.is_absent( control.ictr_alias )
            else control.ictr_alias )
        return __.ictr.install( alias = alias, **nomargs )
    return __.ictr.produce_dispatcher( **nomargs )


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


def _produce_ictr_generalcfg(
    control: Control, target: __.typx.TextIO
) -> __.ictr.PrinterFactoriesArgument:
    ''' Produces ictr printer factories for the presentation mode.

        Plain and Null modes never colorize, so ANSI sequences are always
        stripped. Rich mode uses the default factory so TTY detection and
        ``NO_COLOR`` remain with ictr.
    '''
    match control.mode:
        case Presentations.Rich:
            if isinstance( target, __.io.TextIOBase ):
                return (
                    __.ictr.produce_printer_factory_default( target ),
                )
        case _: pass
    return (
        __.ictr.produce_printer_factory_default(
            target, colorize = False ),
    )


def _resolve_ictr_active_flavors(
    auxdata: _state.Globals, control: Control
) -> tuple[
    __.ictr.ActiveFlavorsArgument,
    __.ictr.EvnActiveFlavorsArgument,
]:
    ''' Resolves active flavors with Control > app env > ictr env > level. '''
    if not __.is_absent( control.active_flavors ):
        return control.active_flavors, None
    app_evname = (
        f"{_application_name_normalized( auxdata )}_ACTIVE_FLAVORS" )
    if app_evname in __.os.environ:
        return __.absent, app_evname
    if 'ICTR_ACTIVE_FLAVORS' in __.os.environ:
        return __.absent, __.absent
    level_name = _discover_inscription_level_name( auxdata, control )
    return _derive_ictr_flavors( level_name ), None


def _resolve_ictr_trace_levels(
    auxdata: _state.Globals, control: Control
) -> tuple[
    __.ictr.TraceLevelsArgument,
    __.ictr.EvnTraceLevelsArgument,
]:
    ''' Resolves trace levels with Control > app env > ictr env > defaults. '''
    if not __.is_absent( control.trace_levels ):
        return control.trace_levels, None
    app_evname = (
        f"{_application_name_normalized( auxdata )}_TRACE_LEVELS" )
    if app_evname in __.os.environ:
        return __.absent, app_evname
    return __.absent, __.absent
