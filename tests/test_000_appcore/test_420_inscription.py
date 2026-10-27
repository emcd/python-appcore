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


''' Application inscription management tests. '''


import io
import logging
import sys

from unittest.mock import patch

import pytest

from appcore import __
from appcore import inscription as module

from .fixtures import create_globals_with_temp_dirs


def test_100_modes_enum_values( ):
    ''' Modes enum has expected string values. '''
    assert module.Modes.Null.value == 'null'
    assert module.Modes.Plain.value == 'plain'
    assert module.Modes.Rich.value == 'rich'


def test_110_control_creation_defaults( ):
    ''' Control creates with default values. '''
    control = module.Control( )
    assert control.mode == module.Modes.Plain
    assert control.level == 'info'
    assert control.target == sys.stderr
    assert __.is_absent( control.active_flavors )
    assert __.is_absent( control.ictr_alias )
    assert __.is_absent( control.install_ictr )
    assert __.is_absent( control.trace_levels )


def test_120_control_creation_custom_values( ):
    ''' Control accepts custom mode, level, and target. '''
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Rich,
        level = 'debug',
        target = target_stream )
    assert control.mode == module.Modes.Rich
    assert control.level == 'debug'
    assert control.target == target_stream


def test_130_control_immutability( ):
    ''' Control instances are immutable. '''
    control = module.Control( )
    # Should not be able to modify fields after creation
    try:
        control.mode = module.Modes.Rich  # type: ignore
        raise AssertionError( "Should not be able to modify immutable field" )
    except ( AttributeError, TypeError ):
        pass  # Expected


def test_140_control_equality( ):
    ''' Control instances with same data are equal. '''
    control1 = module.Control(
        mode = module.Modes.Rich,
        level = 'debug' )
    control2 = module.Control(
        mode = module.Modes.Rich,
        level = 'debug' )
    assert control1 == control2


def test_150_control_inequality( ):
    ''' Control instances with different data are not equal. '''
    control1 = module.Control( mode = module.Modes.Plain )
    control2 = module.Control( mode = module.Modes.Rich )
    assert control1 != control2


def test_200_prepare_with_null_mode( ):
    ''' Null inscription mode skips logging configuration. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    control = module.Control(
        mode = module.Modes.Null, install_ictr = False )
    # Should not raise an error or configure logging
    module.prepare( globals_dto, control )


def test_210_prepare_with_plain_mode( ):
    ''' Plain inscription mode configures standard logging. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Plain,
        level = 'debug',
        target = target_stream, install_ictr = False )
    # Should not raise an error
    module.prepare( globals_dto, control )


def test_220_prepare_with_rich_mode_without_rich( ):
    ''' Rich inscription mode degrades gracefully without Rich. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Rich,
        target = target_stream, install_ictr = False )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', {
        'rich.console': None,
        'rich.logging': None
    } ):
        # Should not raise an error (graceful fallback)
        module.prepare( globals_dto, control )


def test_230_prepare_with_stream_target( ):
    ''' Inscription accepts a custom stream target. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Plain,
        target = target_stream, install_ictr = False )
    # Should not raise an error
    module.prepare( globals_dto, control )


def test_300_discover_inscription_level_name_default( ):
    ''' Level discovery defaults to control level when no override. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    control = module.Control( level = 'debug' )
    level_name = module._discover_inscription_level_name(
        globals_dto, control )
    assert level_name == 'debug'


def test_310_discover_inscription_level_name_with_inscription_env( ):
    ''' INSCRIPTION environment variable overrides control level setting. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'TEST_APP_INSCRIPTION_LEVEL': 'error'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'error'


def test_320_discover_inscription_level_name_with_log_env( ):
    ''' LOG environment variable provides alternative level override. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, { 'TEST_APP_LOG_LEVEL': 'warning' } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'warning'


def test_330_discover_inscription_level_name_precedence( ):
    ''' Level discovery gives INSCRIPTION env var precedence. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'TEST_APP_INSCRIPTION_LEVEL': 'debug',
        'TEST_APP_LOG_LEVEL': 'error'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'debug'


