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


''' Configuration acquirer and management tests. '''


import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock
import io

from . import PACKAGE_NAME, cache_import_module
from .fixtures import (
    create_temp_directories_and_distribution, create_config_template_files )


MODULE_QNAME = f"{PACKAGE_NAME}.configuration"
module = cache_import_module( MODULE_QNAME )

dictedits_module = cache_import_module( f"{PACKAGE_NAME}.dictedits" )
distribution_module = cache_import_module( f"{PACKAGE_NAME}.distribution" )
exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )


def test_100_enablement_tristate_disable( ):
    ''' EnablementTristate.Disable converts to False. '''
    state = module.EnablementTristate.Disable
    assert bool( state ) is False


def test_110_enablement_tristate_enable( ):
    ''' EnablementTristate.Enable converts to True. '''
    state = module.EnablementTristate.Enable
    assert bool( state ) is True


def test_120_enablement_tristate_retain_error( ):
    ''' EnablementTristate.Retain raises error on boolean conversion. '''
    state = module.EnablementTristate.Retain
    with pytest.raises( exceptions_module.OperationInvalidity ):
        bool( state )


def test_130_enablement_tristate_is_retain( ):
    ''' EnablementTristate.is_retain identifies retain state. '''
    assert module.EnablementTristate.Retain.is_retain( ) is True
    assert module.EnablementTristate.Enable.is_retain( ) is False
    assert module.EnablementTristate.Disable.is_retain( ) is False


def test_140_enablement_tristate_values( ):
    ''' EnablementTristate has expected string values. '''
    assert module.EnablementTristate.Disable.value == 'disable'
    assert module.EnablementTristate.Retain.value == 'retain'
    assert module.EnablementTristate.Enable.value == 'enable'


def test_200_toml_acquirer_creation( ):
    ''' TomlAcquirer creates with default values. '''
    acquirer = module.TomlAcquirer( )
    assert acquirer.main_filename == 'general.toml'
    assert acquirer.includes_name == 'includes'


def test_210_toml_acquirer_custom_values( ):
    ''' TomlAcquirer accepts custom filename and includes name. '''
    acquirer = module.TomlAcquirer(
        main_filename = 'custom.toml',
        includes_name = 'custom_includes'
    )
    assert acquirer.main_filename == 'custom.toml'
    assert acquirer.includes_name == 'custom_includes'


def test_220_toml_acquirer_protocol_compliance( ):
    ''' TomlAcquirer implements AcquirerAbc protocol. '''
    acquirer = module.TomlAcquirer( )
    # Check that TomlAcquirer has the required protocol methods
    assert hasattr( acquirer, '__call__' )
    assert callable( acquirer )
    # Check that it's a dataclass (protocol requirement)
    assert hasattr( acquirer, '__dataclass_fields__' )


@pytest.mark.asyncio
async def test_300_toml_acquirer_call_with_text_io( ):
    ''' TomlAcquirer processes configuration from TextIO. '''
    toml_content = '''
[app]
name = "test-app"
version = "1.0.0"

[database]
host = "localhost"
port = 5432
    '''
    
    file_io = io.StringIO( toml_content )
    directories = MagicMock( )
    distribution = MagicMock( )
    
    acquirer = module.TomlAcquirer( )
    result = await acquirer(
        'test-app',
        directories,
        distribution,
        file = file_io
    )
    
    assert result[ 'app' ][ 'name' ] == 'test-app'
    assert result[ 'app' ][ 'version' ] == '1.0.0'
    assert result[ 'database' ][ 'host' ] == 'localhost'
    assert result[ 'database' ][ 'port' ] == 5432


@pytest.mark.asyncio
async def test_310_toml_acquirer_call_with_path( ):
    ''' TomlAcquirer processes configuration from file path. '''
    toml_content = '''
[app]
name = "path-app"
debug = true
    '''
    
    with tempfile.NamedTemporaryFile( mode = 'w', suffix = '.toml',
                                      delete = False ) as tmp_file:
        tmp_file.write( toml_content )
        tmp_file_path = Path( tmp_file.name )
    
    try:
        directories = MagicMock( )
        distribution = MagicMock( )
        
        acquirer = module.TomlAcquirer( )
        result = await acquirer(
            'path-app',
            directories,
            distribution,
            file = tmp_file_path
        )
        
        assert result[ 'app' ][ 'name' ] == 'path-app'
        assert result[ 'app' ][ 'debug' ] is True
    finally:
        tmp_file_path.unlink( )


