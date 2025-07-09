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

from . import PACKAGE_NAME, cache_import_module
from .fixtures import create_globals_with_temp_dirs


MODULE_QNAME = f"{PACKAGE_NAME}.inscription"
module = cache_import_module( MODULE_QNAME )
__ = cache_import_module( f"{PACKAGE_NAME}.__" )


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


def test_120_control_creation_custom_values( ):
    ''' Control accepts custom mode, level, and target. '''
    target_stream = io.StringIO( )
    control = module.Control(
        mode = module.Modes.Rich,
        level = 'debug',
        target = target_stream
    )
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
        level = 'debug'
    )
    control2 = module.Control(
        mode = module.Modes.Rich,
        level = 'debug'
    )
    assert control1 == control2


def test_150_control_inequality( ):
    ''' Control instances with different data are not equal. '''
    control1 = module.Control( mode = module.Modes.Plain )
    control2 = module.Control( mode = module.Modes.Rich )
    assert control1 != control2


def test_200_prepare_with_null_mode( ):
    ''' prepare() handles null mode (no configuration). '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    control = module.Control( mode = module.Modes.Null )
    # Should not raise an error or configure logging
    module.prepare( globals_dto, control )


def test_210_prepare_with_plain_mode( ):
    ''' prepare() configures logging with plain mode. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Plain,
        level = 'debug',
        target = target_stream
    )
    # Should not raise an error
    module.prepare( globals_dto, control )


def test_220_prepare_with_rich_mode_without_rich( ):
    ''' prepare() gracefully degrades when Rich unavailable. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Rich,
        target = target_stream
    )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', { 
        'rich.console': None, 
        'rich.logging': None 
    } ):
        # Should not raise an error (graceful fallback)
        module.prepare( globals_dto, control )


def test_230_prepare_with_stream_target( ):
    ''' prepare() accepts custom stream target. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Plain,
        target = target_stream
    )
    # Should not raise an error
    module.prepare( globals_dto, control )


def test_300_discover_inscription_level_name_default( ):
    ''' Level discovery defaults to control level when no override. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    control = module.Control( level = 'debug' )
    level_name = module._discover_inscription_level_name(
        globals_dto, control )
    assert level_name == 'debug'


def test_310_discover_inscription_level_name_with_inscription_env( ):
    ''' INSCRIPTION environment variable overrides control level setting. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'TEST_APP_INSCRIPTION_LEVEL': 'error'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'error'


def test_320_discover_inscription_level_name_with_log_env( ):
    ''' LOG environment variable provides alternative level override. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, { 'TEST_APP_LOG_LEVEL': 'warning' } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'warning'


def test_330_discover_inscription_level_name_precedence( ):
    ''' _discover_inscription_level_name gives INSCRIPTION precedence. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        app_name = 'test-app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'TEST_APP_INSCRIPTION_LEVEL': 'debug',
        'TEST_APP_LOG_LEVEL': 'error'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'debug'


def test_340_discover_inscription_level_name_normalizes_app_name( ):
    ''' _discover_inscription_level_name normalizes app name for env vars. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        app_name = 'my-awesome app' )
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, {
        'MY_AWESOME_APP_INSCRIPTION_LEVEL': 'debug'
    } ):
        level_name = module._discover_inscription_level_name(
            globals_dto, control )
        assert level_name == 'debug'


def test_350_discover_inscription_level_name_robust_normalization( ):
    ''' _discover_inscription_level_name handles special chars robustly. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs(
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
    ''' prepare_scribes_logging configures plain logging. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Plain,
        level = 'debug',
        target = target_stream
    )
    # Should not raise an error
    module.prepare_scribes_logging( globals_dto, control )


def test_410_prepare_scribes_logging_rich_fallback( ):
    ''' prepare_scribes_logging falls back when Rich unavailable. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Rich,
        target = target_stream
    )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', { 
        'rich.console': None, 
        'rich.logging': None 
    } ):
        # Should not raise an error (graceful fallback)
        module.prepare_scribes_logging( globals_dto, control )


def test_420_prepare_scribes_logging_null( ):
    ''' prepare_scribes_logging handles null mode. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( )
    control = module.Control( mode = module.Modes.Null )
    # Should not raise an error or configure logging
    module.prepare_scribes_logging( globals_dto, control )


def test_500_prepare_logging_plain( ):
    ''' _prepare_logging_plain configures basic logging. '''
    target_stream = io.StringIO( )
    formatter = logging.Formatter( "%(name)s: %(message)s" )
    # Should not raise an error
    module._prepare_logging_plain( logging.DEBUG, target_stream, formatter )


def test_510_prepare_logging_rich_fallback( ):
    ''' _prepare_logging_rich falls back when Rich unavailable. '''
    target_stream = io.StringIO( )
    formatter = logging.Formatter( "%(name)s: %(message)s" )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', { 
        'rich.console': None, 
        'rich.logging': None 
    } ):
        # Should not raise an error (graceful fallback)
        module._prepare_logging_rich( logging.INFO, target_stream, formatter )