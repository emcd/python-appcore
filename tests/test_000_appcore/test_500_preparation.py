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


import contextlib
import io

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from appcore import application as application_module
from appcore import configuration as configuration_module
from appcore import dictedits as dictedits_module
from appcore import distribution as distribution_module
from appcore import inscription as inscription_module
from appcore import preparation as module
from appcore import state as state_module


async def _prepare( exits, **nomargs ):
    ''' Calls prepare without installing ictr into builtins. '''
    if 'inscription' not in nomargs:
        nomargs[ 'inscription' ] = inscription_module.Control(
            install_ictr = False )
    else:
        ctrl = nomargs[ 'inscription' ]
        nomargs[ 'inscription' ] = inscription_module.Control(
            active_flavors = ctrl.active_flavors,
            ictr_alias = ctrl.ictr_alias,
            install_ictr = False,
            level = ctrl.level,
            mode = ctrl.mode,
            target = ctrl.target,
            trace_levels = ctrl.trace_levels )
    return await module.prepare( exits, **nomargs )


@pytest.mark.asyncio
async def test_100_prepare_minimal( ):
    ''' Preparation works with minimal arguments. '''
    exits = MagicMock( )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        distribution = distribution,
        configfile = config_stream
    )
    assert isinstance( result, state_module.Globals )
    assert result.exits == exits
    assert result.application.name == 'test-dist'  # From distribution
    assert 'app' in result.configuration


@pytest.mark.asyncio
async def test_110_prepare_with_custom_application( ):
    ''' Preparation accepts custom application information. '''
    exits = MagicMock( )
    application = application_module.Information(
        name = 'custom-app',
        publisher = 'Test Publisher'
    )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        application = application,
        distribution = distribution,
        configfile = config_stream
    )
    assert result.application.name == 'custom-app'
    assert result.application.publisher == 'Test Publisher'


@pytest.mark.asyncio
async def test_120_prepare_with_custom_acquirer( ):
    ''' Preparation accepts custom configuration acquirer. '''
    exits = MagicMock( )
    acquirer = configuration_module.TomlAcquirer(
        main_filename = 'custom.toml',
        includes_name = 'custom_includes'
    )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream with custom content
    config_content = '''
[custom]
value = "config"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        acquirer = acquirer,
        distribution = distribution,
        configfile = config_stream
    )
    assert 'custom' in result.configuration
    assert result.configuration[ 'custom' ][ 'value' ] == 'config'


@pytest.mark.asyncio
async def test_130_prepare_with_config_edits( ):
    ''' Preparation applies configuration edits. '''
    exits = MagicMock( )
    edits = (
        dictedits_module.SimpleEdit(
            address = [ 'app', 'version' ],
            value = '2.0.0'
        ),
    )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
version = "1.0.0"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        configedits = edits,
        distribution = distribution,
        configfile = config_stream
    )
    # Verify edits were applied
    assert result.configuration[ 'app' ][ 'name' ] == 'test'
    assert result.configuration[ 'app' ][ 'version' ] == '2.0.0'


@pytest.mark.asyncio
async def test_140_prepare_with_config_file( ):
    ''' Preparation accepts custom configuration file. '''
    exits = MagicMock( )
    config_content = '''
