# Configuration Management

## Purpose

Provides extensible configuration acquisition with a default TOML implementation, hierarchical merging, template variables, and environment overrides.

## Requirements

### Requirement: Extensible Configuration Acquisition

The system SHALL provide an `AcquirerAbc` protocol that enables pluggable
configuration sources with a default TOML implementation.

#### Scenario: Default TOML configuration loading
- **WHEN** no custom acquirer is provided to `prepare()`
- **THEN** the `TomlAcquirer` loads configuration from TOML files
- **AND** configuration is merged into an accretive dictionary

#### Scenario: Custom configuration acquirer
- **WHEN** an application provides a custom `AcquirerAbc` implementation
- **THEN** the custom acquirer is used for configuration loading
- **AND** the result is merged into the standard configuration dictionary

#### Scenario: Configuration source protocol compliance
- **WHEN** a custom acquirer implements `AcquirerAbc`
- **THEN** it must provide a method that returns a configuration dictionary
- **AND** the dictionary is merged with environment overrides and edits

### Requirement: Hierarchical Configuration Merging

The system SHALL support hierarchical configuration loading with include
processing, template variables, and environment overrides.

#### Scenario: Configuration file includes
- **WHEN** a TOML file contains an `includes` array of file paths
- **THEN** referenced files are loaded and merged in order
- **AND** later files override values from earlier files

#### Scenario: Template variable expansion
- **WHEN** configuration values contain `{variable}` placeholders
- **THEN** placeholders are expanded using values from the configuration itself
- **AND** undefined variables cause a clear error

#### Scenario: Environment variable overrides
- **WHEN** environment variables match the pattern `{APP}_CONFIG_{KEY}`
- **THEN** those values override configuration file values
- **AND** environment overrides take highest precedence

### Requirement: Configuration Edits

The system SHALL support configuration edits that are applied after loading
and before final state assembly.

#### Scenario: Edit application during initialization
- **WHEN** `configedits` are provided to `prepare()`
- **THEN** edits are applied to the loaded configuration in order
- **AND** the final configuration reflects all edits

#### Scenario: Edit types
- **WHEN** configuration edits include set, update, and delete operations
- **THEN** set replaces a value, update merges, and delete removes
- **AND** edits operate on the nested dictionary path

### Requirement: Enablement Tristate

The system SHALL provide an `EnablementTristate` enum for disable/retain/enable
configuration options.

#### Scenario: Boolean conversion
- **WHEN** `EnablementTristate.Disable` is evaluated in a boolean context
- **THEN** it returns `False`
- **AND** `EnablementTristate.Enable` returns `True`

#### Scenario: Retain natural state
- **WHEN** `EnablementTristate.Retain` is used
- **THEN** the system preserves the existing or default behavior
- **AND** no explicit enable/disable override is applied
