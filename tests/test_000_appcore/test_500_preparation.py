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


''' Application preparation and integration tests. '''


import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import io

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.preparation"
module = cache_import_module( MODULE_QNAME )

application_module = cache_import_module( f"{PACKAGE_NAME}.application" )
configuration_module = cache_import_module( f"{PACKAGE_NAME}.configuration" )
dictedits_module = cache_import_module( f"{PACKAGE_NAME}.dictedits" )
distribution_module = cache_import_module( f"{PACKAGE_NAME}.distribution" )
state_module = cache_import_module( f"{PACKAGE_NAME}.state" )


@pytest.mark.asyncio
async def test_100_prepare_minimal( ):
    ''' prepare() works with minimal arguments. '''
    exits = MagicMock( )
    
    # Mock dependencies
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        result = await module.prepare( exits )
        
        assert isinstance( result, state_module.Globals )
        assert result.exits == exits
        assert result.application.name == PACKAGE_NAME  # Default application
        assert 'app' in result.configuration


@pytest.mark.asyncio
async def test_110_prepare_with_custom_application( ):
    ''' prepare() accepts custom application information. '''
    exits = MagicMock( )
    application = application_module.Information( 
        name = 'custom-app',
        publisher = 'Test Publisher'
    )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        result = await module.prepare( exits, application = application )
        
        assert result.application.name == 'custom-app'
        assert result.application.publisher == 'Test Publisher'


@pytest.mark.asyncio
async def test_120_prepare_with_custom_acquirer( ):
    ''' prepare() accepts custom configuration acquirer. '''
    exits = MagicMock( )
    acquirer = configuration_module.TomlAcquirer(
        main_filename = 'custom.toml',
        includes_name = 'custom_includes'
    )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( acquirer, '__call__' )
        as mock_acquirer_call
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer_call.return_value = { 'custom': 'config' }
        
        result = await module.prepare( exits, acquirer = acquirer )
        
        assert 'custom' in result.configuration
        mock_acquirer_call.assert_called_once( )


@pytest.mark.asyncio
async def test_130_prepare_with_config_edits( ):
    ''' prepare() applies configuration edits. '''
    exits = MagicMock( )
    edits = (
        dictedits_module.SimpleEdit(
            address = [ 'app', 'version' ],
            value = '2.0.0'
        ),
    )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        # The acquirer should receive the edits
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        await module.prepare( exits, configedits = edits )
        
        # Verify edits were passed to acquirer
        mock_acquirer.assert_called_once( )
        call_args = mock_acquirer.call_args
        assert call_args[ 1 ][ 'edits' ] == edits


@pytest.mark.asyncio
async def test_140_prepare_with_config_file( ):
    ''' prepare() accepts custom configuration file. '''
    exits = MagicMock( )
    config_content = '''
[app]
name = "file-app"
version = "1.0.0"
    '''
    config_file = io.StringIO( config_content )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'file-app' } }
        
        await module.prepare( exits, configfile = config_file )
        
        # Verify file was passed to acquirer
        mock_acquirer.assert_called_once( )
        call_args = mock_acquirer.call_args
        assert call_args[ 1 ][ 'file' ] == config_file


@pytest.mark.asyncio
async def test_150_prepare_with_custom_directories( ):
    ''' prepare() accepts custom platform directories. '''
    exits = MagicMock( )
    directories = MagicMock( )
    directories.user_config_path = Path( '/custom/config' )
    directories.user_data_path = Path( '/custom/data' )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        result = await module.prepare( exits, directories = directories )
        
        assert result.directories == directories
        # Verify directories were passed to acquirer
        mock_acquirer.assert_called_once( )
        call_args = mock_acquirer.call_args
        assert call_args[ 1 ][ 'directories' ] == directories