def test_340_discover_inscription_level_name_normalizes_app_name( ):
    ''' Level discovery normalizes app name for env vars. '''
    globals_dto, _ = create_globals_with_temp_dirs(
        app_name = 'my-awesome app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'MY_AWESOME_APP_INSCRIPTION_LEVEL': 'debug'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'debug'


def test_350_discover_inscription_level_name_robust_normalization( ):
    ''' Level discovery handles special characters robustly. '''
    globals_dto, _ = create_globals_with_temp_dirs(
        app_name = 'my@app-2.0! (beta)' )
    control = module.Control( level = 'info' )
    # The expected normalized name: MY_APP_2_0___BETA_
    with patch.dict( __.os.environ, {
        'MY_APP_2_0___BETA__INSCRIPTION_LEVEL': 'warning'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'warning'


def test_400_prepare_scribes_logging_plain( ):
    ''' Plain logging can be configured. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Plain,
        level = 'debug',
        target = target_stream, install_ictr = False )
    # Should not raise an error
    module._prepare_scribes_logging(
        globals_dto, control, target = target_stream )


def test_410_prepare_scribes_logging_rich_fallback( ):
    ''' Rich logging falls back to plain logging, when unavailable. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Rich,
        target = target_stream, install_ictr = False )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', {
        'rich.console': None,
        'rich.logging': None
    } ):
        # Should not raise an error (graceful fallback)
        module._prepare_scribes_logging(
            globals_dto, control, target = target_stream )


def test_420_prepare_scribes_logging_null( ):
    ''' Null logging can be configured. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    control = module.Control(
        mode = module.Modes.Null, install_ictr = False )
    # Should not raise an error or configure logging
    module._prepare_scribes_logging(
        globals_dto, control, target = io.StringIO( ) )


def test_500_prepare_logging_plain( ):
    ''' Plain logging configures root logger. '''
    target_stream = io.StringIO( )
    formatter = logging.Formatter( "%(name)s: %(message)s" )
    # Should not raise an error
    module._prepare_logging_plain( logging.DEBUG, target_stream, formatter )


def test_510_prepare_logging_rich_fallback( ):
    ''' Rich logging gracefully falls back when import fails. '''
    target_stream = io.StringIO( )
    formatter = logging.Formatter( "%(name)s: %(message)s" )
    # Mock the import to raise ImportError
    with patch( 'builtins.__import__', side_effect = ImportError( ) ):
        # Should not raise an error (graceful fallback)
        module._prepare_logging_rich( logging.INFO, target_stream, formatter )


def test_520_prepare_logging_rich_available( ):
    ''' Rich logging configures when Rich is available. '''
    import importlib.util
    target_stream = io.StringIO( )
    formatter = logging.Formatter( "%(name)s: %(message)s" )
    # Check if rich is available using importlib
    if ( importlib.util.find_spec( 'rich.console' ) is not None and
         importlib.util.find_spec( 'rich.logging' ) is not None ):
        # Rich is available, test the rich path
        module._prepare_logging_rich( logging.DEBUG, target_stream, formatter )
        # Should have configured logging without error
    else:
        # Rich not available in test environment, skip this test
        pytest.skip( "Rich not available in test environment" )


def test_600_target_descriptor_created_with_defaults( ):
    ''' TargetDescriptor uses truncate mode and UTF-8 encoding by default. '''
    descriptor = module.TargetDescriptor( location = "test.log" )
    assert descriptor.location == "test.log"
    assert descriptor.mode == module.TargetModes.Truncate
    assert descriptor.codec == 'utf-8'


def test_610_target_descriptor_accepts_custom_settings( ):
    ''' TargetDescriptor accepts custom mode and encoding. '''
    descriptor = module.TargetDescriptor(
        location = "test.log",
        mode = module.TargetModes.Append,
        codec = 'latin-1'
    )
    assert descriptor.location == "test.log"
    assert descriptor.mode == module.TargetModes.Append
    assert descriptor.codec == 'latin-1'


def test_620_target_modes_provide_append_and_truncate( ):
    ''' TargetModes enum provides append and truncate options. '''
    assert module.TargetModes.Append.value == 'append'
    assert module.TargetModes.Truncate.value == 'truncate'


def test_630_control_accepts_target_descriptor( ):
    ''' Control accepts TargetDescriptor for file-based logging. '''
    descriptor = module.TargetDescriptor( location = "test.log" )
    control = module.Control( target = descriptor )
    assert control.target == descriptor


def test_640_textio_streams_used_directly( ):
    ''' TextIO streams are used directly without conversion. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( target = target_stream, install_ictr = False )
    result = module._process_target( globals_dto, control )
    assert result is target_stream


