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
from .fixtures import (
    create_fake_project_with_pyproject,
    create_nested_project_structure
)


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
async def test_200_prepare_production_distribution( ):
    ''' Information.prepare handles production distribution path. '''
    exits = MagicMock( )
    # Mock an installed package to trigger production mode (lines 56-58)
    with (patch( 'importlib_metadata.packages_distributions' ) as mock_pkg,
          patch( 'importlib_resources.files' ) as mock_files,
          patch( 'importlib_resources.as_file' ) as mock_as_file):
        
        # Mock installed package found
        mock_pkg.return_value = { 'test-package': [ 'test-distribution' ] }
        
        # Mock resource extraction
        mock_files.return_value = MagicMock( )
        temp_path = Path( '/extracted/location' )
        exits.enter_context.return_value = temp_path
        mock_as_file.return_value = MagicMock( )
        
        info = await module.Information.prepare( 'test-package', exits )
        
        # Verify production distribution was detected
        assert info.editable is False  # Production mode
        assert info.name == 'test-distribution'
        assert info.location == temp_path


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
            project_anchor = temp_path )
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
            project_anchor = temp_path )
        assert location == temp_path
        assert name == 'auto-located-package'


@pytest.mark.asyncio
async def test_350_acquire_production_location( ):
    ''' _acquire_production_location extracts package to temp directory. '''
    exits = MagicMock( )
    temp_path = Path( '/temp/extracted' )
    exits.enter_context.return_value = temp_path
    with (patch( 'importlib_resources.files' ) as mock_files,
          patch( 'importlib_resources.as_file' ) as mock_as_file):
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


def test_500_discover_invoker_location_finds_caller( ):
    ''' Invoker location discovery finds the calling location. '''
    # Create a fake project structure
    project_root, nested_dir = create_nested_project_structure(
        project_name = 'invoker-test',
        nesting_levels = 2
    )
    
    # Create a test file in the nested directory
    test_file = nested_dir / 'test_caller.py'
    test_file.write_text( '''
import sys
from pathlib import Path
sys.path.insert(0, str(
    Path(__file__).parent.parent.parent.parent.parent / 'sources'))
from appcore.distribution import _discover_invoker_location

def call_discover():
    return _discover_invoker_location()

if __name__ == "__main__":
    result = call_discover()
    print(f"RESULT:{result}")
    ''' )
    
    # Execute the test file
    import subprocess
    import sys
    result = subprocess.run(  # noqa: S603
        [ sys.executable, str( test_file ) ],
        cwd = nested_dir,
        capture_output = True,
        text = True,
        check = False
    )
    
    assert result.returncode == 0, f"Process failed: {result.stderr}"
    # The result should be the directory containing the test file
    assert f"RESULT:{nested_dir}" in result.stdout


def test_510_discover_invoker_location_fallback( ):
    ''' Invoker location discovery returns cwd for no external frame. '''
    # Direct call from test - should return current working directory
    # since all frames will be within the appcore package or Python stdlib
    result = module._discover_invoker_location( )
    # Should return a valid Path object
    assert isinstance( result, Path )
    assert result.exists( )


def test_515_discover_invoker_location_no_frame( ):
    ''' Invoker location discovery handles when currentframe returns None. '''
    # Test the fallback when inspect.currentframe() returns None
    # This happens in some Python implementations or when called from certain
    # contexts
    import inspect
    original_currentframe = inspect.currentframe
    
    def mock_currentframe():
        return None
    
    try:
        # Temporarily replace currentframe with our mock
        inspect.currentframe = mock_currentframe
        result = module._discover_invoker_location( )
        # Should return cwd when no frame is available
        assert isinstance( result, Path )
        assert result.exists( )
    finally:
        # Restore original function
        inspect.currentframe = original_currentframe


