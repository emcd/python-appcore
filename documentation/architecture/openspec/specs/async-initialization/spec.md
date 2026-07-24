# Async Initialization

## Purpose

Provides a single-point async initialization mechanism that coordinates configuration loading, inscription setup, and state assembly for Python applications.

## Requirements

### Requirement: Single-Point Async Preparation

The system SHALL provide a single `prepare()` function that coordinates all
framework initialization asynchronously.

#### Scenario: Basic application initialization
- **WHEN** an application calls `prepare()` with an `AsyncExitStack`
- **THEN** the system initializes distribution detection, platform directories,
  configuration, and inscription
- **AND** returns an immutable `Globals` dataclass with all framework state

#### Scenario: Custom application metadata
- **WHEN** an application provides an `ApplicationInformation` instance to `prepare()`
- **THEN** the system uses the provided metadata for platform directory derivation
- **AND** configuration loading uses the application name for environment variable prefixes

#### Scenario: Custom configuration acquirer
- **WHEN** an application provides a custom `AcquirerAbc` implementation to `prepare()`
- **THEN** the system uses the custom acquirer for configuration loading
- **AND** all other initialization steps proceed normally

#### Scenario: Resource cleanup on exit
- **WHEN** the application's `AsyncExitStack` is closed
- **THEN** all resources registered during initialization are properly cleaned up
- **AND** cleanup occurs in reverse registration order

### Requirement: Async Resource Management

The system SHALL integrate with `AsyncExitStack` for proper lifecycle management
of async resources.

#### Scenario: Concurrent resource initialization
- **WHEN** external async resources are registered during `prepare()`
- **THEN** those resources are managed by the provided `AsyncExitStack`
- **AND** cleanup is guaranteed even if initialization partially fails

#### Scenario: Exit stack propagation
- **WHEN** `prepare()` completes successfully
- **THEN** the `AsyncExitStack` is stored in `Globals.exits`
- **AND** application code can register additional resources via `Globals.exits`
