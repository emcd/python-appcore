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


''' Application logging configuration and management tests. '''


import io
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

from . import PACKAGE_NAME, cache_import_module


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
    assert __.is_absent( control.target )


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


def test_130_control_creation_path_target( ):
    ''' Control accepts Path as target. '''
    with tempfile.NamedTemporaryFile( ) as tmp_file:
        target_path = Path( tmp_file.name )
        control = module.Control(
            mode = module.Modes.Plain,
            target = target_path
        )
        assert control.target == target_path


def test_140_control_immutability( ):
    ''' Control instances are immutable. '''
    control = module.Control( )
    # Should not be able to modify fields after creation
    try:
        control.mode = module.Modes.Rich  # type: ignore
        raise AssertionError( "Should not be able to modify immutable field" )
    except ( AttributeError, TypeError ):
        pass  # Expected


def test_150_control_equality( ):
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


def test_160_control_inequality( ):
    ''' Control instances with different data are not equal. '''
    control1 = module.Control( mode = module.Modes.Plain )
    control2 = module.Control( mode = module.Modes.Rich )
    assert control1 != control2


def test_200_prepare_with_null_mode( ):
    ''' prepare() configures logging with null mode. '''
    control = module.Control( mode = module.Modes.Null )
    # Should not raise an error
    module.prepare( control )


def test_210_prepare_with_plain_mode( ):
    ''' prepare() configures logging with plain mode. '''
    control = module.Control( 
        mode = module.Modes.Plain,
        level = 'debug'
    )
    # Should not raise an error
    module.prepare( control )


def test_220_prepare_with_rich_mode_without_rich( ):
    ''' prepare() gracefully degrades when Rich unavailable. '''
    control = module.Control( mode = module.Modes.Rich )
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', { 
        'rich.console': None, 
        'rich.logging': None 
    } ):
        # Should not raise an error (graceful fallback)
        module.prepare( control )


def test_230_prepare_with_stream_target( ):
    ''' prepare() accepts custom stream target. '''
    target_stream = io.StringIO( )
    control = module.Control( 
        mode = module.Modes.Plain,
        target = target_stream
    )
    # Should not raise an error
    module.prepare( control )


def test_240_prepare_with_file_target( ):
    ''' prepare() accepts file path target. '''
    with tempfile.NamedTemporaryFile( delete = False ) as tmp_file:
        target_path = Path( tmp_file.name )
    try:
        control = module.Control( 
            mode = module.Modes.Plain,
            target = target_path
        )
        # Should not raise an error
        module.prepare( control )
    finally:
        # Clean up temp file
        target_path.unlink( missing_ok = True )


def test_300_create_handler_absent_target( ):
    ''' _create_handler returns StreamHandler for absent target. '''
    handler = module._create_handler( __.absent )
    assert isinstance( handler, logging.StreamHandler )


def test_310_create_handler_stream_custom( ):
    ''' _create_handler returns StreamHandler for TextIO target. '''
    target_stream = io.StringIO( )
    handler = module._create_handler( target_stream )
    assert isinstance( handler, logging.StreamHandler )
    assert handler.stream == target_stream


def test_320_create_handler_file( ):
    ''' _create_handler returns FileHandler for Path target. '''
    with tempfile.NamedTemporaryFile( delete = False ) as tmp_file:
        target_path = Path( tmp_file.name )
    try:
        handler = module._create_handler( target_path )
        assert isinstance( handler, logging.FileHandler )
        # Clean up the handler
        handler.close( )
    finally:
        # Clean up temp file
        target_path.unlink( missing_ok = True )


def test_400_discover_inscription_level_name_default( ):
    ''' _discover_inscription_level_name uses control level by default. '''
    control = module.Control( level = 'debug' )
    level_name = module._discover_inscription_level_name( control )
    assert level_name == 'debug'


def test_410_discover_inscription_level_name_with_inscription_env( ):
    ''' _discover_inscription_level_name uses INSCRIPTION environment. '''
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, { 'APPCORE_INSCRIPTION_LEVEL': 'error' } ):
        level_name = module._discover_inscription_level_name( control )
        assert level_name == 'error'


def test_420_discover_inscription_level_name_with_log_env( ):
    ''' _discover_inscription_level_name uses LOG environment variable. '''
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, { 'APPCORE_LOG_LEVEL': 'warning' } ):
        level_name = module._discover_inscription_level_name( control )
        assert level_name == 'warning'


def test_430_discover_inscription_level_name_precedence( ):
    ''' _discover_inscription_level_name gives INSCRIPTION precedence. '''
    control = module.Control( level = 'info' )
    with patch.dict( __.os.environ, { 
        'APPCORE_INSCRIPTION_LEVEL': 'debug',
        'APPCORE_LOG_LEVEL': 'error' 
    } ):
        level_name = module._discover_inscription_level_name( control )
        assert level_name == 'debug'


def test_500_configure_null_mode( ):
    ''' _configure_null_mode adds handler to root logger. '''
    original_handler_count = len( logging.getLogger( ).handlers )
    module._configure_null_mode( logging.INFO, __.absent )
    # Should have added one handler
    new_handler_count = len( logging.getLogger( ).handlers )
    assert new_handler_count > original_handler_count


def test_510_configure_plain_mode( ):
    ''' _configure_plain_mode adds handler to root logger. '''
    original_handler_count = len( logging.getLogger( ).handlers )
    module._configure_plain_mode( logging.DEBUG, __.absent )
    # Should have added one handler
    new_handler_count = len( logging.getLogger( ).handlers )
    assert new_handler_count > original_handler_count


def test_520_configure_rich_mode_fallback( ):
    ''' _configure_rich_mode falls back when Rich unavailable. '''
    # Mock Rich imports to fail
    with patch.dict( 'sys.modules', { 
        'rich.console': None, 
        'rich.logging': None 
    } ):
        # Should not raise an error (graceful fallback)
        module._configure_rich_mode( logging.INFO, __.absent )


def test_530_configure_rich_mode_file_fallback( ):
    ''' _configure_rich_mode falls back to plain for file targets. '''
    with tempfile.NamedTemporaryFile( delete = False ) as tmp_file:
        target_path = Path( tmp_file.name )
    try:
        # Should fallback to plain mode for file targets
        module._configure_rich_mode( logging.INFO, target_path )
    finally:
        target_path.unlink( missing_ok = True )