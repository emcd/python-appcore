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

This section covers advanced patterns for using ``appcore``, including
sophisticated testing strategies, dependency injection patterns, and 
integration with testing frameworks.

.. doctest:: Advanced.Setup

    >>> import appcore
    >>> import platformdirs
    >>> import io
    >>> import asyncio
    >>> import contextlib


Testing Strategies
===============================================================================

Appcore's dependency injection capabilities make it excellent for testing.
Here are common patterns:

.. doctest:: Advanced.Testing

    >>> import appcore
    >>> import platformdirs
    >>> from pathlib import Path
    >>> class MockGlobals:
    ...     ''' Mock globals object for unit testing. '''
    ...     def __init__( self, app_name = 'test-app' ):
    ...         self.application = appcore.ApplicationInformation( name = app_name )
    ...         self.configuration = { 'test': True }
    ...         self.directories = platformdirs.PlatformDirs( app_name, ensure_exists = False )
    ...         self.distribution = appcore.DistributionInformation(
    ...             name = app_name,
    ...             location = Path( '/tmp/test' ),
    ...             editable = True
    ...         )
    ...     def provide_data_location( self, *appendages ):
    ...         base = Path( f"/tmp/test-data/{self.application.name}" )
    ...         if appendages:
    ...             return base.joinpath( *appendages )
    ...         return base
    >>> 
    >>> # Use mock in tests
    >>> mock_globals = MockGlobals( 'unit-test' )
    >>> assert mock_globals.application.name == 'unit-test'
    >>> test_path = mock_globals.provide_data_location( 'test.json' )
    >>> print( f"Test data path: {test_path}" )
    Test data path: /tmp/test-data/unit-test/test.json


Parameterized Testing Setup
===============================================================================

Create reusable test fixtures with different configurations:

.. doctest:: Advanced.Fixtures

    >>> import appcore
    >>> import platformdirs
    >>> import io
    >>> import contextlib
    >>> from pathlib import Path
    >>> async def create_test_globals( 
    ...     app_name = 'test-app',
    ...     config_content = None,
    ...     env_vars = None,
    ...     development_mode = True
    ... ):
    ...     ''' Factory function for test globals with custom parameters. '''
    ...     # Default configuration
    ...     if config_content is None:
    ...         config_content = '''
    ...         [application]
    ...         name = "''' + app_name + '''"
    ...         debug = true
    ...         
    ...         [testing]
    ...         enabled = true
    ...         '''
    ...     # Setup components
    ...     app_info = appcore.ApplicationInformation( name = app_name )
    ...     test_dirs = platformdirs.PlatformDirs( app_name, ensure_exists = False )
    ...     test_dist = appcore.DistributionInformation(
    ...         name = app_name,
    ...         location = Path( '/tmp/test' ),
    ...         editable = development_mode
    ...     )
    ...     config_stream = io.StringIO( config_content )
    ...     env_vars = env_vars or { }
    ...     # Create globals
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             application = app_info,
    ...             directories = test_dirs,
    ...             distribution = test_dist,
    ...             configfile = config_stream,
    ...             environment = env_vars
    ...         )
    ...         return globals_dto
    >>> 
    >>> # Example usage in tests
    >>> async def test_development_setup( ):
    ...     globals_dto = await create_test_globals(
    ...         app_name = 'dev-test',
    ...         development_mode = True,
    ...         env_vars = { 'DEBUG': 'true' }
    ...     )
    ...     assert globals_dto.distribution.editable == True
    ...     assert globals_dto.application.name == 'dev-test'
    ...     return globals_dto


Configuration Testing Patterns
===============================================================================

Test different configuration scenarios systematically:

