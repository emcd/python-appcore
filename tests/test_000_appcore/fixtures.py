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


''' Standard test fixtures for temp directories and dependency injection. '''


import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from . import PACKAGE_NAME, cache_import_module


application_module = cache_import_module( f"{PACKAGE_NAME}.application" )
distribution_module = cache_import_module( f"{PACKAGE_NAME}.distribution" )
state_module = cache_import_module( f"{PACKAGE_NAME}.state" )


def create_temp_directories_and_distribution( 
    editable = False, 
    config_locations = None,
    app_name = 'test-app',
    dist_name = 'test-dist'
):
    ''' Creates temporary directories with directories and distribution DTOs.
    Returns:
        tuple[directories, distribution, temp_dir]: Mock directories object,
        real distribution object, and Path to temp directory for cleanup.
    '''
    temp_dir = Path( tempfile.mkdtemp( ) )
    # Create directories mock with real paths
    directories = MagicMock( )
    directories.user_config_path = temp_dir / 'config'
    directories.user_config_path.mkdir( parents = True, exist_ok = True )
    # Create real distribution with temp location
    distribution = distribution_module.Information(
        name = dist_name,
        location = temp_dir / 'project' if editable else temp_dir,
        editable = editable
    )
    if editable:
        distribution.location.mkdir( parents = True, exist_ok = True )
    return directories, distribution, temp_dir


def create_globals_with_temp_dirs( 
    editable = False, 
    config_locations = None,
    app_name = 'test-env-app' 
):
    ''' Creates Globals DTO with temporary directories for environment tests.
    Returns:
        tuple[Globals, temp_dir]: Globals DTO and Path to temp directory.
    '''
    directories, distribution, temp_dir = (
        create_temp_directories_and_distribution(
            editable = editable, 
            app_name = app_name
        ) )
    application = application_module.Information( name = app_name )
    configuration = { }
    if config_locations:
        configuration[ 'locations' ] = config_locations
    exits = MagicMock( )
    return state_module.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits
    ), temp_dir


def create_config_template_files( 
    distribution, 
    main_filename = 'general.toml',
    content = None 
):
    ''' Creates configuration template files in distribution data location.
    Args:
        distribution: Distribution DTO with location
        main_filename: Name of main config file 
        content: TOML content string, defaults to basic app config
    '''
    if content is None:
        content = '''
[app]
name = "template-app"
version = "1.0.0"
        '''
    # Create data/configuration directory structure
    config_dir = distribution.provide_data_location( 'configuration' )
    config_dir.mkdir( parents = True, exist_ok = True )
    # Write template file
    template_file = config_dir / main_filename
    template_file.write_text( content )
    return template_file