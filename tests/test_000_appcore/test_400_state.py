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


''' Global state DTO and directory management tests. '''


import dataclasses

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from .__ import PACKAGE_NAME, cache_import_module

MODULE_QNAME = f"{PACKAGE_NAME}.state"
module = cache_import_module( MODULE_QNAME )

application_module = cache_import_module( f"{PACKAGE_NAME}.application" )
distribution_module = cache_import_module( f"{PACKAGE_NAME}.distribution" )


def test_100_directory_species_values( ):
    ''' DirectorySpecies has expected string values. '''
    assert module.DirectorySpecies.Cache.value == 'cache'
    assert module.DirectorySpecies.Data.value == 'data'
    assert module.DirectorySpecies.State.value == 'state'


def test_110_directory_species_enum_members( ):
    ''' DirectorySpecies has all expected enum members. '''
    assert hasattr( module.DirectorySpecies, 'Cache' )
    assert hasattr( module.DirectorySpecies, 'Data' )
    assert hasattr( module.DirectorySpecies, 'State' )


def test_200_globals_creation( ):
    ''' Globals creates with all required fields. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'app': { 'name': 'test' } }
    directories = MagicMock( )
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    assert globals_obj.application == application
    assert globals_obj.configuration == configuration
    assert globals_obj.directories == directories
    assert globals_obj.distribution == distribution
    assert globals_obj.exits == exits


def test_210_globals_as_dictionary( ):
    ''' Globals.as_dictionary returns shallow copy of state. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'app': { 'name': 'test' } }
    directories = MagicMock( )
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.as_dictionary( )
    assert 'application' in result
    assert 'configuration' in result
    assert 'directories' in result
    assert 'distribution' in result
    assert 'exits' in result
    assert result[ 'application' ] == application
    assert result[ 'configuration' ] == configuration
    assert result[ 'directories' ] == directories
    assert result[ 'distribution' ] == distribution
    assert result[ 'exits' ] == exits


def test_220_globals_as_dictionary_immutable( ):
    ''' Globals.as_dictionary returns copy, not reference. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'app': { 'name': 'test' } }
    directories = MagicMock( )
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.as_dictionary( )
    # Modifying the returned dictionary should not affect the original
    result[ 'new_field' ] = 'new_value'
    # Original should not have the new field
    assert not hasattr( globals_obj, 'new_field' )


def test_300_globals_provide_cache_location_basic( ):
    ''' Globals.provide_cache_location returns cache directory. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { }
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_cache_location( )
    assert result == Path( '/user/cache/test-app' )


def test_310_globals_provide_cache_location_with_appendages( ):
    ''' Globals.provide_cache_location handles appendages. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { }
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_cache_location( 'temp', 'files' )
    assert result == Path( '/user/cache/test-app/temp/files' )


def test_320_globals_provide_data_location_basic( ):
    ''' Globals.provide_data_location returns data directory. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { }
    directories = MagicMock( )
    directories.user_data_path = Path( '/user/data/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_data_location( )
    assert result == Path( '/user/data/test-app' )


def test_330_globals_provide_state_location_basic( ):
    ''' Globals.provide_state_location returns state directory. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { }
    directories = MagicMock( )
    directories.user_state_path = Path( '/user/state/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_state_location( )
    assert result == Path( '/user/state/test-app' )


def test_340_globals_provide_location_with_custom_config( ):
    ''' Globals.provide_location uses custom configuration specs. '''
    application = application_module.Information( name = 'test-app' )
    configuration = {
        'locations': {
            'cache': '{user_home}/custom-cache/{application_name}',
            'data': '{user_data}/custom-data'
        }
    }
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    directories.user_data_path = Path( '/user/data/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    # Test custom cache location
    cache_result = globals_obj.provide_location(
        module.DirectorySpecies.Cache )
    expected_cache = Path.home( ) / 'custom-cache' / 'test-app'
    assert cache_result == expected_cache
    # Test custom data location with user_data substitution
    data_result = globals_obj.provide_location(
        module.DirectorySpecies.Data )
    expected_data = Path( '/user/data/test-app/custom-data' )
    assert data_result == expected_data


def test_350_globals_provide_location_with_appendages_and_config( ):
    ''' Globals.provide_location combines custom config with appendages. '''
    application = application_module.Information( name = 'test-app' )
    configuration = {
        'locations': {
            'cache': '{user_home}/custom/{application_name}'
        }
    }
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_location(
        module.DirectorySpecies.Cache, 'temp', 'files' )
    expected = Path.home( ) / 'custom' / 'test-app' / 'temp' / 'files'
    assert result == expected


def test_360_globals_provide_location_fallback_to_default( ):
    ''' Globals.provide_location falls back to default when no config. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'other': 'value' }  # No locations config
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    result = globals_obj.provide_location( module.DirectorySpecies.Cache )
    assert result == Path( '/user/cache/test-app' )


def test_370_globals_provide_location_partial_config( ):
    ''' Globals.provide_location handles partial location configuration. '''
    application = application_module.Information( name = 'test-app' )
    configuration = {
        'locations': {
            'cache': '{user_home}/custom-cache'
            # data not configured
        }
    }
    directories = MagicMock( )
    directories.user_cache_path = Path( '/user/cache/test-app' )
    directories.user_data_path = Path( '/user/data/test-app' )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    # Cache should use custom config
    cache_result = globals_obj.provide_location(
        module.DirectorySpecies.Cache )
    assert cache_result == Path.home( ) / 'custom-cache'
    # Data should use default
    data_result = globals_obj.provide_location(
        module.DirectorySpecies.Data )
    assert data_result == Path( '/user/data/test-app' )


def test_400_globals_immutability( ):
    ''' Globals instances are immutable. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { }
    directories = MagicMock( )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    # Should not be able to modify fields after creation
    with pytest.raises( ( AttributeError, TypeError ) ):
        globals_obj.application = MagicMock( )  # type: ignore


def test_410_globals_equality( ):
    ''' Globals instances with same data are equal. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'test': 'value' }
    directories = MagicMock( )
    distribution = distribution_module.Information(
        name = 'test-dist',
        location = Path( '/test' ),
        editable = True
    )
    exits = MagicMock( )
    globals1 = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    globals2 = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    assert globals1 == globals2


def test_420_globals_inequality( ):
    ''' Globals instances with different data are not equal. '''
    application1 = application_module.Information( name = 'test-app-1' )
    application2 = application_module.Information( name = 'test-app-2' )
    configuration = { }
    directories = MagicMock( )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals1 = module.Globals(
        application = application1,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    globals2 = module.Globals(
        application = application2,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    assert globals1 != globals2


def test_430_globals_string_representation( ):
    ''' Globals has useful string representation. '''
    application = application_module.Information( name = 'test-app' )
    configuration = { 'test': 'value' }
    directories = MagicMock( )
    distribution = MagicMock( )
    exits = MagicMock( )
    globals_obj = module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    )
    str_repr = str( globals_obj )
    assert 'test-app' in str_repr


def test_440_globals_dataclass_fields( ):
    ''' Globals has proper dataclass field definitions. '''
    fields = dataclasses.fields( module.Globals )
    # Filter out frigid internal fields
    user_field_names = {
        field.name for field in fields
        if not field.name.startswith( '_frigid' )
    }
    expected_fields = {
        'application', 'configuration', 'directories',
        'distribution', 'exits'
    }
    assert user_field_names == expected_fields
