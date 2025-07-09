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


''' Environment variable loading and dot file processing tests. '''


import pytest
from pathlib import Path
from unittest.mock import patch
import os

from . import PACKAGE_NAME, cache_import_module
from .fixtures import create_globals_with_temp_dirs


def _get_home_environment_vars( ):
    ''' Get minimal environment variables needed for Path.home(). '''
    return {
        key: value for key, value in os.environ.items( )
        if key in ( 'USERPROFILE', 'HOMEDRIVE', 'HOMEPATH', 'HOME' )
    }


MODULE_QNAME = f"{PACKAGE_NAME}.environment"
module = cache_import_module( MODULE_QNAME )

application_module = cache_import_module( f"{PACKAGE_NAME}.application" )
distribution_module = cache_import_module( f"{PACKAGE_NAME}.distribution" )
state_module = cache_import_module( f"{PACKAGE_NAME}.state" )




@pytest.mark.asyncio
async def test_100_update_editable_with_env_file( ):
    ''' Environment updater loads .env file for editable distributions. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( editable = True )
    # Create .env file in project root
    env_file = globals_dto.distribution.location / '.env'
    env_file.write_text( '''
TEST_VAR_1=editable_value_1
TEST_VAR_2=editable_value_2
    ''' )
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        await module.update( globals_dto )
        
        # Environment should be updated with values from .env file
        assert os.environ.get( 'TEST_VAR_1' ) == 'editable_value_1'
        assert os.environ.get( 'TEST_VAR_2' ) == 'editable_value_2'


@pytest.mark.asyncio
async def test_110_update_editable_with_env_directory( ):
    ''' Environment updater loads multiple .env files from directory. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( editable = True )
    # Create .env directory with multiple files
    env_dir = globals_dto.distribution.location / '.env'
    env_dir.mkdir( )
    ( env_dir / 'base.env' ).write_text( '''
BASE_VAR=base_value
OVERRIDE_VAR=base_override
    ''' )
    ( env_dir / 'local.env' ).write_text( '''
LOCAL_VAR=local_value
OVERRIDE_VAR=local_override
    ''' )
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        await module.update( globals_dto )
        
        # Environment should be updated with values from both files
        assert os.environ.get( 'BASE_VAR' ) == 'base_value'
        assert os.environ.get( 'LOCAL_VAR' ) == 'local_value'
        # One of the override values should be present
        assert 'OVERRIDE_VAR' in os.environ


@pytest.mark.asyncio
async def test_120_update_editable_no_env_file( ):
    ''' Environment updater falls through when no .env for editable. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( editable = True )
    # No .env file exists in project root
    assert not ( globals_dto.distribution.location / '.env' ).exists( )
    # Create a local .env file in current directory
    local_env = Path( ) / '.env'
    try:
        local_env.write_text( '''
FALLBACK_VAR=fallback_value
        ''' )
        
        with patch.dict( 
            os.environ, _get_home_environment_vars( ), clear = True ):
            await module.update( globals_dto )
            
            # Should load from local .env since project .env doesn't exist
            assert os.environ.get( 'FALLBACK_VAR' ) == 'fallback_value'
    finally:
        if local_env.exists( ):
            local_env.unlink( )


@pytest.mark.asyncio
async def test_130_update_normal_with_configured_location( ):
    ''' Environment updater loads from configured location for normal. '''
    config_locations = {
        'environment': '{user_configuration}/app.env'
    }
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        editable = False,
        config_locations = config_locations
    )
    # Create configured environment file
    config_env = globals_dto.directories.user_config_path / 'app.env'
    config_env.write_text( '''
CONFIG_VAR=config_value
PRECEDENCE_VAR=config_precedence
    ''' )
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        await module.update( globals_dto )
        
        # Environment should be updated from configured location
        assert os.environ.get( 'CONFIG_VAR' ) == 'config_value'
        assert os.environ.get( 'PRECEDENCE_VAR' ) == 'config_precedence'


@pytest.mark.asyncio
async def test_140_update_normal_with_local_precedence( ):
    ''' Environment updater gives local .env precedence over configured. '''
    config_locations = {
        'environment': '{user_configuration}/app.env'
    }
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        editable = False,
        config_locations = config_locations
    )
    # Create configured environment file
    config_env = globals_dto.directories.user_config_path / 'app.env'
    config_env.write_text( '''
CONFIG_VAR=config_value
PRECEDENCE_VAR=config_precedence
    ''' )
    # Create local .env file
    local_env = Path( ) / '.env'
    try:
        local_env.write_text( '''
