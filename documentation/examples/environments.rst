.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
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
Environment Handling
*******************************************************************************


Introduction
===============================================================================

The ``appcore`` package provides sophisticated environment detection and
management. It automatically distinguishes between development and production
environments, loads environment variables from files, and supports custom
environment injection for testing.

.. doctest:: Environment.Setup

    >>> import appcore
    >>> import platformdirs
    >>> import io


Development vs Production Detection
===============================================================================

Appcore automatically detects whether your application is running in
development or production mode by examining how the package is installed:

**Development mode detection:**

1. **Check package distribution**: Uses ``importlib_metadata.packages_distributions()`` to see if your package is installed as a proper distribution
2. **If not found**: Assumes development mode (``editable = True``)
3. **Locate project root**: Searches upward from the current file to find ``pyproject.toml``
4. **Respect boundaries**: Honors ``GIT_CEILING_DIRECTORIES`` environment variable to limit search scope

**Production mode detection:**

1. **Package found in distribution**: Package is properly installed (``pip install``, not ``pip install -e``)
2. **Set production mode**: ``editable = False``
3. **Use installed location**: Points to the installed package location

**Detection process happens automatically during** ``appcore.prepare()``

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            
            # Check the automatically detected mode
            if globals_dto.distribution.editable:
                print( 'Running in DEVELOPMENT mode' )
                print( f"Project root: {globals_dto.distribution.location}" )
                print( f"Package name: {globals_dto.distribution.name}" )
                # Development-specific behavior
                debug_mode = True
                use_local_configs = True
            else:
                print( 'Running in PRODUCTION mode' )
                print( f"Installed at: {globals_dto.distribution.location}" )
                print( f"Package name: {globals_dto.distribution.name}" )
                # Production-specific behavior  
                debug_mode = False
                use_local_configs = False

    if __name__ == '__main__':
        asyncio.run( main( ) )

**Example output in development:**
- ``Running in DEVELOPMENT mode``
- ``Project root: /home/user/projects/myapp``
- ``Package name: myapp``

**Example output in production:**
- ``Running in PRODUCTION mode``  
- ``Installed at: /usr/local/lib/python3.10/site-packages/myapp``
- ``Package name: myapp``


Environment Variable Injection
===============================================================================

For testing or custom deployment scenarios, you can inject environment
variables directly:

.. doctest:: Environment.Injection

    >>> import asyncio
    >>> import contextlib
    >>> 
    >>> async def test_with_custom_env( ):
    ...     # Define custom environment variables
    ...     custom_env = {
    ...         'DEBUG': 'true',
    ...         'LOG_LEVEL': 'debug',
    ...         'API_KEY': 'test-key-12345'
    ...     }
    ...     # Create custom directories to avoid filesystem operations
    ...     custom_dirs = platformdirs.PlatformDirs( 'test-app', ensure_exists = False )
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             directories = custom_dirs,
    ...             environment = custom_env  # Inject environment variables
    ...         )
    ...         print( f"Environment injected successfully" )
    ...         return globals_dto
    >>> 
    >>> # This would normally be run with asyncio.run()
    >>> # globals_dto = asyncio.run( test_with_custom_env( ) )


Custom Platform Directories
===============================================================================

You can override the default platform directory logic for testing or
specialized deployments:

.. doctest:: Environment.CustomDirectories

    >>> import platformdirs
    >>> # Create custom directory configuration
    >>> custom_dirs = platformdirs.PlatformDirs(
    ...     appname = 'test-app',
    ...     appauthor = 'TestCorp',
    ...     version = '1.0.0',
    ...     ensure_exists = False  # Don't create directories during testing
    ... )
    >>> 
    >>> async def test_with_custom_directories( ):
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             directories = custom_dirs
    ...         )
    ...         # Use injected directories instead of auto-generated ones
    ...         cache_dir = globals_dto.provide_cache_location( )
    ...         print( f"Custom cache directory: {cache_dir}" )
    ...         return globals_dto


Distribution Information Override
===============================================================================

For advanced testing scenarios, you can provide custom distribution
information:

.. doctest:: Environment.DistributionOverride

    >>> import appcore
    >>> from pathlib import Path
    >>> # Create mock distribution for testing
    >>> test_distribution = appcore.DistributionInformation(
    ...     name = 'my-test-app',
    ...     location = Path( '/tmp/test-project' ),
    ...     editable = True  # Simulate development mode
    ... )
    >>> 
    >>> async def test_development_behavior( ):
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             distribution = test_distribution
    ...         )
    ...         # Test development-specific code paths
    ...         assert globals_dto.distribution.editable
    ...         assert globals_dto.distribution.name == 'my-test-app'
    ...         print( 'Development mode simulation successful' )
    ...         return globals_dto


Configuration Stream with Environment
===============================================================================

Combine stream-based configuration with environment variable injection:

.. doctest:: Environment.ConfigStream

    >>> config_content = '''
    ... [application]
    ... name = "stream-app"
    ... debug = false
    ... 
    ... [logging]
    ... level = "info"
    ... '''
    >>> 
    >>> env_overrides = {
    ...     'DEBUG': 'true',
    ...     'LOG_LEVEL': 'debug'
    ... }
    >>> 
    >>> def apply_env_overrides( config ):
    ...     ''' Apply environment variable overrides to configuration. '''
    ...     import os
    ...     # Use DEBUG environment variable if present
    ...     if 'DEBUG' in os.environ:
    ...         if 'application' not in config:
    ...             config[ 'application' ] = { }
    ...         config[ 'application' ][ 'debug' ] = (
    ...             os.environ[ 'DEBUG' ].lower( ) in ( 'true', '1', 'yes' ) )
    >>> 
    >>> async def test_config_with_env( ):
    ...     config_stream = io.StringIO( config_content )
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             configfile = config_stream,
    ...             environment = env_overrides,
    ...             configedits = ( apply_env_overrides, )
    ...         )
    ...         config = globals_dto.configuration
    ...         debug_enabled = config.get( 'application', { } ).get( 'debug', False )
    ...         print( f"Debug mode: {debug_enabled}" )
    ...         return globals_dto


Environment File Loading
===============================================================================

Appcore can load environment variables from ``.env`` files with precedence
rules:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            # Enable environment file loading
            globals_dto = await appcore.prepare(
                exits,
                environment = True  # Load from .env files
            )
            # Environment variables are now available in os.environ
            import os
            debug_mode = os.environ.get( 'DEBUG', 'false' ).lower( ) == 'true'
            api_key = os.environ.get( 'API_KEY', 'default-key' )
            print( f"Debug mode: {debug_mode}" )
            print( f"API key configured: {'Yes' if api_key != 'default-key' else 'No'}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )

**Environment file precedence (later files override earlier ones):**

1. **Configuration directory**: Files specified in configuration includes
2. **Local directory**: ``.env`` file in current working directory
3. **Development mode**: Project root ``.env`` file (takes precedence)


Complete Testing Setup
===============================================================================

Here's a comprehensive example showing how to set up a controlled environment
for testing:

.. doctest:: Environment.CompleteTesting

    >>> import appcore
    >>> import platformdirs
    >>> import io
    >>> import contextlib
    >>> from pathlib import Path
    >>> async def create_test_environment( ):
    ...     ''' Create a completely controlled test environment. '''
    ...     # Custom application info
    ...     app_info = appcore.ApplicationInformation(
    ...         name = 'test-suite',
    ...         publisher = 'TestCorp',
    ...         version = '0.1.0'
    ...     )
    ...     # Custom directories (no filesystem access)
    ...     test_dirs = platformdirs.PlatformDirs(
    ...         appname = 'test-suite',
    ...         ensure_exists = False
    ...     )
    ...     # Mock distribution info
    ...     test_dist = appcore.DistributionInformation(
    ...         name = 'test-suite',
    ...         location = Path( '/tmp/test' ),
    ...         editable = True
    ...     )
    ...     # Custom environment variables
    ...     test_env = {
    ...         'DEBUG': 'true',
    ...         'TEST_MODE': 'true',
    ...         'LOG_LEVEL': 'debug'
    ...     }
    ...     # Custom configuration
    ...     test_config = '''
    ...     [application]
    ...     name = "test-suite"
    ...     timeout = 10
    ...     
    ...     [testing]
    ...     enabled = true
    ...     '''
    ...     config_stream = io.StringIO( test_config )
    ...     # Initialize with all custom components
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             application = app_info,
    ...             directories = test_dirs,
    ...             distribution = test_dist,
    ...             environment = test_env,
    ...             configfile = config_stream
    ...         )
    ...         # Verify everything is set up correctly
    ...         assert globals_dto.application.name == 'test-suite'
    ...         assert globals_dto.distribution.editable == True
    ...         config = globals_dto.configuration
    ...         assert config[ 'testing' ][ 'enabled' ] == True
    ...         print( 'Complete test environment setup successful' )
    ...         return globals_dto
    
    Complete test environment setup successful


Error Handling for Environment Issues
===============================================================================

Environment setup can encounter various error conditions:

.. doctest:: Environment.ErrorHandling

    >>> import appcore
    >>> import contextlib
    >>> from pathlib import Path
    >>> async def test_error_scenarios( ):
    ...     # Test with invalid distribution location
    ...     bad_dist = appcore.DistributionInformation(
    ...         name = 'bad-app',
    ...         location = Path( '/nonexistent/path' ),
    ...         editable = True
    ...     )
    ...     try:
    ...         async with contextlib.AsyncExitStack( ) as exits:
    ...             globals_dto = await appcore.prepare(
    ...                 exits,
    ...                 distribution = bad_dist
    ...             )
    ...     except Exception as e:
    ...         print( f"Handled distribution error: {type( e ).__name__}" )
    ...     # Test with invalid environment values
    ...     bad_env = { 'INVALID_KEY': None }  # None values not allowed
    ...     try:
    ...         async with contextlib.AsyncExitStack( ) as exits:
    ...             globals_dto = await appcore.prepare(
    ...                 exits,
    ...                 environment = bad_env
    ...             )
    ...     except Exception as e:
    ...         print( f"Handled environment error: {type( e ).__name__}" )
    >>> 
    >>> # This would normally be run with asyncio.run()
    >>> # asyncio.run( test_error_scenarios( ) )


Next Steps
===============================================================================

This covers environment handling in appcore. For more topics, see:

- **Advanced Usage** - Testing patterns and dependency injection strategies
- **Configuration Management** - TOML loading and hierarchical includes  
- **Basic Usage** - Application setup and platform directories