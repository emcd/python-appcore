# State Management

## Purpose

Provides immutable global state management for application configuration, distribution information, and runtime context.

## Requirements

### Requirement: Immutable Global State

The system SHALL provide an immutable `Globals` dataclass that contains all
framework state and cannot be modified after creation.

#### Scenario: State creation during initialization
- **WHEN** `prepare()` completes successfully
- **THEN** a `Globals` instance is returned with all fields populated
- **AND** all fields are immutable (frozen dataclass with accretive containers)

#### Scenario: State access by application code
- **WHEN** application code accesses `Globals` fields
- **THEN** field values are consistent with the state at initialization time
- **AND** no field can be modified through the `Globals` reference

#### Scenario: State serialization
- **WHEN** `Globals.as_dictionary()` is called
- **THEN** a shallow copy of all state fields is returned as a dictionary
- **AND** the returned dictionary is independent of the `Globals` instance

### Requirement: Location Provision

The system SHALL provide methods on `Globals` for resolving platform-specific
locations with configuration overrides.

#### Scenario: Default cache location
- **WHEN** `Globals.provide_cache_location()` is called without arguments
- **THEN** the platform-default cache directory is returned
- **AND** the directory path is derived from `platformdirs`

#### Scenario: Location with configuration override
- **WHEN** configuration contains a `locations.cache` entry
- **THEN** `Globals.provide_cache_location()` uses the configured path
- **AND** template variables (`{user_cache}`, `{user_home}`, `{application_name}`) are expanded

#### Scenario: Location with subpath appendages
- **WHEN** `Globals.provide_data_location('subdir', 'file.txt')` is called
- **THEN** the subpath is appended to the resolved base location
- **AND** the full path is returned

### Requirement: State Field Composition

The `Globals` dataclass SHALL contain fields for application metadata,
configuration, platform directories, distribution information, and the exit stack.

#### Scenario: Complete state assembly
- **WHEN** `prepare()` assembles the `Globals` instance
- **THEN** the following fields are populated:
  - `application`: `Information` instance with name, publisher, version
  - `configuration`: accretive dictionary with merged configuration
  - `directories`: `PlatformDirs` instance for the application
  - `distribution`: `Information` instance with deployment mode
  - `exits`: the `AsyncExitStack` passed to `prepare()`
