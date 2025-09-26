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
Building CLI Applications
*******************************************************************************


Introduction
===============================================================================

The ``appcore.cli`` module provides a comprehensive framework for building
command-line applications that integrate seamlessly with appcore's
configuration and initialization systems. This guide demonstrates practical
patterns for creating CLIs with multiple output formats, flexible stream
routing, and rich presentation capabilities.


Using the CLI Module
===============================================================================


Basic Command Structure
-------------------------------------------------------------------------------

CLI applications in appcore follow a consistent pattern using ``Command`` and
``Application`` base classes:

.. code-block:: python

    from appcore import cli, state, __
    import asyncio

    class GreetCommand( cli.Command ):

        async def execute( self, auxdata: state.Globals ) -> None:
            if not isinstance( auxdata, GreetGlobals ):
                raise TypeError( "GreetCommand requires GreetGlobals" )
            print( f"Hello, {auxdata.username}!" )

    class GreetGlobals( state.Globals ):

        username: str

    class GreetApplication( cli.Application ):

        username: str = "World"

        async def execute( self, auxdata: state.Globals ) -> None:
            command = GreetCommand( )
            await command.execute( auxdata )

        async def prepare( self, exits ) -> state.Globals:
            auxdata_base = await super( ).prepare( exits )
            nomargs = {
                field.name: getattr( auxdata_base, field.name )
                for field in __.dcls.fields( auxdata_base )
                if not field.name.startswith( '_' ) }
            return GreetGlobals( username = self.username, **nomargs )

Commands use ``isinstance()`` type guards to safely access specialized data
while maintaining protocol compliance.


Display Options and Output Control
-------------------------------------------------------------------------------

The ``DisplayOptions`` class provides standardized output configuration:

.. code-block:: python

    from appcore import cli, state
    import json

    class DataGlobals( state.Globals ):

        display: cli.DisplayOptions

    class ShowDataCommand( cli.Command ):

        async def execute( self, auxdata: state.Globals ) -> None:
            if not isinstance( auxdata, DataGlobals ):
                raise TypeError( "ShowDataCommand requires DataGlobals" )
            data = {
                "application": auxdata.application.name,
                "platform": auxdata.directories.user_data_path.as_posix( ),
                "config_keys": list( auxdata.configuration.keys( ) )
            }
            await auxdata.display.render( data )

    class DataApplication( cli.Application ):

        display: cli.DisplayOptions = cli.DisplayOptions( )

        async def execute( self, auxdata: state.Globals ) -> None:
            command = ShowDataCommand( )
            await command.execute( auxdata )

        async def prepare( self, exits ) -> state.Globals:
            auxdata_base = await super( ).prepare( exits )
            nomargs = {
                field.name: getattr( auxdata_base, field.name )
                for field in __.dcls.fields( auxdata_base )
                if not field.name.startswith( '_' ) }
            return DataGlobals( display = self.display, **nomargs )

The ``display.render()`` method automatically handles multiple output formats
based on the presentation mode.


Stream Routing and File Output
-------------------------------------------------------------------------------

Commands can route output to different streams or files:

.. code-block:: python

    from appcore import cli, state
    import asyncio
    from pathlib import Path

    class LoggingGlobals( state.Globals ):

        display: cli.DisplayOptions

    class DiagnosticCommand( cli.Command ):

        async def execute( self, auxdata: state.Globals ) -> None:
            if not isinstance( auxdata, LoggingGlobals ):
                raise TypeError( "DiagnosticCommand requires LoggingGlobals" )
            diagnostic_data = {
                "memory_usage": "45MB",
                "active_connections": 12,
                "cache_hits": 234
            }
            await auxdata.display.render( diagnostic_data )

    class DiagnosticApplication( cli.Application ):

        display: cli.DisplayOptions = cli.DisplayOptions( )

        async def execute( self, auxdata: state.Globals ) -> None:
            command = DiagnosticCommand( )
            enriched_auxdata = LoggingGlobals(
                display = self.display,
                **auxdata.__dict__
            )
            await command.execute( enriched_auxdata )

Users can control output destination through command-line arguments:

.. code-block:: shell

    # Output to stdout (default)
    python -m myapp diagnostic

    # Output to stderr
    python -m myapp --display.target-stream stderr diagnostic

    # Output to file
    python -m myapp --display.target-file report.json diagnostic


Subcommands and Complex Applications
-------------------------------------------------------------------------------

For applications with multiple commands, use tyro's subcommand annotations:

.. code-block:: python

    from appcore import cli, state
    import tyro
    from typing import Union, Annotated

    class StatusGlobals( state.Globals ):

        display: cli.DisplayOptions

    class StatusCommand( cli.Command ):

        async def execute( self, auxdata: state.Globals ) -> None:
            if not isinstance( auxdata, StatusGlobals ):
                raise TypeError( "StatusCommand requires StatusGlobals" )
            status_info = {"status": "running", "uptime": "2h 34m"}
            await auxdata.display.render( status_info )

    class StatsCommand( cli.Command ):

        async def execute( self, auxdata: state.Globals ) -> None:
            if not isinstance( auxdata, StatusGlobals ):
                raise TypeError( "StatsCommand requires StatusGlobals" )
            stats_info = {"requests": 1542, "errors": 3}
            await auxdata.display.render( stats_info )

    class MonitorApplication( cli.Application ):

        display: cli.DisplayOptions = cli.DisplayOptions( )
        command: Union[
            Annotated[
                StatusCommand,
                tyro.conf.subcommand( "status", prefix_name = False ),
            ],
            Annotated[
                StatsCommand,
                tyro.conf.subcommand( "stats", prefix_name = False ),
            ],
        ] = StatusCommand( )

        async def execute( self, auxdata: state.Globals ) -> None:
            enriched_auxdata = StatusGlobals(
                display = self.display, **auxdata.__dict__ )
            await self.command.execute( enriched_auxdata )

This creates a CLI with subcommands accessible as ``python -m myapp status`` and ``python -m myapp stats``.


Demonstration: The appcore CLI
===============================================================================


Overview
-------------------------------------------------------------------------------

The built-in ``appcore`` CLI tool demonstrates all the patterns described above.
It provides introspection capabilities for configuration, environment variables,
and platform directories, showcasing practical CLI implementation techniques.


Configuration Introspection
-------------------------------------------------------------------------------

View your application's merged configuration from TOML files:

.. code-block:: shell

    # Default rich format with syntax highlighting
    python -m appcore configuration

    # JSON format for programmatic consumption
    python -m appcore configuration --display.presentation json

    # TOML format matching input files
    python -m appcore configuration --display.presentation toml

    # Plain text format for simple parsing
    python -m appcore configuration --display.presentation plain

The configuration command shows the final merged configuration after processing
all TOML files, includes, and template variable substitution.


Environment Variable Inspection
-------------------------------------------------------------------------------

Show application-specific environment variables:

.. code-block:: shell

    # Show all APPCORE_* environment variables
    python -m appcore environment

    # JSON format for scripting
    python -m appcore environment --display.presentation json

    # Save to file for later analysis
    python -m appcore environment --display.target-file env-vars.json

The environment command filters environment variables by application name prefix,
showing only variables that affect your application's behavior.


Platform Directory Discovery
-------------------------------------------------------------------------------

Display platform-specific directories for data, configuration, and caching:

.. code-block:: shell

    # Rich format showing directory paths with labels
    python -m appcore directories

    # Save directory paths to file for scripts
    python -m appcore directories --display.target-file dirs.txt

    # JSON format with full path information
    python -m appcore directories --display.presentation json

The directories command shows where your application should store different
types of data according to platform conventions.


Advanced Output Options
-------------------------------------------------------------------------------

Combine presentation formats with output routing for complex scenarios:

.. code-block:: shell

    # Separate main output and logging streams
    python -m appcore configuration --display.target-stream stdout --inscription.target-stream stderr

    # Save both output and logs to files
    python -m appcore configuration --display.target-file config.json --inscription.target-file app.log

    # Rich output with colorization control
    python -m appcore configuration --display.no-colorize --display.presentation rich

    # Force rich terminal capabilities for testing
    python -m appcore configuration --display.assume-rich-terminal --display.presentation rich

These options provide precise control over where different types of output are
directed, enabling integration with shell scripts and monitoring systems.


Configuration File Integration
-------------------------------------------------------------------------------

The appcore CLI integrates with configuration files like any appcore application:

.. code-block:: shell

    # Use specific configuration file
    python -m appcore --configfile /path/to/config.toml configuration

    # Disable environment loading
    python -m appcore --no-environment configuration

Configuration files can specify default presentation formats, output locations,
and logging levels that the CLI will respect.


Implementation Reference
-------------------------------------------------------------------------------

The complete implementation can be found in ``sources/appcore/introspection.py``,
which demonstrates:


- Advanced subcommand patterns with tyro annotations
- Custom DisplayOptions subclasses with additional presentation formats
- Integration between CLI arguments and appcore preparation systems
- Type-safe command implementations using isinstance guards
- Rich terminal detection and colorization handling
- Stream and file output management with proper resource cleanup

This serves as a comprehensive reference for building production CLI applications
with similar capabilities and patterns.