[app]
name = "file-app"
version = "1.0.0"
    '''
    config_file = io.StringIO( config_content )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    result = await _prepare(
        exits,
        configfile = config_file,
        distribution = distribution
    )
    # Verify configuration was loaded from file
    assert result.configuration[ 'app' ][ 'name' ] == 'file-app'
    assert result.configuration[ 'app' ][ 'version' ] == '1.0.0'


@pytest.mark.asyncio
async def test_150_prepare_with_custom_directories( ):
    ''' Preparation accepts custom platform directories. '''
    exits = MagicMock( )
    directories = MagicMock( )
    directories.user_config_path = Path( '/custom/config' )
    directories.user_data_path = Path( '/custom/data' )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        directories = directories,
        distribution = distribution,
        configfile = config_stream
    )
    assert result.directories == directories
    assert result.configuration[ 'app' ][ 'name' ] == 'test'


@pytest.mark.asyncio
async def test_160_prepare_with_custom_distribution( ):
    ''' Preparation accepts custom distribution information. '''
    exits = MagicMock( )
    distribution = distribution_module.Information(
        name = 'custom-dist',
        location = Path( '/custom/location' ),
        editable = False
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    result = await _prepare(
        exits,
        distribution = distribution,
        configfile = config_stream
    )
    assert result.distribution == distribution
    assert result.configuration[ 'app' ][ 'name' ] == 'test'


@pytest.mark.asyncio
async def test_170_prepare_with_environment_bool( ):
    ''' Preparation accepts environment enablement flag. '''
    exits = MagicMock( )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    # Test that prepare() completes successfully with environment=True
    result = await _prepare(
        exits,
        environment = True,
        distribution = distribution,
        configfile = config_stream
    )
    # Verify basic functionality still works
    assert isinstance( result, state_module.Globals )
    assert result.configuration[ 'app' ][ 'name' ] == 'test'


@pytest.mark.asyncio
async def test_180_prepare_with_environment_mapping( ):
    ''' Preparation updates environment from a mapping. '''
    exits = MagicMock( )
    environment = { 'TEST_VAR': 'test_value', 'OTHER_VAR': 'other_value' }
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    with (
        patch.dict( 'os.environ', { }, clear = True )
        as mock_environ
    ):
        await _prepare(
            exits,
            environment = environment,
            distribution = distribution,
            configfile = config_stream
        )
        # Environment variables should be updated
        assert mock_environ[ 'TEST_VAR' ] == 'test_value'
        assert mock_environ[ 'OTHER_VAR' ] == 'other_value'


@pytest.mark.asyncio
async def test_190_prepare_with_custom_inscription( ):
    ''' Preparation accepts custom inscription control. '''
    exits = MagicMock( )
    # Create real inscription control
    inscription = inscription_module.Control(
        mode = inscription_module.Modes.Null,
        level = 'debug',
        install_ictr = False,
    )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    # Test that prepare() completes successfully with custom inscription
    result = await _prepare(
        exits,
        inscription = inscription,
        distribution = distribution,
        configfile = config_stream
    )
    # Verify basic functionality still works
    assert isinstance( result, state_module.Globals )
    assert result.configuration[ 'app' ][ 'name' ] == 'test'


@pytest.mark.asyncio
async def test_200_prepare_auto_directories( ):
    ''' Preparation auto-creates directories when not provided. '''
    exits = MagicMock( )
    application = application_module.Information( name = 'auto-dir-app' )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    # Test without providing directories - they should be auto-created
    result = await _prepare(
        exits,
        application = application,
        distribution = distribution,
        configfile = config_stream
        # Note: no directories parameter provided
    )
    # Verify directories were auto-created and assigned
    assert result.directories is not None
    assert hasattr( result.directories, 'user_config_path' )




@pytest.mark.asyncio
async def test_215_prepare_distribution_auto_discovery( ):
    ''' Distribution auto-discovery triggers when not provided. '''
    # Create real configuration stream
    config_content = '''
[app]
name = "test-app"
'''
    config_stream = io.StringIO( config_content )
    async with contextlib.AsyncExitStack( ) as exits:
        # Call prepare() without distribution to trigger auto-discovery
        result = await _prepare(
            exits,
            configfile = config_stream
            # Note: no distribution parameter - should auto-discover
        )
        # Verify that distribution was auto-discovered and assigned
        assert result.distribution is not None
        assert isinstance( result.distribution,
                          distribution_module.Information )
        # Should discover this package (emcd-appcore)
        assert result.distribution.name == 'emcd-appcore'


@pytest.mark.asyncio
async def test_220_prepare_basic_functionality( ):
    ''' Preparation completes basic initialization successfully. '''
    exits = MagicMock( )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    # Create real configuration stream
    config_content = '''
[app]
name = "test"
    '''
    config_stream = io.StringIO( config_content )
    # Test that prepare() completes successfully
    result = await _prepare(
        exits,
        distribution = distribution,
        configfile = config_stream
    )
    # Verify complete globals object is created
    assert isinstance( result, state_module.Globals )
    assert result.exits == exits
    assert result.distribution == distribution
    assert result.configuration[ 'app' ][ 'name' ] == 'test'


@pytest.mark.asyncio
async def test_300_prepare_integration_complete( ):
    ''' Full preparation integrates real components successfully. '''
    exits = MagicMock( )
    # Use a real application info
    application = application_module.Information(
        name = 'integration-test-app',
        publisher = 'Test Publisher',
        version = '1.0.0'
    )
    # Create real distribution information
    distribution = distribution_module.Information(
        name = 'integration-dist',
        location = Path( '/integration/location' ),
        editable = True
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
    result = await _prepare(
        exits,
        application = application,
        distribution = distribution,
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
    assert hasattr( module, '_configuration_acquirer' )
    assert isinstance( module._configuration_acquirer,
                      configuration_module.TomlAcquirer )


def test_410_inscribe_preparation_report( ):
    ''' Preparation reporting function provides startup information. '''
    # Verify the function exists
    assert hasattr( module, '_inscribe_preparation_report' )
    assert callable( module._inscribe_preparation_report )
    # Create a simple globals object
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
    # Test that the function can be called without error
    # (This tests the function interface, not the internal logging details)
    try:
        module._inscribe_preparation_report( globals_obj )
        # If we get here, the function executed without error
        assert True
    except Exception as e:
        # If there's an error, fail the test
        raise AssertionError(
            f"_inscribe_preparation_report raised: {e}" ) from e
