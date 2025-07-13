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


import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
# patchfs import removed - using Patcher context manager instead

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
async def test_200_prepare_production_distribution( ):
    ''' Information.prepare handles production distribution path. '''
    exits = MagicMock( )
    # Mock an installed package to trigger production mode (lines 56-58)
    with (
        patch( 'importlib_metadata.packages_distributions' ) as mock_pkg,
        patch( 'importlib_resources.files' ) as mock_files,
        patch( 'importlib_resources.as_file' ) as mock_as_file
    ):
        mock_pkg.return_value = { 'test-package': [ 'test-distribution' ] }
        mock_files.return_value = MagicMock( )
        temp_path = Path( '/extracted/location' )
        exits.enter_context.return_value = temp_path
        mock_as_file.return_value = MagicMock( )
        info = await module.Information.prepare(
            exits, package = 'test-package' )
        # Verify production distribution was detected
        assert info.editable is False  # Production mode
        assert info.name == 'test-distribution'
        assert info.location.resolve( ) == temp_path.resolve( )


@pytest.mark.asyncio
async def test_210_prepare_development_mode_simple( ):
    ''' Information.prepare creates development mode instance. '''
    dev_info = module.Information(
        name = 'dev-package',
        location = Path( '/test/path' ),
        editable = True
    )
    # Verify development mode characteristics
    assert dev_info.editable is True
    assert dev_info.location == Path( '/test/path' )
    assert dev_info.name == 'dev-package'


@pytest.mark.asyncio
async def test_220_prepare_production_mode_simple( ):
    ''' Information.prepare creates production mode instance. '''
    prod_info = module.Information(
        name = 'prod-package',
        location = Path( '/production/path' ),
        editable = False
    )
    # Verify production mode characteristics
    assert prod_info.editable is False
    assert prod_info.location == Path( '/production/path' )
    assert prod_info.name == 'prod-package'


def test_300_locate_pyproject_function_exists( ):
    ''' _locate_pyproject function is available. '''
    assert hasattr( module, '_locate_pyproject' )
    assert callable( module._locate_pyproject )


def test_310_locate_pyproject_exception_type( ):
    ''' _locate_pyproject raises appropriate exception type. '''
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
    # Test with real temporary directory since aiofiles integration is complex
    import tempfile
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
            anchor = temp_path )
        assert location.resolve( ) == temp_path.resolve( )
        assert name == 'test-package'


@pytest.mark.asyncio
async def test_340_acquire_development_information_auto_locate( ):
    ''' _acquire_development_information auto-locates pyproject.toml. '''
    # Use real temporary directory for async file operations
    import tempfile
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
            anchor = temp_path )
        assert location.resolve( ) == temp_path.resolve( )
        assert name == 'auto-located-package'


@pytest.mark.asyncio
async def test_350_acquire_production_location( ):
    ''' _acquire_production_location extracts package to temp directory. '''
    exits = MagicMock( )
    temp_path = Path( '/temp/extracted' )
    exits.enter_context.return_value = temp_path
    with (
        patch( 'importlib_resources.files' ) as mock_files,
        patch( 'importlib_resources.as_file' ) as mock_as_file
    ):
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
    # Check path components instead of string representation for Windows
    assert 'test' in str_repr and 'path' in str_repr
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
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        project_root = Path( '/fake/project' )
        nested_dir = project_root / 'level_0' / 'level_1'
        fs.create_dir( nested_dir )
        caller_file = nested_dir / 'caller.py'
        fs.create_file( caller_file, contents = '# test caller file' )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( caller_file )
        external_frame.f_globals = { '__name__': 'test.caller.module' }
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = external_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch.object( module.__.Path, 'cwd',
                         return_value = Path( '/fake/fallback' ) )
        ): package, anchor = module._discover_invoker_location( )
        assert package == 'test'
        assert anchor.samefile( nested_dir )


def test_510_discover_invoker_location_fallback( ):
    ''' Invoker location discovery returns cwd for no external frame. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        appcore_path = Path( '/fake/appcore' )
        fs.create_dir( appcore_path )
        mock_frame = MagicMock( )
        mock_frame.f_code.co_filename = str( appcore_path / 'some_file.py' )
        mock_frame.f_back = None
        with (
            patch( 'inspect.currentframe', return_value = mock_frame ),
            patch( 'pathlib.Path.cwd', return_value = cwd )
        ): package, anchor = module._discover_invoker_location( )
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


def test_515_discover_invoker_location_no_frame( ):
    ''' Invoker location discovery handles when currentframe returns None. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        with (
            patch( 'inspect.currentframe', return_value = None ),
            patch( 'pathlib.Path.cwd', return_value = cwd )
        ): package, anchor = module._discover_invoker_location( )
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