@pytest.mark.asyncio
async def test_160_prepare_with_custom_distribution( ):
    ''' prepare() accepts custom distribution information. '''
    exits = MagicMock( )
    distribution = distribution_module.Information(
        name = 'custom-dist',
        location = Path( '/custom/location' ),
        editable = False
    )
    
    with (
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        result = await module.prepare( exits, distribution = distribution )
        
        assert result.distribution == distribution
        # Distribution.prepare should not be called
        # Verify distribution was passed to acquirer
        mock_acquirer.assert_called_once( )
        call_args = mock_acquirer.call_args
        assert call_args[ 1 ][ 'distribution' ] == distribution


@pytest.mark.asyncio
async def test_170_prepare_with_environment_bool( ):
    ''' prepare() loads environment when environment=True. '''
    exits = MagicMock( )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer,
        patch( f"{MODULE_QNAME}._environment.update" )
        as mock_env_update
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        mock_env_update.return_value = AsyncMock( )
        
        await module.prepare( exits, environment = True )
        
        # Environment update should be called with globals
        mock_env_update.assert_called_once( )
        call_args = mock_env_update.call_args[ 0 ][ 0 ]
        assert isinstance( call_args, state_module.Globals )


@pytest.mark.asyncio
async def test_180_prepare_with_environment_mapping( ):
    ''' prepare() updates environment with mapping. '''
    exits = MagicMock( )
    environment = { 'TEST_VAR': 'test_value', 'OTHER_VAR': 'other_value' }
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer,
        patch.dict( 'os.environ', { }, clear = True )
        as mock_environ
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        await module.prepare( exits, environment = environment )
        
        # Environment variables should be updated
        assert mock_environ[ 'TEST_VAR' ] == 'test_value'
        assert mock_environ[ 'OTHER_VAR' ] == 'other_value'


@pytest.mark.asyncio
async def test_190_prepare_with_custom_inscription( ):
    ''' prepare() accepts custom inscription control. '''
    exits = MagicMock( )
    inscription = MagicMock( )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer,
        patch( f"{MODULE_QNAME}._inscription.prepare" )
        as mock_inscription_prepare
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        await module.prepare( exits, inscription = inscription )
        
        # Inscription prepare should be called with custom control
        mock_inscription_prepare.assert_called_once_with( 
            control = inscription )


@pytest.mark.asyncio
async def test_200_prepare_auto_directories( ):
    ''' prepare() auto-creates directories from application. '''
    exits = MagicMock( )
    application = application_module.Information( name = 'auto-dir-app' )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer,
        patch.object( application, 'produce_platform_directories' )
        as mock_produce_dirs
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        mock_directories = MagicMock( )
        mock_produce_dirs.return_value = mock_directories
        
        result = await module.prepare( exits, application = application )
        
        # Application should produce directories
        mock_produce_dirs.assert_called_once( )
        assert result.directories == mock_directories


@pytest.mark.asyncio
async def test_210_prepare_auto_distribution( ):
    ''' prepare() auto-prepares distribution information. '''
    exits = MagicMock( )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer
    ):
        
        mock_distribution = distribution_module.Information(
            name = 'auto-dist',
            location = Path( '/auto' ),
            editable = False
        )
        mock_dist_prepare.return_value = mock_distribution
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        result = await module.prepare( exits )
        
        # Distribution prepare should be called with package name and exits
        mock_dist_prepare.assert_called_once_with(
            package = PACKAGE_NAME, exits = exits )
        assert result.distribution == mock_distribution


@pytest.mark.asyncio
async def test_220_prepare_inscription_preparation_report( ):
    ''' prepare() logs preparation report. '''
    exits = MagicMock( )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare,
        patch.object( configuration_module.TomlAcquirer, '__call__' )
        as mock_acquirer,
        patch( f"{MODULE_QNAME}._inscribe_preparation_report" )
        as mock_report
    ):
        
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'test-dist',
            location = Path( '/test' ),
            editable = True
        )
        
        mock_acquirer.return_value = { 'app': { 'name': 'test' } }
        
        await module.prepare( exits )
        
        # Preparation report should be logged
        mock_report.assert_called_once( )
        call_args = mock_report.call_args[ 0 ][ 0 ]
        assert isinstance( call_args, state_module.Globals )


