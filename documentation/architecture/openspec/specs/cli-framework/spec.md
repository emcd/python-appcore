# CLI Framework

## Purpose

Provides a type-safe CLI framework with command routing, display options, and integration with the tyro argument parser for Python applications.

## Requirements

### Requirement: Command Base Class

The system SHALL provide an abstract `Command` base class for CLI command
implementations with type-safe argument parsing integration.

#### Scenario: Command implementation
- **WHEN** a class inherits from `Command`
- **THEN** it must implement an `execute()` method
- **AND** the command receives `Globals` for access to framework state

#### Scenario: Command argument parsing
- **WHEN** a command class defines typed fields
- **THEN** `tyro` automatically generates argument parsing from type annotations
- **AND** help text is generated from field docstrings

#### Scenario: Command execution
- **WHEN** a command instance is called with `Globals`
- **THEN** the `execute()` method is invoked with the provided state
- **AND** the command can access configuration, directories, and inscription

### Requirement: Application Base Class

The system SHALL provide an `Application` base class for CLI application
definition with automatic command routing.

#### Scenario: Application definition
- **WHEN** a class inherits from `Application`
- **THEN** it defines its command structure through typed fields
- **AND** `tyro` generates the CLI interface from the class definition

#### Scenario: Application preparation
- **WHEN** `Application.prepare()` is called
- **THEN** it extends the standard `prepare()` with CLI-specific initialization
- **AND** display options and inscription are configured from CLI arguments

#### Scenario: Application execution
- **WHEN** `Application()` is called (the instance is callable)
- **THEN** argument parsing occurs via `tyro`
- **AND** the application's `execute()` method is invoked with `Globals`

### Requirement: Command Routing via Type Guards

The system SHALL use `isinstance()` type guards for command routing within
CLI applications.

#### Scenario: Single command routing
- **WHEN** an application has a single command type
- **THEN** the application directly instantiates and executes the command

#### Scenario: Multiple command routing
- **WHEN** an application has multiple command types
- **THEN** the application uses `isinstance()` checks to determine which
  command to execute
- **AND** each command type is a distinct class inheriting from `Command`

#### Scenario: Subcommand composition
- **WHEN** commands need subcommands
- **THEN** each subcommand is a separate `Command` subclass
- **AND** the parent command routes to subcommands via `isinstance()` checks

### Requirement: Display and Output Control

The system SHALL provide `DisplayOptions` for controlling output presentation
and routing.

#### Scenario: Presentation mode selection
- **WHEN** display options specify a presentation mode (plain, rich, json, toml)
- **THEN** output is formatted according to the selected mode
- **AND** rich mode enables terminal-aware formatting when available

#### Scenario: Output stream routing
- **WHEN** display options specify a target stream (stdout, stderr, file)
- **THEN** output is directed to the specified stream
- **AND** file targets are created with proper resource management

#### Scenario: Colorization control
- **WHEN** display options specify colorization preferences
- **THEN** ANSI color codes are applied or stripped accordingly
- **AND** non-TTY streams automatically disable colorization
