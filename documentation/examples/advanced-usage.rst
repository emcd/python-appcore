.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Advanced Usage
*******************************************************************************


Introduction
===============================================================================

This section covers advanced patterns for using ``appcore`` beyond basic
application setup.

.. doctest:: Advanced.Setup

    >>> import appcore
    >>> import platformdirs
    >>> import io
    >>> import asyncio
    >>> import contextlib


Custom Application Information Patterns
===============================================================================

Create application information objects for different deployment scenarios:

.. doctest:: Advanced.ApplicationInfo

    >>> import appcore
    >>> def create_application_profiles( ):
    ...     ''' Create different application profiles. '''
    ...     return {
    ...         'development': appcore.ApplicationInformation(
    ...             name = 'myapp-dev',
    ...             publisher = 'DevCorp',
    ...             version = '0.1.0-dev'
    ...         ),
    ...         'staging': appcore.ApplicationInformation(
    ...             name = 'myapp-staging',
    ...             publisher = 'DevCorp',
    ...             version = '1.0.0-rc1'
    ...         ),
    ...         'production': appcore.ApplicationInformation(
    ...             name = 'myapp',
    ...             publisher = 'ProductionCorp',
    ...             version = '1.0.0'
    ...         )
    ...     }
    >>>
    >>> profiles = create_application_profiles( )
    >>> dev_profile = profiles[ 'development' ]
    >>> print( f"Dev app: {dev_profile.name} v{dev_profile.version}" )
    Dev app: myapp-dev v0.1.0-dev
    >>>
    >>> # Each profile will have different platform directories
    >>> dev_dirs = dev_profile.produce_platform_directories( )
    >>> prod_dirs = profiles[ 'production' ].produce_platform_directories( )
    >>> print( f"Different apps use different directories" )
    Different apps use different directories


Resource Management Patterns
===============================================================================

Advanced patterns for managing resources with AsyncExitStack:

.. doctest:: Advanced.Resources

    >>> import tempfile
    >>>
    >>> async def test_with_temporary_resources( ):
    ...     ''' Example using temporary resources that are cleaned up automatically. '''
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         # Create temporary directory
    ...         temp_dir = exits.enter_context( tempfile.TemporaryDirectory( ) )
    ...         print( f"Created temp directory: {temp_dir}" )
    ...         # Use custom directories pointing to temp location
    ...         custom_dirs = platformdirs.PlatformDirs( 'temp-app', ensure_exists = False )
    ...         # Initialize appcore with temporary resources
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             directories = custom_dirs,
    ...             configfile = io.StringIO( '''
    ...             [application]
    ...             name = "temp-app"
    ...             [data]
    ...             temporary = true
    ...             ''' )
    ...         )
    ...         # Use the globals object
    ...         config = globals_dto.configuration
    ...         is_temporary = config[ 'data' ][ 'temporary' ]
    ...         print( f"Using temporary setup: {is_temporary}" )
    ...         return globals_dto
    ...     # temp_dir is automatically cleaned up when exiting the context


Next Steps
===============================================================================

This covers advanced usage patterns for appcore. For foundational topics, see:

- **Basic Usage** - Application setup and platform directories
- **Configuration Management** - TOML loading and hierarchical includes
- **Environment Handling** - Development detection and environment variables