def test_650_stringio_used_directly( ):
    ''' StringIO instances are used directly without conversion. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( target = target_stream, install_ictr = False )
    result = module._process_target( globals_dto, control )
    assert result is target_stream


def test_660_string_location_creates_log_file( fs ):
    ''' String file paths create log files when processed. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    descriptor = module.TargetDescriptor( location = str( log_path ) )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    assert fs.exists( str( log_path ) )


def test_670_pathlike_location_creates_log_file( fs ):
    ''' PathLike objects create log files when processed. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    descriptor = module.TargetDescriptor( location = log_path )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    assert fs.exists( str( log_path ) )


def test_680_bytes_location_creates_log_file( fs ):
    ''' Bytes file paths create log files when processed. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    descriptor = module.TargetDescriptor(
        location = str( log_path ).encode( ) )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    assert fs.exists( str( log_path ) )


def test_690_append_mode_preserves_existing_content( fs ):
    ''' Append mode preserves existing file content. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    fs.create_file( str( log_path ), contents = "existing content\n" )
    descriptor = module.TargetDescriptor(
        location = str( log_path ),
        mode = module.TargetModes.Append
    )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    content = fs.get_object( str( log_path ) ).contents
    assert "existing content" in content


def test_700_truncate_mode_clears_existing_content( fs ):
    ''' Truncate mode clears existing file content. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    fs.create_file( str( log_path ), contents = "existing content\n" )
    descriptor = module.TargetDescriptor(
        location = str( log_path ),
        mode = module.TargetModes.Truncate
    )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    content = fs.get_object( str( log_path ) ).contents
    assert "existing content" not in content


def test_710_parent_directories_created_automatically( fs ):
    ''' Parent directories are created automatically for log files. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "logs" / "subdir" / "test.log"
    descriptor = module.TargetDescriptor( location = str( log_path ) )
    control = module.Control( target = descriptor, install_ictr = False )
    module.prepare( globals_dto, control )
    assert fs.exists( str( log_path ) )
    assert fs.exists( str( log_path.parent ) )
    assert fs.exists( str( log_path.parent.parent ) )


def test_720_pathlike_object_converted_to_path( fs ):
    ''' PathLike objects are converted to Path instances for processing. '''
    from pathlib import Path
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    log_path = temp_dir / "test.log"
    path_obj = Path( str( log_path ) )
    descriptor = module.TargetDescriptor( location = path_obj )
    control = module.Control( target = descriptor, install_ictr = False )
    module._process_target( globals_dto, control )
    assert fs.exists( str( log_path ) )


def test_800_derive_ictr_flavors_debug( ):
    ''' Debug level activates note, monition, error-family, and semantic. '''
    flavors = module._derive_ictr_flavors( 'debug' )
    assert 'note' in flavors
    assert 'monition' in flavors
    assert 'error' in flavors
    assert 'errorx' in flavors
    assert 'abort' in flavors
    assert 'abortx' in flavors
    assert 'future' in flavors
    assert 'success' in flavors
    assert 'advice' in flavors


def test_810_derive_ictr_flavors_info( ):
    ''' Info level activates note and error-family without monition. '''
    flavors = module._derive_ictr_flavors( 'info' )
    assert 'note' in flavors
    assert 'monition' not in flavors
    assert 'error' in flavors
    assert 'success' in flavors


def test_815_derive_ictr_flavors_warn( ):
    ''' Warn level activates monition and error-family without note. '''
    flavors = module._derive_ictr_flavors( 'warn' )
    assert 'note' not in flavors
    assert 'monition' in flavors
    assert 'error' in flavors
    assert 'abort' in flavors
    assert 'success' in flavors


def test_820_derive_ictr_flavors_error( ):
    ''' Error level activates only error-family and semantic flavors. '''
    flavors = module._derive_ictr_flavors( 'error' )
    assert 'note' not in flavors
    assert 'monition' not in flavors
    assert 'error' in flavors
    assert 'abort' in flavors
    assert 'advice' in flavors


def test_830_prepare_scribes_ictr_installs_dispatcher( ):
    ''' Ictr preparation installs dispatcher into builtins by default. '''
    import builtins
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    alias = '_appcore_test_ictr_install'
    if hasattr( builtins, alias ):
        delattr( builtins, alias )
    control = module.Control(
        target = target_stream,
        ictr_alias = alias,
        active_flavors = ( 'note', ),
        install_ictr = True )
    dispatcher = module._prepare_scribes_ictr(
        globals_dto, control, target_stream )
    try:
        assert getattr( builtins, alias ) is dispatcher
    finally:
        if hasattr( builtins, alias ):
            delattr( builtins, alias )


def test_840_prepare_scribes_ictr_without_install( ):
    ''' Ictr preparation can skip builtins installation. '''
    import builtins
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    alias = '_appcore_test_ictr_noinstall'
    if hasattr( builtins, alias ):
        delattr( builtins, alias )
    control = module.Control(
        target = target_stream,
        ictr_alias = alias,
        install_ictr = False )
    dispatcher = module._prepare_scribes_ictr(
        globals_dto, control, target_stream )
    assert dispatcher is not None
    assert not hasattr( builtins, alias )


def test_850_prepare_scribes_ictr_explicit_flavors( ):
    ''' Explicit active flavors configure the dispatcher. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream,
        active_flavors = ( 'note', 'error' ),
        install_ictr = False )
    dispatcher = module._prepare_scribes_ictr(
        globals_dto, control, target_stream )
    active = dispatcher.active_flavors[ None ]
    assert active == frozenset( { 'note', 'error' } )


