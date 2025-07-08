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


''' Application information and platform directories tests. '''


import platformdirs
import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.application"
module = cache_import_module( MODULE_QNAME )


def test_100_information_default_creation( ):
    ''' Information creates with package name as default. '''
    app_info = module.Information( )
    assert app_info.name == PACKAGE_NAME
    assert app_info.publisher is None
    assert app_info.version is None


def test_110_information_custom_name( ):
    ''' Information accepts custom application name. '''
    app_info = module.Information( name = 'custom-app' )
    assert app_info.name == 'custom-app'
    assert app_info.publisher is None
    assert app_info.version is None


def test_120_information_with_publisher( ):
    ''' Information accepts publisher information. '''
    app_info = module.Information(
        name = 'test-app',
        publisher = 'Test Company'
    )
    assert app_info.name == 'test-app'
    assert app_info.publisher == 'Test Company'
    assert app_info.version is None


def test_130_information_with_version( ):
    ''' Information accepts version information. '''
    app_info = module.Information(
        name = 'test-app',
        version = '1.2.3'
    )
    assert app_info.name == 'test-app'
    assert app_info.publisher is None
    assert app_info.version == '1.2.3'


def test_140_information_complete( ):
    ''' Information accepts all fields together. '''
    app_info = module.Information(
        name = 'test-app',
        publisher = 'Test Company',
        version = '1.2.3'
    )
    assert app_info.name == 'test-app'
    assert app_info.publisher == 'Test Company'
    assert app_info.version == '1.2.3'


def test_150_produce_platform_directories_minimal( ):
    ''' Platform directory creator uses app name only. '''
    app_info = module.Information( name = 'test-app' )
    dirs = app_info.produce_platform_directories( )
    assert isinstance( dirs, platformdirs.PlatformDirs )
    assert 'test-app' in str( dirs.user_config_path )
    assert 'test-app' in str( dirs.user_data_path )


def test_160_produce_platform_directories_with_publisher( ):
    ''' produce_platform_directories includes publisher when provided. '''
    app_info = module.Information(
        name = 'test-app',
        publisher = 'Test Company'
    )
    dirs = app_info.produce_platform_directories( )
    assert isinstance( dirs, platformdirs.PlatformDirs )
    # Publisher should be included in path structure
    config_path = str( dirs.user_config_path )
    assert 'test-app' in config_path


def test_170_produce_platform_directories_with_version( ):
    ''' produce_platform_directories includes version when provided. '''
    app_info = module.Information(
        name = 'test-app',
        version = '1.2.3'
    )
    dirs = app_info.produce_platform_directories( )
    assert isinstance( dirs, platformdirs.PlatformDirs )
    # Version should be included in path structure
    config_path = str( dirs.user_config_path )
    assert 'test-app' in config_path


def test_180_produce_platform_directories_complete( ):
    ''' produce_platform_directories works with all fields provided. '''
    app_info = module.Information(
        name = 'test-app',
        publisher = 'Test Company',
        version = '1.2.3'
    )
    dirs = app_info.produce_platform_directories( )
    assert isinstance( dirs, platformdirs.PlatformDirs )
    config_path = str( dirs.user_config_path )
    assert 'test-app' in config_path


def test_190_platform_directories_ensure_exists( ):
    ''' Platform directory creator ensures directories exist. '''
    app_info = module.Information( name = 'test-app-ensure' )
    dirs = app_info.produce_platform_directories( )
    # PlatformDirs was created with ensure_exists=True
    # Directories should be created when accessed
    assert dirs.user_config_path.exists( )
    assert dirs.user_data_path.exists( )
    assert dirs.user_cache_path.exists( )


def test_200_information_immutability( ):
    ''' Information instances are immutable. '''
    app_info = module.Information( name = 'test-app' )
    # Should not be able to modify fields after creation
    with pytest.raises( ( AttributeError, TypeError ) ):
        app_info.name = 'modified-app'  # type: ignore


def test_210_information_equality( ):
    ''' Information instances with same data are equal. '''
    app1 = module.Information(
        name = 'test-app',
        publisher = 'Test Company',
        version = '1.0'
    )
    app2 = module.Information(
        name = 'test-app',
        publisher = 'Test Company',
        version = '1.0'
    )
    assert app1 == app2


def test_220_information_inequality( ):
    ''' Information instances with different data are not equal. '''
    app1 = module.Information( name = 'test-app' )
    app2 = module.Information( name = 'other-app' )
    assert app1 != app2


def test_230_platform_directories_different_apps( ):
    ''' Different application names produce different platform directories. '''
    app1 = module.Information( name = 'app-one' )
    app2 = module.Information( name = 'app-two' )
    dirs1 = app1.produce_platform_directories( )
    dirs2 = app2.produce_platform_directories( )
    assert dirs1.user_config_path != dirs2.user_config_path
    assert 'app-one' in str( dirs1.user_config_path )
    assert 'app-two' in str( dirs2.user_config_path )


def test_240_information_string_representation( ):
    ''' Information has useful string representation. '''
    app_info = module.Information(
        name = 'test-app',
        publisher = 'Test Company',
        version = '1.0'
    )
    str_repr = str( app_info )
    assert 'test-app' in str_repr
    assert 'Test Company' in str_repr
    assert '1.0' in str_repr


def test_250_platform_directories_standard_paths( ):
    ''' Platform directories provide standard directory types. '''
    app_info = module.Information( name = 'test-standard' )
    dirs = app_info.produce_platform_directories( )
    # Standard directories should be available
    assert hasattr( dirs, 'user_config_path' )
    assert hasattr( dirs, 'user_data_path' )
    assert hasattr( dirs, 'user_cache_path' )
    assert hasattr( dirs, 'user_log_path' )
    # All should be Path objects
    from pathlib import Path
    assert isinstance( dirs.user_config_path, Path )
    assert isinstance( dirs.user_data_path, Path )
    assert isinstance( dirs.user_cache_path, Path )
    assert isinstance( dirs.user_log_path, Path )