.. doctest:: Advanced.ConfigTesting

    >>> def create_config_variants( ):
    ...     ''' Generate different configuration scenarios for testing. '''
    ...     return {
    ...         'minimal': '''
    ...         [application]
    ...         name = "minimal-app"
    ...         ''',
    ...         'debug_enabled': '''
    ...         [application]
    ...         name = "debug-app"
    ...         debug = true
    ...         timeout = 30
    ...         
    ...         [logging]
    ...         level = "debug"
    ...         ''',
    ...         'production': '''
    ...         [application]
    ...         name = "prod-app"
    ...         debug = false
    ...         timeout = 300
    ...         
    ...         [logging]
    ...         level = "info"
    ...         
    ...         [security]
    ...         strict_mode = true
    ...         '''
    ...     }
    >>> 
    >>> async def test_config_variant( variant_name, config_content ):
    ...     ''' Test a specific configuration variant. '''
    ...     config_stream = io.StringIO( config_content )
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             configfile = config_stream,
    ...             directories = platformdirs.PlatformDirs( 'test', ensure_exists = False )
    ...         )
    ...         config = globals_dto.configuration
    ...         app_name = config[ 'application' ][ 'name' ]
    ...         print( f"{variant_name}: {app_name}" )
    ...         return config
    >>> 
    >>> # Test all variants
    >>> async def test_all_config_variants( ):
    ...     configs = create_config_variants( )
    ...     results = { }
    ...     for name, content in configs.items( ):
    ...         result = await test_config_variant( name, content )
    ...         results[ name ] = result
    ...     return results


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


Error Simulation and Recovery
===============================================================================

Test error conditions and recovery strategies:

.. doctest:: Advanced.ErrorTesting

    >>> class ConfigurationError( Exception ):
    ...     ''' Custom configuration error for testing. '''
    ...     pass
    >>> 
    >>> def failing_config_edit( config ):
    ...     ''' Configuration edit that fails for testing. '''
    ...     raise ConfigurationError( 'Simulated configuration failure' )
    >>> 
    >>> def safe_config_edit( config ):
    ...     ''' Configuration edit with error handling. '''
    ...     try:
    ...         # Attempt risky operation
    ...         if 'application' not in config:
    ...             config[ 'application' ] = { }
    ...         config[ 'application' ][ 'safe_mode' ] = True
    ...     except Exception as e:
    ...         print( f"Config edit failed: {e}" )
    ...         # Apply fallback configuration
    ...         config[ 'fallback' ] = True
    >>> 
    >>> async def test_error_recovery( ):
    ...     ''' Test configuration error recovery. '''
    ...     config_content = '''
    ...     [application]
    ...     name = "error-test"
    ...     '''
    ...     try:
    ...         config_stream = io.StringIO( config_content )
    ...         async with contextlib.AsyncExitStack( ) as exits:
    ...             globals_dto = await appcore.prepare(
    ...                 exits,
    ...                 configfile = config_stream,
    ...                 configedits = ( safe_config_edit, ),
    ...                 directories = platformdirs.PlatformDirs( 'test', ensure_exists = False )
    ...             )
    ...             config = globals_dto.configuration
    ...             has_safe_mode = config.get( 'application', { } ).get( 'safe_mode', False )
    ...             print( f"Safe mode enabled: {has_safe_mode}" )
    ...             return config
    ...     except Exception as e:
    ...         print( f"Initialization failed: {e}" )
    ...         return None


Performance Testing Setup
===============================================================================

Measure initialization performance with different configurations:

.. doctest:: Advanced.Performance

    >>> import time
    >>> 
    >>> async def benchmark_initialization( config_size = 'small' ):
    ...     ''' Benchmark appcore initialization performance. '''
    ...     # Generate configuration of different sizes
    ...     if config_size == 'small':
    ...         config_content = '''
    ...         [application]
    ...         name = "benchmark"
    ...         '''
    ...     elif config_size == 'large':
    ...         # Generate larger configuration
    ...         sections = [ ]
    ...         for i in range( 10 ):
    ...             sections.append( f'''
    ...             [section_{i}]
    ...             value_{i} = {i}
    ...             setting_{i} = "config_{i}"
    ...             ''' )
    ...         config_content = '''
    ...         [application]
    ...         name = "benchmark"
    ...         ''' + '\n'.join( sections )
    ...     start_time = time.time( )
    ...     config_stream = io.StringIO( config_content )
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             configfile = config_stream,
    ...             directories = platformdirs.PlatformDirs( 'benchmark', ensure_exists = False )
    ...         )
    ...         end_time = time.time( )
    ...         duration = end_time - start_time
    ...         config_keys = len( globals_dto.configuration )
    ...         print( f"{config_size} config: {duration:.3f}s, {config_keys} sections" )
    ...         return duration


