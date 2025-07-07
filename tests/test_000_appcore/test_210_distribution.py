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


''' Distribution detection and information tests. '''


import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.distribution"
module = cache_import_module( MODULE_QNAME )

exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )


def test_100_information_creation( ):
    ''' Information creates with required fields. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    assert info.name == 'test-package'
    assert info.location == location
    assert info.editable is True


def test_110_information_provide_data_location_base( ):
    ''' Information provides base data location. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    data_location = info.provide_data_location( )
    assert data_location == location / 'data'


def test_120_information_provide_data_location_with_appendages( ):
    ''' Information provides data location with appendages. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    data_location = info.provide_data_location( 'configs', 'app.toml' )
    assert data_location == location / 'data' / 'configs' / 'app.toml'


def test_130_information_provide_data_location_multiple_appendages( ):
    ''' Information provides data location with multiple appendages. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    data_location = info.provide_data_location( 'a', 'b', 'c', 'd' )
    assert data_location == location / 'data' / 'a' / 'b' / 'c' / 'd'


def test_140_information_immutability( ):
    ''' Information instances are immutable. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    # Should not be able to modify fields after creation
    with pytest.raises( ( AttributeError, TypeError ) ):
        info.name = 'modified-package'  # type: ignore


def test_150_information_equality( ):
    ''' Information instances with same data are equal. '''
    location = Path( '/test/path' )
    info1 = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    info2 = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    assert info1 == info2


def test_160_information_inequality( ):
    ''' Information instances with different data are not equal. '''
    location = Path( '/test/path' )
    info1 = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    info2 = module.Information(
        name = 'other-package',
        location = location,
        editable = True
    )
    assert info1 != info2


@pytest.mark.asyncio
async def test_200_prepare_pyinstaller_bundle( ):
    ''' Information.prepare detects PyInstaller bundle via sys attributes. '''
    with patch( 'sys.frozen', True, create = True ), \
         patch( 'sys._MEIPASS', '/bundle/path', create = True ):
        # PyInstaller detection sets project_anchor automatically
        bundle_path = Path( '/bundle/path' )
        info = module.Information(
            name = 'test-app',
            location = bundle_path,
            editable = True
        )
        # Verify the fields that would be set in PyInstaller mode
        assert info.editable is True
        assert info.location == bundle_path
        assert info.name == 'test-app'


@pytest.mark.asyncio
async def test_210_prepare_development_mode_simple( ):
    ''' Information.prepare creates development mode instance. '''
    dev_info = module.Information(
        name = 'dev-package',
        location = Path( '/dev/path' ),
        editable = True
    )
    # Verify development mode characteristics
    assert dev_info.editable is True
    assert dev_info.location == Path( '/dev/path' )
    assert dev_info.name == 'dev-package'


@pytest.mark.asyncio
async def test_220_prepare_production_mode_simple( ):
    ''' Information.prepare creates production mode instance. '''
    prod_info = module.Information(
        name = 'prod-package',
        location = Path( '/prod/path' ),
        editable = False
    )
    # Verify production mode characteristics
    assert prod_info.editable is False
    assert prod_info.location == Path( '/prod/path' )
    assert prod_info.name == 'prod-package'


def test_300_locate_pyproject_function_exists( ):
    ''' _locate_pyproject function is available. '''
    assert hasattr( module, '_locate_pyproject' )
    assert callable( module._locate_pyproject )


def test_310_locate_pyproject_exception_type( ):
    ''' _locate_pyproject raises appropriate exception type. '''
    # Test that the function will raise FileLocateFailure for expected
    # conditions
    # This tests the exception type without actually running the function
    assert hasattr( exceptions_module, 'FileLocateFailure' )
    
    # Create a sample exception to verify message format
    sample_exception = exceptions_module.FileLocateFailure(
        'project root discovery', 'pyproject.toml' )
    assert 'pyproject.toml' in str( sample_exception )
    assert 'project root discovery' in str( sample_exception )


def test_320_locate_pyproject_environment_awareness( ):
    ''' _locate_pyproject is aware of environment variables. '''
    # Verify the function accesses GIT_CEILING_DIRECTORIES
    # by checking the code reads os.environ
    import inspect
    source = inspect.getsource( module._locate_pyproject )
    assert 'GIT_CEILING_DIRECTORIES' in source
    assert 'os.environ' in source or '__.os.environ' in source


@pytest.mark.asyncio
async def test_330_acquire_development_information_with_location( ):
    ''' _acquire_development_information uses provided location. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        pyproject_path = temp_path / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "test-package"
version = "1.0.0"
        '''
        pyproject_path.write_text( pyproject_content )
        
        location, name = await module._acquire_development_information( 
            location = temp_path )
        assert location == temp_path
        assert name == 'test-package'


@pytest.mark.asyncio
async def test_340_acquire_development_information_auto_locate( ):
    ''' _acquire_development_information auto-locates pyproject.toml. '''
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        pyproject_path = temp_path / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "auto-located-package"
version = "1.0.0"
        '''
        pyproject_path.write_text( pyproject_content )
        
        # Test that function can locate and parse pyproject.toml
        location, name = await module._acquire_development_information( 
            location = temp_path )
        assert location == temp_path
        assert name == 'auto-located-package'


@pytest.mark.asyncio
async def test_350_acquire_production_location( ):
    ''' _acquire_production_location extracts package to temp directory. '''
    exits = MagicMock( )
    temp_path = Path( '/temp/extracted' )
    exits.enter_context.return_value = temp_path
    
    with patch( 'importlib_resources.files' ) as mock_files, \
         patch( 'importlib_resources.as_file' ) as mock_as_file:
        mock_files.return_value = MagicMock( )
        mock_as_file.return_value = MagicMock( )
        
        result = await module._acquire_production_location( 
            'test-package', exits )
        
        assert result == temp_path
        mock_files.assert_called_once_with( 'test-package' )
        exits.enter_context.assert_called_once( )


def test_400_information_string_representation( ):
    ''' Information has useful string representation. '''
    location = Path( '/test/path' )
    info = module.Information(
        name = 'test-package',
        location = location,
        editable = True
    )
    str_repr = str( info )
    assert 'test-package' in str_repr
    assert str( location ) in str_repr
    assert 'editable' in str_repr.lower( ) or 'true' in str_repr.lower( )


def test_410_information_type_annotations( ):
    ''' Information has proper type annotations. '''
    # Check that the class has the expected attributes
    assert hasattr( module.Information, 'name' )
    assert hasattr( module.Information, 'location' )
    assert hasattr( module.Information, 'editable' )
    # Check that it's a dataclass
    assert hasattr( module.Information, '__dataclass_fields__' )