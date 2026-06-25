# appcore

Application foundation components for Python: streamlined async initialization,
configuration management, platform directories, logging setup, and environment
handling.

## System Architecture

### Core Components

**Application Foundation**
- `preparation.py` — Single-point async initialization via `prepare()`
- `state.py` — Immutable global state management through `Globals` dataclass
- `application.py` — Application metadata and platform directory integration

**Configuration Management**
- `configuration.py` — Hierarchical TOML configuration with extensible acquirer protocol
- `dictedits.py` — Configuration editing and merging utilities
- `environment.py` — Environment variable processing and integration

**CLI Framework**
- `cli/` — Command and application base classes with rich output control
- `introspection.py` — Self-inspection commands demonstrating CLI patterns
- `inscription.py` — Integrated logging and diagnostic output

**Platform Integration**
- `distribution.py` — Development vs production deployment detection
- `io.py` — Cross-platform I/O utilities
- `asyncf.py` — Async utilities and patterns

**Infrastructure**
- `exceptions.py` — Comprehensive exception hierarchy with chaining support
- `generics.py` — Result types and generic utilities

### Component Relationships

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│  Configuration  │───▶│   Environment   │
│   Foundation    │    │   Management    │    │   Integration   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  State Manager  │◀───│  CLI Framework  │───▶│    Platform     │
│   (Globals)     │    │   (Commands)    │    │   Detection     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Exceptions    │    │   Inscription   │    │  Infrastructure │
│   & Results     │    │   & Logging     │    │   Utilities     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

**Initialization Flow**
1. `prepare()` function coordinates async initialization
2. Distribution detection determines deployment mode
3. Platform directories discovered and created
4. Configuration loaded with hierarchical merging
5. `Globals` dataclass created with immutable application state
6. Logging configured based on deployment mode and preferences

**CLI Application Flow**
1. `Application.prepare()` extends foundation initialization
2. Command routing via `isinstance()` type guards
3. Display options control output format and routing
4. Rich terminal detection enables automatic format adaptation
5. Stream routing directs output to stdout, stderr, or files

**Configuration Flow**
1. `AcquirerAbc` protocol enables pluggable configuration sources
2. TOML files loaded with include processing and template variables
3. Environment overrides applied with precedence rules
4. Configuration edits merged into final immutable dictionary

## Package Structure

```
appcore/
├── __/                      # Centralized import hub
│   ├── __init__.py          # Re-exports core utilities
│   ├── imports.py           # External library imports
│   └── nomina.py            # Package-specific naming constants
├── __init__.py              # Package entry point
├── __main__.py              # CLI entry point (python -m appcore)
├── py.typed                 # Type checking marker
├── exceptions.py            # Package exception hierarchy
├── preparation.py           # Single-point async initialization
├── state.py                 # Immutable global state management
├── application.py           # Application metadata and platform directories
├── configuration.py         # Hierarchical TOML configuration system
├── dictedits.py             # Configuration editing utilities
├── environment.py           # Environment variable processing
├── distribution.py          # Development vs production detection
├── cli/
│   ├── __init__.py
│   ├── core.py              # CLI foundation classes and interfaces
│   └── standard.py          # Rendering extensions
├── introspection.py         # Self-inspection CLI commands
├── inscription.py           # Logging and diagnostic output
├── io.py                    # Cross-platform I/O utilities
├── asyncf.py                # Async utilities and patterns
└── generics.py              # Result types and generic utilities
```

All package modules use the standard `__` import pattern for centralized
dependency management.

## Architectural Patterns

### Single Point of Initialization

The `prepare()` function in `preparation.py` coordinates all framework setup.
Its async design allows concurrent external initialization, and it returns an
immutable `Globals` dataclass with all framework state.

### Immutable Data Architecture

All state management uses immutable dataclasses. Configuration is stored as
accretive dictionary objects (immutable after assignment). Thread-safe by
design, preventing accidental mutation.

### Extensible Configuration Protocol

`AcquirerAbc` protocol enables pluggable configuration sources. The default
TOML implementation supports hierarchical loading with template variables and
environment overrides.

### CLI Command Routing

`isinstance()` type guards provide command discovery with Rich terminal
integration and automatic format detection. Stream routing directs output to
stdout, stderr, or files.

### Exception Organization

Package-wide exceptions are centralized in `exceptions.py` following the
hierarchy: `Omniexception` → `Omnierror` → specific exceptions with consistent
naming patterns (`*Failure`, `*Invalidity`, `*Absence`).

## Quality Attributes

**Type Safety** — 100% type annotation coverage for all public APIs. Generic
types for customizable components. Protocol-based interfaces for extensibility.

**Cross-Platform Compatibility** — Automatic platform detection and adaptation.
Consistent behavior across Windows, macOS, Linux. PyPy compatibility through
careful metaclass handling.

**Maintainability** — Clear separation of concerns between modules. Immutable
data prevents state-related bugs. Comprehensive exception hierarchy with proper
chaining.

**Testability** — 100% test coverage with edge case handling. Dependency
injection through constructor parameters. Clear interfaces enable easy mocking.

## Deployment Modes

**Development Mode** — Automatic detection based on package installation method.
Enhanced logging and debugging capabilities. Configuration loading from
development directories.

**Production Mode** — Optimized for deployed applications. Platform-standard
directory usage. Streamlined logging configuration.