@pytest.mark.asyncio
async def test_320_toml_acquirer_call_with_edits( ):
    ''' TomlAcquirer applies edits to configuration. '''
    toml_content = '''
[app]
name = "test-app"
version = "1.0.0"
    '''
    
    file_io = io.StringIO( toml_content )
    directories = MagicMock( )
    distribution = MagicMock( )
    
    # Create edit to modify version
    edit = dictedits_module.SimpleEdit(
        address = [ 'app', 'version' ],
        value = '2.0.0'
    )
    
    acquirer = module.TomlAcquirer( )
    result = await acquirer(
        'test-app',
        directories,
        distribution,
        edits = ( edit, ),
        file = file_io
    )
    
    assert result[ 'app' ][ 'name' ] == 'test-app'
    assert result[ 'app' ][ 'version' ] == '2.0.0'  # Modified by edit


@pytest.mark.asyncio
async def test_325_toml_acquirer_call_with_absent_file( ):
    ''' TomlAcquirer handles absent file parameter by discovering template. '''
    # Create temp directories and distribution with template file
    directories, distribution, temp_dir = (
        create_temp_directories_and_distribution( ) )
    
    template_content = '''
[app]
name = "discovered-app"
version = "1.0.0"
    '''
    
    # Create template file in distribution data location
    create_config_template_files( 
        distribution, 
        main_filename = 'general.toml',
        content = template_content 
    )
    
    try:
        acquirer = module.TomlAcquirer( )
        
        # Call with absent file parameter (triggers line 80-81)
        result = await acquirer(
            'test-app',
            directories,
            distribution,
            file = module.__.absent
        )
        
        # Verify configuration was loaded from discovered template
        assert result[ 'app' ][ 'name' ] == 'discovered-app'
        assert result[ 'app' ][ 'version' ] == '1.0.0'
        
        # Verify template was copied to user config directory
        user_config_file = directories.user_config_path / 'general.toml'
        assert user_config_file.exists( )
        assert 'discovered-app' in user_config_file.read_text( )
        
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree( temp_dir )


@pytest.mark.asyncio
async def test_330_toml_acquirer_call_with_includes( ):
    ''' TomlAcquirer processes includes configuration structure. '''
    toml_content = '''
[app]
name = "test-app"

includes = [
    "/path/to/includes/*.toml"
]
    '''
    
    file_io = io.StringIO( toml_content )
    directories = MagicMock( )
    distribution = MagicMock( )
    
    # Test basic functionality with includes configuration
    # The actual includes processing would require real files
    acquirer = module.TomlAcquirer( )
    result = await acquirer(
        'test-app',
        directories,
        distribution,
        file = file_io
    )
    
    assert result[ 'app' ][ 'name' ] == 'test-app'
    # The includes configuration is parsed but won't be processed 
    # since no actual include files exist
    assert 'includes' in result[ 'app' ]


@pytest.mark.asyncio
async def test_340_toml_acquirer_discover_copy_template( ):
    ''' TomlAcquirer discovers and copies template when file absent. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        
        directories = MagicMock( )
        directories.user_config_path = temp_path
        
        distribution = MagicMock( )
        distribution.provide_data_location.return_value = (
            temp_path / 'template.toml' )
        
        # Create template file
        template_file = temp_path / 'template.toml'
        template_file.write_text( '''
[app]
name = "template-app"
        ''' )
        
        acquirer = module.TomlAcquirer( )
        result_path = acquirer._discover_copy_template(
            directories, distribution )
        
        assert result_path == temp_path / 'general.toml'
        assert result_path.exists( )
        # Template should be copied to user config
        content = result_path.read_text( )
        assert 'template-app' in content


@pytest.mark.asyncio
async def test_350_toml_acquirer_discover_existing_file( ):
    ''' TomlAcquirer uses existing file when it exists. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        
        directories = MagicMock( )
        directories.user_config_path = temp_path
        
        distribution = MagicMock( )
        
        # Create existing file
        existing_file = temp_path / 'general.toml'
        existing_file.write_text( '''
[app]
name = "existing-app"
        ''' )
        
        acquirer = module.TomlAcquirer( )
        result_path = acquirer._discover_copy_template(
            directories, distribution )
        
        assert result_path == existing_file
        # Distribution should not be called since file exists
        distribution.provide_data_location.assert_not_called( )


@pytest.mark.asyncio
async def test_360_toml_acquirer_acquire_includes_with_files( ):
    ''' TomlAcquirer._acquire_includes processes file specifications. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        
        # Create include files
        include1 = temp_path / 'include1.toml'
        include1.write_text( '''