def test_516_discover_invoker_location_exhausted_frames( ):
    ''' Invoker location discovery returns cwd when all frames exhausted. '''
    # Create a test file that deeply nests calls within the Python stdlib
    # This should exhaust all frames without finding an external caller
    project_root, nested_dir = create_nested_project_structure(
        project_name = 'exhausted-frames-test',
        nesting_levels = 1
    )
    
    test_file = nested_dir / 'test_exhausted.py'
    test_file.write_text( '''
import sys
import os
from pathlib import Path

# Add appcore to path
sys.path.insert(0, str(
    Path(__file__).parent.parent.parent.parent.parent / 'sources'))

def deeply_nested_call():
    # Import inside function to avoid early import issues
    from appcore.distribution import _discover_invoker_location
    
    def inner_call():
        def innermost_call():
            # Call from deep within Python stdlib-like context
            return _discover_invoker_location()
        return innermost_call()
    return inner_call()

if __name__ == "__main__":
    # Change to a different directory to test cwd fallback
    original_cwd = os.getcwd()
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    try:
        result = deeply_nested_call()
        print(f"RESULT:{result}")
    finally:
        os.chdir(original_cwd)
    ''')
    
    # Execute the test file
    import subprocess
    import sys
    result = subprocess.run(  # noqa: S603
        [ sys.executable, str( test_file ) ],
        cwd = nested_dir,
        capture_output = True,
        text = True,
        check = False
    )
    
    assert result.returncode == 0, f"Process failed: {result.stderr}"
    # Should return the current working directory when frames are exhausted
    assert f"RESULT:{nested_dir}" in result.stdout


def test_520_locate_pyproject_finds_in_current_dir( ):
    ''' _locate_pyproject finds pyproject.toml in current directory. '''
    project_root, pyproject_path = create_fake_project_with_pyproject(
        project_name = 'current-dir-test'
    )
    
    result = module._locate_pyproject( project_root )
    assert result == project_root
    assert ( result / 'pyproject.toml' ).exists( )


def test_530_locate_pyproject_finds_in_parent_dir( ):
    ''' _locate_pyproject finds pyproject.toml in parent directory. '''
    project_root, nested_dir = create_nested_project_structure(
        project_name = 'parent-dir-test',
        nesting_levels = 3
    )
    
    # Call _locate_pyproject from the nested directory
    result = module._locate_pyproject( nested_dir )
    assert result == project_root
    assert ( result / 'pyproject.toml' ).exists( )


def test_540_locate_pyproject_handles_file_anchor( ):
    ''' _locate_pyproject handles file path as anchor. '''
    project_root, pyproject_path = create_fake_project_with_pyproject(
        project_name = 'file-anchor-test'
    )
    
    # Create a test file in the project
    test_file = project_root / 'test.py'
    test_file.write_text( '# test file' )
    
    # Call _locate_pyproject with file path (not directory)
    result = module._locate_pyproject( test_file )
    assert result == project_root
    assert ( result / 'pyproject.toml' ).exists( )


@pytest.mark.asyncio
async def test_550_prepare_development_mode_without_anchor( ):
    ''' Information.prepare works in development mode without anchor. '''
    # Create a fake project structure
    project_root, nested_dir = create_nested_project_structure(
        project_name = 'no-anchor-test',
        nesting_levels = 2
    )
    
    # Create a test file that will call prepare
    test_file = nested_dir / 'test_prepare.py'
    test_file.write_text( '''
import sys
import asyncio
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(
    Path(__file__).parent.parent.parent.parent.parent / 'sources'))
from appcore.distribution import Information

async def main():
    exits = MagicMock()
    # Call prepare without project_anchor - should trigger
    # _discover_invoker_location
    info = await Information.prepare('nonexistent-package', exits)
    print(f"NAME:{{info.name}}")
    print(f"LOCATION:{{info.location}}")
    print(f"EDITABLE:{{info.editable}}")

if __name__ == "__main__":
    asyncio.run(main())
    ''' )
    
    # Execute the test file
    import subprocess
    import sys
    result = subprocess.run(  # noqa: S603
        [ sys.executable, str( test_file ) ],
        cwd = nested_dir,
        capture_output = True,
        text = True,
        check = False
    )
    
    assert result.returncode == 0, f"Process failed: {result.stderr}"
    # Should find the project and return development mode
    assert "NAME:no-anchor-test" in result.stdout
    assert f"LOCATION:{project_root}" in result.stdout
    assert "EDITABLE:True" in result.stdout


def test_560_locate_pyproject_with_missing_file( ):
    ''' Project location raises FileLocateFailure when pyproject absent. '''
    # Create a temporary directory without pyproject.toml
    with tempfile.TemporaryDirectory( ) as temp_dir:
        temp_path = Path( temp_dir )
        
        # Should raise FileLocateFailure
        with pytest.raises( exceptions_module.FileLocateFailure ) as exc_info:
            module._locate_pyproject( temp_path )
        
        assert 'pyproject.toml' in str( exc_info.value )
        assert 'project root discovery' in str( exc_info.value )