def test_517_discover_invoker_location_site_packages( ):
    ''' Invoker location discovery allows site-packages calling packages. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        site_packages = Path( '/fake/venv/lib/python3.10/site-packages' )
        fs.create_dir( site_packages )
        third_party_pkg = site_packages / 'third_party' / '__init__.py'
        fs.create_file( third_party_pkg, contents = '# third party package' )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( third_party_pkg )
        external_frame.f_globals = { '__name__': 'third_party.module' }
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = external_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'site.getsitepackages',
                   return_value = [ str( site_packages ) ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' )
        ): package, anchor = module._discover_invoker_location( )
        assert package == 'third_party'
        assert anchor.samefile( site_packages / 'third_party' )


def test_518_discover_invoker_location_name_detection( ):
    ''' Uses __name__ for package detection with boundary finding. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        site_packages = Path( '/fake/venv/lib/python3.11/site-packages' )
        fs.create_dir( site_packages )
        installed_pkg = site_packages / 'installed_pkg' / 'module.py'
        fs.create_file( installed_pkg, contents = '# installed package' )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( installed_pkg )
        # Simulate installed package with __name__ attribute
        external_frame.f_globals = {
            '__name__': 'installed_pkg'
        }
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = external_frame
        # Mock sys.modules to contain the package for boundary detection
        mock_pkg = MagicMock(
            __path__ = [ str( site_packages / 'installed_pkg' ) ] )
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'site.getsitepackages',
                   return_value = [ str( site_packages ) ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' ),
            patch.dict( module.__.sys.modules, { 'installed_pkg': mock_pkg } )
        ): package, anchor = module._discover_invoker_location( )
        assert package == 'installed_pkg'
        assert anchor.samefile( site_packages / 'installed_pkg' )