Integration with Testing Frameworks
===============================================================================

Example integration with pytest-like testing patterns:

.. doctest:: Advanced.TestFramework

    >>> class TestAppCore:
    ...     ''' Example test class showing appcore testing patterns. '''
    ...     
    ...     async def setup_test_environment( self, test_name ):
    ...         ''' Set up isolated test environment. '''
    ...         config_content = f'''
    ...         [application]
    ...         name = "{test_name}"
    ...         test_mode = true
    ...         
    ...         [testing]
    ...         isolation = true
    ...         '''
    ...         config_stream = io.StringIO( config_content )
    ...         test_dirs = platformdirs.PlatformDirs( test_name, ensure_exists = False )
    ...         async with contextlib.AsyncExitStack( ) as exits:
    ...             globals_dto = await appcore.prepare(
    ...                 exits,
    ...                 configfile = config_stream,
    ...                 directories = test_dirs,
    ...                 environment = { 'TEST_MODE': 'true' }
    ...             )
    ...             return globals_dto
    ...     
    ...     async def test_basic_functionality( self ):
    ...         ''' Test basic appcore functionality. '''
    ...         globals_dto = await self.setup_test_environment( 'basic-test' )
    ...         assert globals_dto.application.name == 'basic-test'
    ...         config = globals_dto.configuration
    ...         assert config[ 'testing' ][ 'isolation' ] == True
    ...         print( 'Basic functionality test passed' )
    ...         return True
    ...     
    ...     async def test_configuration_override( self ):
    ...         ''' Test configuration override functionality. '''
    ...         globals_dto = await self.setup_test_environment( 'override-test' )
    ...         # Test that test mode is enabled
    ...         config = globals_dto.configuration
    ...         test_mode = config[ 'application' ][ 'test_mode' ]
    ...         assert test_mode == True
    ...         print( 'Configuration override test passed' )
    ...         return True
    >>> 
    >>> # Example test execution
    >>> test_suite = TestAppCore( )
    >>> async def run_test_suite( ):  # doctest: +SKIP
    ...     test1 = await test_suite.test_basic_functionality( )
    ...     test2 = await test_suite.test_configuration_override( )
    ...     return test1 and test2


Resource Management Patterns
===============================================================================

Advanced patterns for managing resources with AsyncExitStack:

.. doctest:: Advanced.Resources

    >>> import tempfile
    >>> 
    >>> async def test_with_temporary_resources( ):
    ...     ''' Test using temporary resources that are cleaned up automatically. '''
    ...     async with contextlib.AsyncExitStack( ) as exits:
    ...         # Create temporary directory for test
    ...         temp_dir = exits.enter_context( tempfile.TemporaryDirectory( ) )
    ...         print( f"Created temp directory: {temp_dir}" )
    ...         # Use custom directories pointing to temp location
    ...         test_dirs = platformdirs.PlatformDirs( 'temp-test', ensure_exists = False )
    ...         # Initialize appcore with temporary resources
    ...         globals_dto = await appcore.prepare(
    ...             exits,
    ...             directories = test_dirs,
    ...             configfile = io.StringIO( '''
    ...             [application]
    ...             name = "temp-test"
    ...             [testing]
    ...             temporary = true
    ...             ''' )
    ...         )
    ...         # Use the globals object
    ...         config = globals_dto.configuration
    ...         is_temporary = config[ 'testing' ][ 'temporary' ]
    ...         print( f"Using temporary setup: {is_temporary}" )
    ...         return globals_dto
    ...     # temp_dir is automatically cleaned up when exiting the context


Next Steps
===============================================================================

This covers advanced usage patterns for appcore. For foundational topics, see:

- **Basic Usage** - Application setup and platform directories
- **Configuration Management** - TOML loading and hierarchical includes
- **Environment Handling** - Development detection and environment variables