LOCAL_VAR=local_value
PRECEDENCE_VAR=local_precedence
        ''' )
        
        with patch.dict( 
            os.environ, _get_home_environment_vars( ), clear = True ):
            await module.update( globals_dto )
            
            # Both files should be loaded
            assert os.environ.get( 'CONFIG_VAR' ) == 'config_value'
            assert os.environ.get( 'LOCAL_VAR' ) == 'local_value'
            # Local should take precedence
            assert os.environ.get( 'PRECEDENCE_VAR' ) == 'local_precedence'
    finally:
        if local_env.exists( ):
            local_env.unlink( )


@pytest.mark.asyncio
async def test_150_update_normal_local_only( ):
    ''' Environment updater loads only local .env when not configured. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( editable = False )
    # No configured location, only local .env
    local_env = Path( ) / '.env'
    try:
        local_env.write_text( '''
LOCAL_ONLY_VAR=local_only_value
        ''' )
        
        with patch.dict( 
            os.environ, _get_home_environment_vars( ), clear = True ):
            await module.update( globals_dto )
            
            # Should load from local .env only
            assert os.environ.get( 'LOCAL_ONLY_VAR' ) == 'local_only_value'
    finally:
        if local_env.exists( ):
            local_env.unlink( )


@pytest.mark.asyncio
async def test_160_update_normal_configured_directory( ):
    ''' Environment updater loads multiple files from configured directory. '''
    config_locations = {
        'environment': '{user_configuration}/env-dir'
    }
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        editable = False,
        config_locations = config_locations
    )
    # Create configured environment directory
    env_dir = globals_dto.directories.user_config_path / 'env-dir'
    env_dir.mkdir( )
    ( env_dir / 'db.env' ).write_text( '''
DB_HOST=localhost
DB_PORT=5432
    ''' )
    ( env_dir / 'api.env' ).write_text( '''
API_KEY=secret_key
API_URL=https://api.example.com
    ''' )
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        await module.update( globals_dto )
        
        # Environment should have values from both files
        assert os.environ.get( 'DB_HOST' ) == 'localhost'
        assert os.environ.get( 'DB_PORT' ) == '5432'
        assert os.environ.get( 'API_KEY' ) == 'secret_key'
        assert os.environ.get( 'API_URL' ) == 'https://api.example.com'


@pytest.mark.asyncio
async def test_170_update_normal_no_files_exist( ):
    ''' Environment updater handles case when no .env files exist. '''
    globals_dto, temp_dir = create_globals_with_temp_dirs( editable = False )
    # No .env files exist anywhere
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        # Should complete without error
        await module.update( globals_dto )
        
        # Environment should only contain home directory variables
        expected_vars = _get_home_environment_vars( )
        assert len( os.environ ) == len( expected_vars )
        for key, value in expected_vars.items( ):
            assert os.environ.get( key ) == value


@pytest.mark.asyncio
async def test_180_update_home_template_substitution( ):
    ''' Environment updater properly substitutes {user_home} in templates. '''
    config_locations = {
        'environment': '{user_home}/.config/myapp/env.conf'
    }
    globals_dto, temp_dir = create_globals_with_temp_dirs(
        editable = False,
        config_locations = config_locations
    )
    # Create environment file in home-based location
    home_config_dir = Path.home( ) / '.config' / 'myapp'
    home_config_dir.mkdir( parents = True, exist_ok = True )
    home_env = home_config_dir / 'env.conf'
    try:
        home_env.write_text( '''
HOME_VAR=home_value
        ''' )
        
        with patch.dict( 
            os.environ, _get_home_environment_vars( ), clear = True ):
            await module.update( globals_dto )
            
            # Should load from home-based location
            assert os.environ.get( 'HOME_VAR' ) == 'home_value'
    finally:
        if home_env.exists( ):
            home_env.unlink( )
        # Cleanup directory if we created it
        try:
            home_config_dir.rmdir( )
            home_config_dir.parent.rmdir( )
        except OSError:
            pass  # Directory not empty or doesn't exist


def test_200_inject_dotenv_data_success( ):
    ''' _inject_dotenv_data successfully loads environment data. '''
    data = '''
TEST_INJECT_VAR=inject_value
ANOTHER_VAR=another_value
    '''
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        result = module._inject_dotenv_data( data )
        
        # Should return True for successful load
        assert result is True
        # Variables should be loaded into environment
        assert os.environ.get( 'TEST_INJECT_VAR' ) == 'inject_value'
        assert os.environ.get( 'ANOTHER_VAR' ) == 'another_value'


def test_210_inject_dotenv_data_empty( ):
    ''' _inject_dotenv_data handles empty data gracefully. '''
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        result = module._inject_dotenv_data( '' )
        
        # Should return False for empty data
        assert result is False
        # Environment should only contain home directory variables
        expected_vars = _get_home_environment_vars( )
        assert len( os.environ ) == len( expected_vars )
        for key, value in expected_vars.items( ):
            assert os.environ.get( key ) == value


def test_220_inject_dotenv_data_comments_and_whitespace( ):
    ''' _inject_dotenv_data properly handles comments and whitespace. '''
    data = '''
# This is a comment
TEST_VAR=value_with_spaces

# Another comment
EMPTY_VAR=

QUOTED_VAR="quoted value"
    '''
    with patch.dict( 
        os.environ, _get_home_environment_vars( ), clear = True ):
        result = module._inject_dotenv_data( data )
        
        # Should return True for successful load
        assert result is True
        # Should properly parse variables
        assert os.environ.get( 'TEST_VAR' ) == 'value_with_spaces'
        assert os.environ.get( 'EMPTY_VAR' ) == ''
        assert os.environ.get( 'QUOTED_VAR' ) == 'quoted value'