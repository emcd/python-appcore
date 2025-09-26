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
System Overview
*******************************************************************************

This foundational Python application framework provides comprehensive
infrastructure components for building robust Python applications. The
architecture emphasizes async-first patterns, immutable data structures,
and cross-platform compatibility.

System Architecture
===============================================================================

Core Components
-------------------------------------------------------------------------------

**Application Foundation**
  - ``preparation`` module: Single-point async initialization
  - ``state`` module: Immutable global state management through ``Globals`` dataclass
  - ``application`` module: Application metadata and platform directory integration

**Configuration Management**
  - ``configuration`` module: Hierarchical TOML configuration with extensible acquirer protocol
  - ``dictedits`` module: Configuration editing and merging utilities
  - ``environment`` module: Environment variable processing and integration

**CLI Framework**
  - ``cli`` module: Command and application base classes with rich output control
  - ``introspection`` module: Self-inspection commands demonstrating CLI patterns
  - ``inscription`` module: Integrated logging and diagnostic output

**Platform Integration**
  - ``distribution`` module: Development vs production deployment detection
  - ``io`` module: Cross-platform I/O utilities
  - ``asyncf`` module: Async utilities and patterns

**Infrastructure**
  - ``exceptions`` module: Comprehensive exception hierarchy with chaining support
  - ``generics`` module: Result types and generic utilities

Component Relationships
-------------------------------------------------------------------------------

::

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

Data Flow
-------------------------------------------------------------------------------

**Initialization Flow**
  1. ``prepare()`` function coordinates async initialization
  2. Distribution detection determines deployment mode
  3. Platform directories discovered and created
  4. Configuration loaded with hierarchical merging
  5. ``Globals`` dataclass created with immutable application state
  6. Logging configured based on deployment mode and preferences

**CLI Application Flow**
  1. ``Application.prepare()`` extends foundation initialization
  2. Command routing via ``isinstance()`` type guards
  3. Display options control output format and routing
  4. Rich terminal detection enables automatic format adaptation
  5. Stream routing directs output to stdout, stderr, or files

**Configuration Flow**
  1. ``AcquirerAbc`` protocol enables pluggable configuration sources
  2. TOML files loaded with include processing and template variables
  3. Environment overrides applied with precedence rules
  4. Configuration edits merged into final immutable dictionary

Architectural Patterns
===============================================================================

Async-First Design
-------------------------------------------------------------------------------

All initialization and resource management uses async patterns to enable
concurrent initialization of external dependencies while maintaining
sequential library setup.

**Key Benefits:**
- Applications can initialize other resources during framework preparation
- Proper resource cleanup through ``AsyncExitStack`` integration
- Future-ready for async-heavy applications

Immutable Data Architecture
-------------------------------------------------------------------------------

All application state uses immutable dataclasses to ensure thread safety
and prevent accidental mutation.

**Implementation:**
- ``Globals`` dataclass contains all framework state
- Configuration stored as accretive dictionary objects (immutable after assignment)
- State updates create new instances rather than modifying existing ones

Metaclass-Based Application Factories
-------------------------------------------------------------------------------

The CLI framework uses sophisticated metaclass patterns from the ``classcore``
library to enable declarative application definition.

**Capabilities:**
- Automatic command discovery and routing
- Type-safe argument parsing integration
- Consistent error handling across commands

Extensible Configuration System
-------------------------------------------------------------------------------

Configuration management supports multiple sources through the ``AcquirerAbc``
protocol while maintaining consistent merging behavior.

**Design Features:**
- Pluggable configuration sources (TOML, database, API, etc.)
- Hierarchical loading with include support
- Template variable processing
- Environment variable overrides

Quality Attributes
===============================================================================

**Type Safety**
  - 100% type annotation coverage for all public APIs
  - Generic types for customizable components
  - Protocol-based interfaces for extensibility

**Cross-Platform Compatibility**
  - Automatic platform detection and adaptation
  - Consistent behavior across Windows, macOS, Linux
  - PyPy compatibility through careful metaclass handling

**Maintainability**
  - Clear separation of concerns between modules
  - Immutable data prevents state-related bugs
  - Comprehensive exception hierarchy with proper chaining

**Testability**
  - 100% test coverage with edge case handling
  - Dependency injection through constructor parameters
  - Clear interfaces enable easy mocking and testing

Deployment Architecture
===============================================================================

**Development Mode**
  - Automatic detection based on package installation method
  - Enhanced logging and debugging capabilities
  - Configuration loading from development directories

**Production Mode**
  - Optimized for deployed applications
  - Platform-standard directory usage
  - Streamlined logging configuration

**Cross-Platform Distribution**
  - Single codebase works across all supported platforms
  - Automatic adaptation to platform conventions
  - Consistent CLI behavior regardless of environment