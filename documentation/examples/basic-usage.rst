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
Basic Usage
*******************************************************************************


Introduction
===============================================================================

The ``appcore`` package provides a simple async initialization framework for 
applications that need configuration loading, platform directory management, 
and environment setup. The core function is ``prepare()``, which returns a 
``Globals`` object containing all the initialized application state.


Basic Application Setup
===============================================================================

The simplest way to initialize appcore for your application:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            # Initialize application core with sensible defaults
            globals_dto = await appcore.prepare( exits )
            # Access application information
            print( f"Application: {globals_dto.application.name}" )
            print( f"Publisher: {globals_dto.application.publisher}" )
            print( f"Version: {globals_dto.application.version}" )
            # Check if running in development mode
            if globals_dto.distribution.editable:
                print( 'Running in development mode' )
            else:
                print( 'Running in production mode' )

    if __name__ == '__main__':
        asyncio.run( main( ) )

This will automatically detect your application name from the package, set up 
platform directories, load configuration, and prepare logging.


Platform Directory Access
===============================================================================

The ``Globals`` object provides convenient access to platform-specific 
directories for your application:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore
    from pathlib import Path

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            # Get platform directories for data storage
            cache_dir = globals_dto.provide_cache_location( )
            data_dir = globals_dto.provide_data_location( )
            state_dir = globals_dto.provide_state_location( )
            print( f"Cache directory: {cache_dir}" )
            print( f"Data directory: {data_dir}" )  
            print( f"State directory: {state_dir}" )
            # Create subdirectories for organization
            logs_dir = globals_dto.provide_data_location( 'logs' )
            config_dir = globals_dto.provide_data_location( 'config' )
            print( f"Logs will go in: {logs_dir}" )
            print( f"Config files in: {config_dir}" )
            # Directories are automatically created as needed
            logs_dir.mkdir( parents = True, exist_ok = True )
            config_dir.mkdir( parents = True, exist_ok = True )

    if __name__ == '__main__':
        asyncio.run( main( ) )

The exact paths depend on your operating system:

- **Linux**: ``~/.cache/appname``, ``~/.local/share/appname``, ``~/.local/state/appname``
- **macOS**: ``~/Library/Caches/appname``, ``~/Library/Application Support/appname``, etc.
- **Windows**: ``%LOCALAPPDATA%\appname``, ``%APPDATA%\appname``, etc.


Working with Application Data
===============================================================================

You can store and retrieve application data using the provided directories:

.. code-block:: python

    import asyncio
    import contextlib
    import json
    import appcore

    async def save_user_preferences( globals_dto, preferences ):
        ''' Save user preferences to the data directory. '''
        prefs_file = globals_dto.provide_data_location( 'preferences.json' )
        prefs_file.parent.mkdir( parents = True, exist_ok = True )
        with open( prefs_file, 'w' ) as f:
            json.dump( preferences, f, indent = 2 )
        print( f"Preferences saved to: {prefs_file}" )

    async def load_user_preferences( globals_dto ):
        ''' Load user preferences from the data directory. '''
        prefs_file = globals_dto.provide_data_location( 'preferences.json' )
        if prefs_file.exists( ):
            with open( prefs_file, 'r' ) as f:
                preferences = json.load( f )
            print( f"Loaded preferences: {preferences}" )
            return preferences
        else:
            print( 'No preferences file found, using defaults' )
            return { 'theme': 'dark', 'auto_save': True }

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            # Save some example preferences
            prefs = { 'theme': 'light', 'auto_save': False, 'recent_files': [ ] }
            await save_user_preferences( globals_dto, prefs )
            # Load them back
            loaded_prefs = await load_user_preferences( globals_dto )

    if __name__ == '__main__':
        asyncio.run( main( ) )


Custom Application Information
===============================================================================

You can customize the application metadata used for directory generation:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        # Create custom application information
        app_info = appcore.ApplicationInformation(
            name = 'my-awesome-app',
            publisher = 'MyCompany', 
            version = '2.1.0'
        )
        async with contextlib.AsyncExitStack( ) as exits:
            # Use custom application info
            globals_dto = await appcore.prepare(
                exits, 
                application = app_info
            )
            print( f"App: {globals_dto.application.name}" )
            print( f"Publisher: {globals_dto.application.publisher}" )
            print( f"Data dir: {globals_dto.provide_data_location()}" )
            # The directories will include publisher and version info:
            # Linux: ~/.local/share/MyCompany/my-awesome-app/2.1.0/
            # macOS: ~/Library/Application Support/MyCompany/my-awesome-app/2.1.0/

    if __name__ == '__main__':
        asyncio.run( main( ) )


Error Handling
===============================================================================

The ``prepare()`` function can raise exceptions in certain scenarios. Use ``Omnierror`` to catch all package errors, or specific exceptions for fine-grained handling:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        try:
            async with contextlib.AsyncExitStack( ) as exits:
                globals_dto = await appcore.prepare( exits )
                print( 'Initialization successful!' )
        except appcore.exceptions.Omnierror as e:
            print( f"Appcore initialization error: {e}" )
            # Omnierror catches all errors from the package API
            # You can also catch specific exceptions for fine-grained handling
        except Exception as e:
            print( f"Unexpected system error: {e}" )
            raise

    if __name__ == '__main__':
        asyncio.run( main( ) )

**For fine-grained error handling, catch specific exceptions:**

.. code-block:: python

    try:
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
    except appcore.exceptions.FileLocateFailure as e:
        print( f"Could not locate required files: {e}" )
        # This can happen in development if pyproject.toml is not found
    except appcore.exceptions.OperationInvalidity as e:
        print( f"Invalid operation during setup: {e}" )
        # This can happen with malformed configuration files


Next Steps
===============================================================================

This covers the basic usage of appcore. For more advanced topics, see:

- **Configuration Management** - Loading TOML configuration files with includes
- **Environment Handling** - Development vs production detection and environment variables  
- **Advanced Usage** - Dependency injection, testing patterns, and custom logging