def test_860_prepare_scribes_ictr_explicit_trace_levels( ):
    ''' Explicit trace levels configure the dispatcher. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream,
        trace_levels = 3,
        install_ictr = False )
    dispatcher = module._prepare_scribes_ictr(
        globals_dto, control, target_stream )
    assert dispatcher.trace_levels[ None ] == 3


def test_870_prepare_scribes_ictr_app_env_flavors( ):
    ''' Application-specific ACTIVE_FLAVORS env configures dispatcher. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream, install_ictr = False )
    with patch.dict( __.os.environ, {
        'TEST_APP_ACTIVE_FLAVORS': 'note,error',
    }, clear = False ):
        dispatcher = module._prepare_scribes_ictr(
            globals_dto, control, target_stream )
    active = dispatcher.active_flavors[ None ]
    assert active == frozenset( { 'note', 'error' } )


def test_880_prepare_scribes_ictr_app_env_trace_levels( ):
    ''' Application-specific TRACE_LEVELS env configures dispatcher. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream, install_ictr = False )
    with patch.dict( __.os.environ, {
        'TEST_APP_TRACE_LEVELS': '4',
    }, clear = False ):
        dispatcher = module._prepare_scribes_ictr(
            globals_dto, control, target_stream )
    assert dispatcher.trace_levels[ None ] == 4


def test_890_prepare_scribes_ictr_explicit_overrides_env( ):
    ''' Explicit Control flavors override application environment. '''
    globals_dto, _ = create_globals_with_temp_dirs( app_name = 'test-app' )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream,
        active_flavors = ( 'success', ),
        install_ictr = False )
    with patch.dict( __.os.environ, {
        'TEST_APP_ACTIVE_FLAVORS': 'note,error',
    }, clear = False ):
        dispatcher = module._prepare_scribes_ictr(
            globals_dto, control, target_stream )
    active = dispatcher.active_flavors[ None ]
    assert active == frozenset( { 'success' } )


def test_895_prepare_scribes_ictr_ictr_env_flavors( ):
    ''' Ictr ICTR_ACTIVE_FLAVORS env provides flavors absent app env. '''
    globals_dto, _ = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control(
        target = target_stream, install_ictr = False )
    with patch.dict( __.os.environ, {
        'ICTR_ACTIVE_FLAVORS': 'error',
    }, clear = False ):
        dispatcher = module._prepare_scribes_ictr(
            globals_dto, control, target_stream )
    active = dispatcher.active_flavors[ None ]
    assert 'error' in active
    assert 'note' not in active


def test_900_produce_ictr_generalcfg_plain_strips_ansi( ):
    ''' Plain mode printer factory strips ANSI escape sequences. '''
    target_stream = io.StringIO( )
    control = module.Control( mode = module.Modes.Plain )
    factories = module._produce_ictr_generalcfg( control, target_stream )
    printer = factories[ 0 ]( 'addr', 'note' )
    printer( '\x1b[31mred\x1b[0m' )
    assert target_stream.getvalue( ) == 'red\n'


def test_910_produce_ictr_generalcfg_rich_uses_default_factory( ):
    ''' Rich mode uses the default ictr printer factory. '''
    target_stream = io.StringIO( )
    control = module.Control( mode = module.Modes.Rich )
    factories = module._produce_ictr_generalcfg( control, target_stream )
    assert len( factories ) == 1
    printer = factories[ 0 ]( 'addr', 'note' )
    assert hasattr( printer, 'provide_textualization_control' )