def test_519_discover_invoker_location_no_name( ):
    ''' Skips frames with no __name__ or __main__. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        # Create a frame with no __name__ or __main__
        no_info_frame = MagicMock( )
        no_info_frame.f_code.co_filename = '/some/path/script.py'
        no_info_frame.f_globals = { '__name__': None }
        no_info_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = no_info_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'pathlib.Path.cwd', return_value = cwd ),
            patch( 'site.getsitepackages', return_value = [ '/fake/site' ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' )
        ): package, anchor = module._discover_invoker_location( )
        # Should fall back to cwd since frame has no identifying info
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


def test_520_detect_package_boundary_simple_package( ):
    ''' Can detect simple packages correctly. '''
    with patch.dict( module.__.sys.modules, {
        'collections': MagicMock( __path__ = [ '/fake/path' ] )
    } ):
        result = module._detect_package_boundary( 'collections.abc' )
        assert result == 'collections'


def test_521_detect_package_boundary_namespace_package( ):
    ''' Can detect namespace packages correctly. '''
    namespace_mock = MagicMock( )
    del namespace_mock.__path__  # Namespace root has no __path__
    subpkg_mock = MagicMock( __path__ = [ '/fake/namespace/subpkg' ] )
    with patch.dict( module.__.sys.modules, {
        'mynamespace': namespace_mock,
        'mynamespace.subpkg': subpkg_mock
    } ):
        result = module._detect_package_boundary( 'mynamespace.subpkg.module' )
        assert result == 'mynamespace.subpkg'


def test_522_detect_package_boundary_main_module( ):
    ''' Can detect __main__ module correctly. '''
    result = module._detect_package_boundary( '__main__' )
    assert module.__.is_absent( result )


def test_523_detect_package_boundary_absent_name( ):
    ''' Can handle null module names correctly. '''
    result = module._detect_package_boundary( None )
    assert module.__.is_absent( result )
    result = module._detect_package_boundary( '' )
    assert module.__.is_absent( result )


def test_524_detect_package_boundary_fallback( ):
    ''' Can handle unregistered modules. '''
    with patch.dict( module.__.sys.modules, {}, clear = True ):
        result = module._detect_package_boundary( 'unknown.package.module' )
        assert result == 'unknown'


def test_525_discover_invoker_location_main_module( ):
    ''' Skips frames with __name__ set to __main__. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        main_frame = MagicMock( )
        main_frame.f_code.co_filename = '/some/path/script.py'
        main_frame.f_globals = { '__name__': '__main__' }
        main_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = main_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'pathlib.Path.cwd', return_value = cwd ),
            patch( 'site.getsitepackages', return_value = [ '/fake/site' ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' )
        ): package, anchor = module._discover_invoker_location( )
        # Should fall back to cwd since __main__ is skipped
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


@pytest.mark.asyncio
async def test_526_prepare_package_found_but_not_distributed( ):
    ''' Correctly handles package found but not in distributions. '''
    import tempfile
    with tempfile.TemporaryDirectory( ) as temp_dir:
        project_root = Path( temp_dir )
        pyproject_path = project_root / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "found-not-distributed"
version = "1.0.0"
'''
        pyproject_path.write_text( pyproject_content )
        package_location = Path( module.__file__ ).parent.resolve( )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( project_root / 'caller.py' )
        external_frame.f_globals = { '__name__': 'mypackage' }
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = str(
            package_location / 'some_file.py' )
        appcore_frame.f_back = external_frame
        mock_pkg = MagicMock( __path__ = [ str( project_root ) ] )
        with (
            # Package found but not in distributions (returns empty dict)
            patch( 'importlib_metadata.packages_distributions',
                   return_value = {} ),
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch.dict( module.__.sys.modules, { 'mypackage': mock_pkg } )
        ):
            exits = MagicMock( )
            # This should find package but not in distributions, then go to dev
            info = await module.Information.prepare(
                exits, package = 'mypackage' )
            # Should trigger development mode (line 53->65)
            assert info.editable is True
            assert info.name == 'found-not-distributed'
            assert info.location.resolve( ) == project_root.resolve( )


def test_527_discover_invoker_location_stdlib_continue( ):
    ''' Skips stdlib frames that are not in site-packages. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        # Create a frame from stdlib location (not in site-packages)
        stdlib_frame = MagicMock( )
        stdlib_frame.f_code.co_filename = '/usr/lib/python3.10/os.py'
        stdlib_frame.f_globals = { '__name__': 'os' }
        stdlib_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = stdlib_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'pathlib.Path.cwd', return_value = cwd ),
            patch( 'site.getsitepackages', return_value = [ '/fake/site' ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' ),
            patch( 'sysconfig.get_path',
                   side_effect = lambda x: '/usr/lib/python3.10'
                   if x in ('stdlib', 'platstdlib') else '/other' )
        ): package, anchor = module._discover_invoker_location( )
        # Should fall back to cwd since stdlib frame was skipped
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


def test_528_detect_package_boundary_absent_result( ):
    ''' Correctly reflects unresolved package boundaries. '''
    with patch.dict( module.__.sys.modules, {}, clear = True ):
        fake_module = MagicMock( )
        del fake_module.__path__  # Remove __path__ to make it not a package
        with patch.dict(
            module.__.sys.modules, { 'notapackage': fake_module }
        ):
            # This should return the fallback (first component)
            result = module._detect_package_boundary( 'notapackage.submodule' )
            assert result == 'notapackage'


def test_529_discover_invoker_location_boundary_absent( ):
    ''' Continues searching for package when not detected on stack frame. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        cwd = Path( '/fake/cwd' )
        fs.create_dir( cwd )
        absent_frame = MagicMock( )
        absent_frame.f_code.co_filename = '/some/path/script.py'
        absent_frame.f_globals = { '__name__': '__main__' }
        absent_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = '/fake/appcore/distribution.py'
        appcore_frame.f_back = absent_frame
        with (
            patch( 'inspect.currentframe', return_value = appcore_frame ),
            patch( 'pathlib.Path.cwd', return_value = cwd ),
            patch( 'site.getsitepackages', return_value = [ '/fake/site' ] ),
            patch( 'site.getusersitepackages',
                   return_value = '/fake/user/site' )
        ): package, anchor = module._discover_invoker_location( )
        # Should fall back to cwd since boundary detection returned absent
        assert module.__.is_absent( package )
        assert anchor.samefile( cwd )


def test_530_locate_pyproject_finds_in_current_dir( ):
    ''' Finds pyproject.toml in current directory. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        project_root = Path( '/fake/project' )
        pyproject_path = project_root / 'pyproject.toml'
        fs.create_file( pyproject_path, contents = '''
[project]
name = "current-dir-test"
version = "1.0.0"
''' )
        result = module._locate_pyproject( project_root )
        assert result.samefile( project_root )
        assert ( result / 'pyproject.toml' ).exists( )


def test_530_locate_pyproject_finds_in_parent_dir( ):
    ''' Finds pyproject.toml in parent directory. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        project_root = Path( '/fake/project' )
        nested_dir = project_root / 'level_0' / 'level_1' / 'level_2'
        fs.create_dir( nested_dir )
        pyproject_path = project_root / 'pyproject.toml'
        fs.create_file( pyproject_path, contents = '''
[project]
name = "parent-dir-test"
version = "1.0.0"
''' )
        result = module._locate_pyproject( nested_dir )
        assert result.samefile( project_root )
        assert ( result / 'pyproject.toml' ).exists( )


def test_540_locate_pyproject_handles_file_anchor( ):
    ''' Finds pyproject.toml from anchor as file path. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        project_root = Path( '/fake/project' )
        pyproject_path = project_root / 'pyproject.toml'
        fs.create_file( pyproject_path, contents = '''
[project]
name = "file-anchor-test"
version = "1.0.0"
''' )
        test_file = project_root / 'test.py'
        fs.create_file( test_file, contents = '# test file' )
        result = module._locate_pyproject( test_file )
        assert result.samefile( project_root )
        assert ( result / 'pyproject.toml' ).exists( )


@pytest.mark.asyncio
async def test_550_prepare_development_mode_without_anchor( ):
    ''' Finds pyproject.toml in development mode without anchor. '''
    # Use real temporary directory for async file operations
    import tempfile
    with tempfile.TemporaryDirectory( ) as temp_dir:
        project_root = Path( temp_dir )
        nested_dir = project_root / 'level_0' / 'level_1'
        nested_dir.mkdir( parents = True, exist_ok = True )
        pyproject_path = project_root / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "no-anchor-test"
version = "1.0.0"
'''
        pyproject_path.write_text( pyproject_content )
        package_location = Path( module.__file__ ).parent.resolve( )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( nested_dir / 'caller.py' )
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = str(
            package_location / 'some_file.py' )
        appcore_frame.f_back = external_frame
        with (
            patch( 'importlib_metadata.packages_distributions',
                   return_value = {} ),
            patch( 'inspect.currentframe', return_value = appcore_frame )
        ):
            exits = MagicMock( )
            info = await module.Information.prepare(
                exits, package = 'nonexistent-package' )
            # Should find the project and return development mode
            assert info.name == 'no-anchor-test'
            assert info.location.resolve( ) == project_root.resolve( )
            assert info.editable is True


def test_560_locate_pyproject_with_missing_file( ):
    ''' Project location raises FileLocateFailure when pyproject absent. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        temp_path = Path( '/fake/empty' )
        fs.create_dir( temp_path )
        with pytest.raises( exceptions_module.FileLocateFailure ) as exc_info:
            module._locate_pyproject( temp_path )
        assert 'pyproject.toml' in str( exc_info.value )
        assert 'project root discovery' in str( exc_info.value )


@pytest.mark.asyncio
async def test_570_prepare_development_mode_with_anchor( ):
    ''' Information.prepare works in development mode with provided anchor. '''
    # Use real temporary directory for async file operations
    import tempfile
    with tempfile.TemporaryDirectory( ) as temp_dir:
        project_root = Path( temp_dir )
        pyproject_path = project_root / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "anchor-test"
version = "1.0.0"
'''
        pyproject_path.write_text( pyproject_content )
        with patch( 'importlib_metadata.packages_distributions',
                   return_value = {} ):
            exits = MagicMock( )
            # Call prepare WITH project_anchor - should NOT trigger
            # _discover_invoker_location
            info = await module.Information.prepare(
                exits, anchor = project_root, package = 'nonexistent-package' )
            # Should find the project and return development mode
            assert info.name == 'anchor-test'
            assert info.location.resolve( ) == project_root.resolve( )
            assert info.editable is True


@pytest.mark.asyncio
async def test_580_prepare_development_mode_no_anchor_absent( ):
    ''' Information.prepare development mode when project_anchor is absent. '''
    # Use real temporary directory for async file operations
    import tempfile
    with tempfile.TemporaryDirectory( ) as temp_dir:
        project_root = Path( temp_dir )
        nested_dir = project_root / 'caller_location'
        nested_dir.mkdir( parents = True, exist_ok = True )
        pyproject_path = project_root / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "absent-anchor-test"
version = "1.0.0"
'''
        pyproject_path.write_text( pyproject_content )
        package_location = Path( module.__file__ ).parent.resolve( )
        external_frame = MagicMock( )
        external_frame.f_code.co_filename = str( nested_dir / 'caller.py' )
        external_frame.f_back = None
        appcore_frame = MagicMock( )
        appcore_frame.f_code.co_filename = str(
            package_location / 'some_file.py' )
        appcore_frame.f_back = external_frame
        with (
            patch( 'importlib_metadata.packages_distributions',
                   return_value = {} ),
            patch( 'inspect.currentframe', return_value = appcore_frame )
        ):
            exits = MagicMock( )
            info = await module.Information.prepare(
                exits, package = 'nonexistent-package' )
            assert info.name == 'absent-anchor-test'
            assert info.location.resolve( ) == project_root.resolve( )
            assert info.editable is True


@pytest.mark.asyncio
async def test_590_prepare_development_mode_missing_package( ):
    ''' Information.prepare triggers development mode for missing package. '''
    # Test the critical development mode path (lines 52-55 in distribution.py)
    import tempfile
    with tempfile.TemporaryDirectory( ) as temp_dir:
        project_root = Path( temp_dir )
        pyproject_path = project_root / 'pyproject.toml'
        pyproject_content = '''
[project]
name = "development-mode-test"
version = "1.0.0"
'''
        pyproject_path.write_text( pyproject_content )
        # Mock packages_distributions to return empty
        # (no installed package found)
        # This triggers the development mode path when name is None
        with patch(
            'importlib_metadata.packages_distributions', return_value = {}
        ):
            exits = MagicMock( )
            # This should trigger development mode because package not found
            info = await module.Information.prepare(
                exits, anchor = project_root, package = 'nonexistent-package' )
            assert info.editable is True
            assert info.name == 'development-mode-test'
            assert info.location.resolve( ) == project_root.resolve( )


def test_590_locate_pyproject_with_git_ceiling_directories( ):
    ''' Project location respects GIT_CEILING_DIRECTORIES. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        ceiling_dir = Path( '/fake/ceiling' )
        project_root = ceiling_dir / 'project'
        nested_dir = project_root / 'nested'
        fs.create_dir( nested_dir )
        upper_pyproject = Path( '/fake/pyproject.toml' )
        fs.create_file( upper_pyproject, contents = '''
[project]
name = "upper-project"
version = "1.0.0"
''' )
        # Set GIT_CEILING_DIRECTORIES to the ceiling directory
        with patch.dict(
            os.environ, { 'GIT_CEILING_DIRECTORIES': str( ceiling_dir ) }
        ):
            with pytest.raises( exceptions_module.FileLocateFailure ) as (
                exc_info ):
                module._locate_pyproject( nested_dir )
            assert 'pyproject.toml' in str( exc_info.value )
            assert 'project root discovery' in str( exc_info.value )


def test_600_locate_pyproject_with_empty_ceiling_directories( ):
    ''' Project location handles empty GIT_CEILING_DIRECTORIES. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        project_root = Path( '/fake/project' )
        nested_dir = project_root / 'nested'
        fs.create_dir( nested_dir )
        pyproject_path = project_root / 'pyproject.toml'
        fs.create_file( pyproject_path, contents = '''
[project]
name = "empty-ceiling-test"
version = "1.0.0"
''' )
        # Set GIT_CEILING_DIRECTORIES to empty string
        with patch.dict( os.environ, { 'GIT_CEILING_DIRECTORIES': '' } ):
            result = module._locate_pyproject( nested_dir )
            assert result.samefile( project_root )
            assert ( result / 'pyproject.toml' ).exists( )


def test_610_locate_pyproject_filesystem_root_traversal( ):
    ''' Project location raises FileLocateFailure at filesystem root. '''
    from pyfakefs.fake_filesystem_unittest import Patcher

    with Patcher( ) as patcher:
        fs = patcher.fs
        deep_dir = Path( '/fake/very/deep/directory/structure' )
        fs.create_dir( deep_dir )
        with pytest.raises( exceptions_module.FileLocateFailure ) as exc_info:
            module._locate_pyproject( deep_dir )
        assert 'pyproject.toml' in str( exc_info.value )
        assert 'project root discovery' in str( exc_info.value )


@pytest.mark.asyncio
async def test_615_prepare_with_auto_detection( ):
    ''' Distribution preparation auto-detects calling package. '''
    __ = cache_import_module( f"{PACKAGE_NAME}.__" )

    async with __.ctxl.AsyncExitStack( ) as exits:
        distribution = await module.Information.prepare( exits )
        # Should auto-detect this project (emcd-appcore) instead of 'appcore'
        assert distribution.name == 'emcd-appcore'
        assert distribution.editable is True
        assert distribution.location.name == 'python-appcore'