[database]
host = "db1.example.com"
        ''' )
        
        include2 = temp_path / 'include2.toml'
        include2.write_text( '''
[cache]
host = "cache.example.com"
        ''' )
        
        directories = MagicMock( )
        directories.user_config_path = temp_path
        
        specs = ( str( temp_path ), )
        
        acquirer = module.TomlAcquirer( )
        result = await acquirer._acquire_includes(
            'test-app', directories, specs )
        
        assert len( result ) == 2
        # Check that both includes were processed
        combined = { }
        for include in result:
            combined.update( include )
        
        assert 'database' in combined
        assert 'cache' in combined
        assert combined[ 'database' ][ 'host' ] == 'db1.example.com'
        assert combined[ 'cache' ][ 'host' ] == 'cache.example.com'


@pytest.mark.asyncio
async def test_370_toml_acquirer_acquire_includes_with_directories( ):
    ''' TomlAcquirer._acquire_includes processes directory specifications. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        
        # Create include directory with files
        include_dir = temp_path / 'includes'
        include_dir.mkdir( )
        
        ( include_dir / 'config1.toml' ).write_text( '''
[service]
name = "service1"
        ''' )
        
        ( include_dir / 'config2.toml' ).write_text( '''
[service]
port = 8080
        ''' )
        
        directories = MagicMock( )
        directories.user_config_path = temp_path
        
        # Use directory spec
        specs = ( str( include_dir ), )
        
        acquirer = module.TomlAcquirer( )
        result = await acquirer._acquire_includes(
            'test-app', directories, specs )
        
        assert len( result ) == 2
        # Verify both files were processed
        combined = { }
        for include in result:
            combined.update( include )
        
        assert 'service' in combined
        assert (
            'name' in combined[ 'service' ] or
            'port' in combined[ 'service' ]
        )


@pytest.mark.asyncio
async def test_380_toml_acquirer_acquire_includes_with_formatting( ):
    ''' TomlAcquirer._acquire_includes formats path specifications. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        # home_path = Path.home( )  # Not used
        
        directories = MagicMock( )
        directories.user_config_path = temp_path
        
        # Create a file using formatted path
        formatted_dir = temp_path / 'test-app'
        formatted_dir.mkdir( )
        config_file = formatted_dir / 'app.toml'
        config_file.write_text( '''
[formatted]
value = "success"
        ''' )
        
        # Use formatted specification
        specs = ( '{user_configuration}/test-app/app.toml', )
        
        acquirer = module.TomlAcquirer( )
        result = await acquirer._acquire_includes(
            'test-app', directories, specs )
        
        assert len( result ) == 1
        assert result[ 0 ][ 'formatted' ][ 'value' ] == 'success'


@pytest.mark.asyncio
async def test_390_toml_acquirer_acquire_includes_empty_specs( ):
    ''' TomlAcquirer._acquire_includes handles empty specifications. '''
    directories = MagicMock( )
    
    acquirer = module.TomlAcquirer( )
    result = await acquirer._acquire_includes( 'test-app', directories, ( ) )
    
    assert len( result ) == 0


def test_400_acquirer_abc_protocol( ):
    ''' AcquirerAbc is a proper protocol class. '''
    assert hasattr( module.AcquirerAbc, '__call__' )
    # Check that the protocol defines the expected abstract method
    import inspect
    assert inspect.isabstract( module.AcquirerAbc )
    
    # Verify protocol structure
    assert hasattr( module.AcquirerAbc, '__abstractmethods__' )
    assert '__call__' in module.AcquirerAbc.__abstractmethods__


def test_410_toml_acquirer_immutability( ):
    ''' TomlAcquirer instances are immutable. '''
    acquirer = module.TomlAcquirer( )
    # Should not be able to modify fields after creation
    with pytest.raises( ( AttributeError, TypeError ) ):
        acquirer.main_filename = 'modified.toml'  # type: ignore


def test_420_toml_acquirer_equality( ):
    ''' TomlAcquirer instances with same data are equal. '''
    acquirer1 = module.TomlAcquirer( 
        main_filename = 'test.toml',
        includes_name = 'test_includes'
    )
    acquirer2 = module.TomlAcquirer(
        main_filename = 'test.toml',
        includes_name = 'test_includes'
    )
    assert acquirer1 == acquirer2


def test_430_toml_acquirer_inequality( ):
    ''' TomlAcquirer instances with different data are not equal. '''
    acquirer1 = module.TomlAcquirer( main_filename = 'test.toml' )
    acquirer2 = module.TomlAcquirer( main_filename = 'other.toml' )
    assert acquirer1 != acquirer2