@pytest.mark.asyncio
async def test_300_prepare_integration_complete( ):
    ''' prepare() full integration test with real components. '''
    exits = MagicMock( )
    
    # Use a real application info
    application = application_module.Information(
        name = 'integration-test-app',
        publisher = 'Test Publisher',
        version = '1.0.0'
    )
    
    # Create a configuration file
    config_content = '''
[app]
name = "integration-app"
debug = true

[database]
host = "localhost"
port = 5432

[locations]
cache = "{user_home}/test-cache/{application_name}"
    '''
    config_file = io.StringIO( config_content )
    
    # Add some edits
    edits = (
        dictedits_module.SimpleEdit(
            address = [ 'app', 'version' ],
            value = '2.0.0'
        ),
        dictedits_module.SimpleEdit(
            address = [ 'database', 'timeout' ],
            value = 30
        ),
    )
    
    with (
        patch.object( distribution_module.Information, 'prepare' )
        as mock_dist_prepare
    ):
        mock_dist_prepare.return_value = distribution_module.Information(
            name = 'integration-dist',
            location = Path( '/integration/location' ),
            editable = True
        )
        
        result = await module.prepare(
            exits,
            application = application,
            configfile = config_file,
            configedits = edits
        )
        
        # Verify complete globals object
        assert isinstance( result, state_module.Globals )
        assert result.application.name == 'integration-test-app'
        assert result.application.publisher == 'Test Publisher'
        assert result.application.version == '1.0.0'
        
        # Verify configuration was processed and edited
        assert result.configuration[ 'app' ][ 'name' ] == 'integration-app'
        assert result.configuration[ 'app' ][ 'debug' ] is True
        assert result.configuration[ 'app' ][ 'version' ] == '2.0.0'  # Edited
        assert result.configuration[ 'database' ][ 'host' ] == 'localhost'
        assert result.configuration[ 'database' ][ 'port' ] == 5432
        assert (
            result.configuration[ 'database' ][ 'timeout' ] == 30
        )  # Added by edit
        
        # Verify location configuration is present
        assert 'locations' in result.configuration
        assert 'cache' in result.configuration[ 'locations' ]
        
        # Verify other components are present
        assert result.exits == exits
        assert result.distribution.name == 'integration-dist'
        assert result.directories is not None


def test_400_module_level_defaults( ):
    ''' Module has proper default instances. '''
    assert hasattr( module, '_application_information' )
    assert hasattr( module, '_configuration_acquirer' )
    
    assert isinstance( module._application_information, 
                      application_module.Information )
    assert isinstance( module._configuration_acquirer, 
                      configuration_module.TomlAcquirer )


def test_410_inscribe_preparation_report( ):
    ''' _inscribe_preparation_report logs expected information. '''
    # Create a mock globals object
    application = application_module.Information( name = 'test-app' )
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test/location' ),
        editable = True
    )
    directories = MagicMock( )
    
    globals_obj = state_module.Globals(
        application = application,
        configuration = { },
        directories = directories,
        distribution = distribution,
        exits = MagicMock( )
    )
    
    # Mock the scribe
    with patch( f"{MODULE_QNAME}.__.produce_scribe" ) as mock_produce_scribe:
        mock_scribe = MagicMock( )
        mock_produce_scribe.return_value = mock_scribe
        
        module._inscribe_preparation_report( globals_obj )
        
        # Verify scribe was created for package
        mock_produce_scribe.assert_called_once_with( PACKAGE_NAME )
        
        # Verify debug messages were logged
        assert mock_scribe.debug.call_count >= 4
        
        # Check that application name was logged
        debug_calls = [
            call[ 0 ][ 0 ] for call in mock_scribe.debug.call_args_list
        ]
        app_name_logged = any( 'test-app' in call for call in debug_calls )
        assert app_name_logged