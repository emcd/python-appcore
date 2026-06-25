## MODIFIED Requirements

### Requirement: Inscription Control

The `Control` dataclass SHALL carry ictr-specific configuration fields for
trace levels, active flavors, dispatcher aliasing, and installation control.

#### Scenario: Default ictr configuration
- **WHEN** `Control` is created without ictr-specific arguments
- **THEN** `active_flavors`, `ictr_alias`, `trace_levels`, and `install_ictr` are `absent`
- **AND** the ictr dispatcher uses environment-variable or default configuration

#### Scenario: Explicit ictr configuration
- **WHEN** `Control` is created with `active_flavors=('note','error')` and `trace_levels=2`
- **THEN** those values override environment variables and defaults
- **AND** the ictr dispatcher is configured with the provided values

#### Scenario: Installation control
- **WHEN** `Control` is created with `install_ictr=True` (or default `absent` which resolves to `True`)
- **THEN** the ictr dispatcher is installed into builtins after preparation
- **WHEN** `Control` is created with `install_ictr=False`
- **THEN** the dispatcher is created but not installed

### Requirement: Dual Inscription Preparation

The `prepare()` function SHALL configure both Python `logging` and `ictr`
as parallel inscription subsystems.

#### Scenario: Standard preparation with ictr
- **WHEN** `prepare()` is called with a `Control` instance
- **THEN** `_prepare_scribes_logging()` configures Python logging
- **AND** `_prepare_scribes_ictr()` configures and installs the ictr dispatcher
- **AND** both subsystems share the same output target

#### Scenario: Ictr dispatcher installation
- **WHEN** `_prepare_scribes_ictr()` is called with `install_ictr=True` (default)
- **THEN** the ictr dispatcher is installed into builtins with the configured alias
- **AND** application code can use `ic()` immediately after `prepare()` returns

#### Scenario: Ictr without installation
- **WHEN** `_prepare_scribes_ictr()` is called with `install_ictr=False`
- **THEN** the ictr dispatcher is created but not installed into builtins
- **AND** the dispatcher is available for explicit use

### Requirement: Level-to-Flavor Derivation

The system SHALL derive active ictr flavors from the inscription level when
no explicit flavor configuration is provided.

#### Scenario: Debug level flavors
- **WHEN** inscription level is `debug` and no explicit flavors are set
- **THEN** active flavors include `note`, `monition`, and all error-family flavors
- **AND** semantic flavors (`future`, `success`, `advice`) are always active

#### Scenario: Info level flavors
- **WHEN** inscription level is `info` and no explicit flavors are set
- **THEN** active flavors include `note` and all error-family flavors
- **AND** `monition` is excluded

#### Scenario: Error level flavors
- **WHEN** inscription level is `error` or `critical`
- **THEN** only error-family and semantic flavors are active

### Requirement: Colorization Control

The system SHALL control ictr colorization based on the inscription
presentation mode using a custom printer factory.

#### Scenario: Plain or null mode
- **WHEN** presentation mode is `Plain` or `Null`
- **THEN** `_produce_ictr_generalcfg()` provides a printer factory that wraps
  the output stream with ANSI stripping
- **AND** ANSI escape sequences are suppressed regardless of TTY detection

#### Scenario: Rich mode
- **WHEN** presentation mode is `Rich`
- **THEN** the ictr dispatcher uses the default printer factory
- **AND** TTY detection and `NO_COLOR` are handled by ictr's printer internally

### Requirement: Environment Variable Overrides

The system SHALL support application-specific environment variables for
ictr configuration with explicit precedence.

#### Scenario: Application-specific active flavors
- **WHEN** environment variable `{APP_UPPER}_ACTIVE_FLAVORS` is set
- **AND** no explicit `active_flavors` argument is provided to `Control`
- **THEN** the environment variable value is used for flavor configuration

#### Scenario: Application-specific trace levels
- **WHEN** environment variable `{APP_UPPER}_TRACE_LEVELS` is set
- **AND** no explicit `trace_levels` argument is provided to `Control`
- **THEN** the environment variable value is used for trace depth configuration

#### Scenario: Explicit override disables environment
- **WHEN** explicit `active_flavors` or `trace_levels` is provided to `Control`
- **THEN** the corresponding environment variable is ignored

#### Scenario: Precedence order
- **WHEN** multiple sources provide ictr configuration
- **THEN** precedence is: explicit `Control` args > app-specific env (`{APP}_*`) > ictr env (`ICTR_*`) > defaults

### Requirement: CLI Inscription Options

The CLI `InscriptionControl` SHALL expose ictr-specific options for trace
levels and active flavors.

#### Scenario: Trace level CLI option
- **WHEN** `--trace-levels 2` is passed on the command line
- **THEN** `InscriptionControl.trace_levels` is set to `2`
- **AND** `as_control()` passes it to `inscription.Control`

#### Scenario: Active flavors CLI option
- **WHEN** `--active-flavors note --active-flavors error` is passed
- **THEN** `InscriptionControl.active_flavors` is set to `('note', 'error')`
- **AND** `as_control()` passes it to `inscription.Control`
