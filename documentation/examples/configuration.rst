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
Configuration Management
*******************************************************************************


Introduction
===============================================================================

The ``appcore`` package provides robust TOML-based configuration management
with support for hierarchical includes, template variables, and runtime edits.
Configuration files are automatically discovered and merged according to
precedence rules.


Basic TOML Configuration
===============================================================================

Configuration files use TOML format and are automatically loaded during
application initialization:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            # Access loaded configuration
            config = globals_dto.configuration
            print( f"Configuration keys: {list( config.keys( ) )}" )
            # Configuration is an accretive dictionary
            print( f"Type: {type( config )}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )

The configuration system looks for a ``general.toml`` file in your user
configuration directory. If it doesn't exist, a template is copied from
the package data.


Configuration File Locations
===============================================================================

Configuration files are searched in platform-specific locations:

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            # Show where configuration files are expected
            config_dir = globals_dto.directories.user_config_path
            print( f"Configuration directory: {config_dir}" )
            print( f"Default config file: {config_dir / 'general.toml'}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )

**Platform-specific locations:**

- **Linux**: ``~/.config/appname/general.toml``
- **macOS**: ``~/Library/Application Support/appname/general.toml``  
- **Windows**: ``%APPDATA%\\appname\\general.toml``


Stream-Based Configuration
===============================================================================

For testing or dynamic configuration, you can provide configuration content
directly as a stream:

.. doctest:: Configuration.Streams

    >>> import io
    >>> import appcore
    >>> 
    >>> # Create configuration content
    >>> config_content = '''
    ... [application]
    ... debug = true
    ... timeout = 30
    ... 
    ... [logging]
    ... level = "debug"
    ... '''
    >>> 
    >>> # Use StringIO for stream-based configuration
    >>> config_stream = io.StringIO( config_content )

.. code-block:: python

    import asyncio
    import contextlib
    import io
    import appcore

    async def main( ):
        # Create configuration content
        config_content = '''
        [application]
        debug = true
        timeout = 30

        [logging]
        level = "debug"
        '''
        config_stream = io.StringIO( config_content )
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare(
                exits,
                configfile = config_stream
            )
            config = globals_dto.configuration
            print( f"Debug mode: {config[ 'application' ][ 'debug' ]}" )
            print( f"Timeout: {config[ 'application' ][ 'timeout' ]}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )


Hierarchical Configuration with Includes
===============================================================================

Configuration files can include other files using the ``includes`` directive:

.. code-block:: toml

    # main configuration file
    [application]
    name = "myapp"
    
    [includes]
    # Include files from user configuration directory
    specs = [
        "{user_configuration}/local.toml",
        "{user_configuration}/overrides/"
    ]

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare( exits )
            config = globals_dto.configuration
            # Configuration from includes is merged
            print( f"Final configuration: {dict( config )}" )
            # Later includes override earlier ones
            # Files in directories are loaded alphabetically

    if __name__ == '__main__':
        asyncio.run( main( ) )

**Include variables available:**

- ``{user_configuration}`` - User configuration directory
- ``{user_home}`` - User home directory  
- ``{application_name}`` - Application name


Configuration Templates and Variables
===============================================================================

Configuration paths support template variables for dynamic resolution:

.. code-block:: toml

    [locations]
    data = "{user_home}/Documents/{application_name}"
    cache = "{user_cache}/custom-cache"
    
    [includes]
    specs = [
        "{user_configuration}/{application_name}-local.toml"
    ]

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        # Custom application name affects template resolution
        app_info = appcore.ApplicationInformation( name = 'my-custom-app' )
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare(
                exits,
                application = app_info
            )
            # Template variables are resolved automatically
            data_location = globals_dto.provide_data_location( )
            print( f"Data location: {data_location}" )
            # Will use custom paths if configured

    if __name__ == '__main__':
        asyncio.run( main( ) )


Runtime Configuration Edits
===============================================================================

You can modify configuration at runtime using edit functions:

.. doctest:: Configuration.Edits

    >>> import appcore
    >>>
    >>> def enable_debug_mode( config ):
    ...     ''' Enable debug mode in configuration. '''
    ...     if 'application' not in config:
    ...         config[ 'application' ] = { }
    ...     config[ 'application' ][ 'debug' ] = True
    ...
    >>> def set_log_level( config ):
    ...     ''' Set logging level to debug. '''
    ...     if 'logging' not in config:
    ...         config[ 'logging' ] = { }
    ...     config[ 'logging' ][ 'level' ] = 'debug'

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    def enable_debug_mode( config ):
        ''' Enable debug mode in configuration. '''
        if 'application' not in config:
            config[ 'application' ] = { }
        config[ 'application' ][ 'debug' ] = True

    def set_log_level( config ):
        ''' Set logging level to debug. '''
        if 'logging' not in config:
            config[ 'logging' ] = { }
        config[ 'logging' ][ 'level' ] = 'debug'

    async def main( ):
        # Apply configuration edits during initialization
        edits = ( enable_debug_mode, set_log_level )
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare(
                exits,
                configedits = edits
            )
            config = globals_dto.configuration
            print( f"Debug enabled: {config.get( 'application', { } ).get( 'debug' )}" )
            print( f"Log level: {config.get( 'logging', { } ).get( 'level' )}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )


Error Handling
===============================================================================

Configuration loading can encounter various error conditions:

.. code-block:: python

    import asyncio
    import contextlib
    import io
    import appcore

    async def main( ):
        # Invalid TOML content
        invalid_toml = '''
        [application
        debug = true  # missing closing bracket
        '''
        config_stream = io.StringIO( invalid_toml )
        
        try:
            async with contextlib.AsyncExitStack( ) as exits:
                globals_dto = await appcore.prepare(
                    exits,
                    configfile = config_stream
                )
        except Exception as e:
            print( f"Configuration error: {e}" )
            # Handle TOML parsing errors gracefully
            print( 'Using default configuration instead' )

    if __name__ == '__main__':
        asyncio.run( main( ) )


Custom Configuration Acquirers
===============================================================================

You can customize configuration loading by providing custom acquirers:

.. doctest:: Configuration.Acquirers

    >>> import appcore
    >>> 
    >>> # Custom acquirer with different template filename
    >>> acquirer = appcore.TomlConfigurationAcquirer( main_filename = 'myapp.toml' )
    >>> type( acquirer )
    <class 'appcore.configuration.TomlAcquirer'>
    >>> acquirer.main_filename
    'myapp.toml'
    >>> acquirer.includes_name
    'includes'

.. code-block:: python

    import asyncio
    import contextlib
    import appcore

    async def main( ):
        # Use custom template filename
        acquirer = appcore.TomlConfigurationAcquirer( main_filename = 'myapp.toml' )
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare(
                exits,
                acquirer = acquirer
            )
            # Will look for myapp.toml instead of general.toml
            config = globals_dto.configuration
            print( f"Configuration loaded from custom template: {dict( config )}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )

For testing, you can create custom acquirers that return specific configuration data:

.. doctest:: Configuration.TestAcquirers

    >>> import appcore
    >>> from dataclasses import dataclass
    >>> 
    >>> @dataclass
    ... class TestConfigurationAcquirer:
    ...     ''' Custom acquirer for testing. '''
    ...     config_data: dict
    ...     
    ...     async def __call__( self, *args, **kwargs ):
    ...         return appcore.accretive.Dictionary( self.config_data )
    >>> 
    >>> # Create test acquirer with specific data
    >>> test_data = { 'application': { 'name': 'test-app', 'debug': True } }
    >>> test_acquirer = TestConfigurationAcquirer( config_data = test_data )
    >>> test_acquirer.config_data[ 'application' ][ 'debug' ]
    True


Advanced Configuration Patterns
===============================================================================

Complex applications can use sophisticated configuration patterns:

.. code-block:: python

    import asyncio
    import contextlib
    import os
    import appcore

    def apply_environment_overrides( config ):
        ''' Apply environment variable overrides. '''
        # Override debug mode from environment
        if 'DEBUG' in os.environ:
            if 'application' not in config:
                config[ 'application' ] = { }
            config[ 'application' ][ 'debug' ] = (
                os.environ[ 'DEBUG' ].lower( ) in ( 'true', '1', 'yes' ) )
        # Override log level from environment  
        if 'LOG_LEVEL' in os.environ:
            if 'logging' not in config:
                config[ 'logging' ] = { }
            config[ 'logging' ][ 'level' ] = os.environ[ 'LOG_LEVEL' ]

    async def main( ):
        # Combine multiple configuration sources
        edits = ( apply_environment_overrides, )
        async with contextlib.AsyncExitStack( ) as exits:
            globals_dto = await appcore.prepare(
                exits,
                configedits = edits,
                environment = True  # Also load .env files
            )
            config = globals_dto.configuration
            print( f"Final config: {dict( config )}" )

    if __name__ == '__main__':
        asyncio.run( main( ) )


Resource Management Patterns
===============================================================================

Advanced patterns for managing resources with AsyncExitStack:

.. doctest:: Configuration.Resources

    >>> import tempfile
    >>> import io
    >>> import platformdirs
    >>> import contextlib
    >>> import appcore
    >>> 
    >>> async def example_with_temporary_resources( ):
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

This pattern is particularly useful for testing scenarios where you need isolated, temporary resources that are guaranteed to be cleaned up.


Next Steps
===============================================================================

This covers configuration management in appcore. For more topics, see:

- **Environment Handling** - Environment variables and development detection
- **Basic Usage** - Application setup and platform directories