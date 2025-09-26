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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    python-appcore/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    ├── appcore/          # Main Python package
    │   ├── __/                      # Centralized import hub
    │   │   ├── __init__.py          # Re-exports core utilities
    │   │   ├── imports.py           # External library imports
    │   │   └── nomina.py            # python-appcore-specific naming constants
    │   ├── __init__.py              # Package entry point
    │   ├── __main__.py              # CLI entry point (python -m appcore)
    │   ├── py.typed                 # Type checking marker
    │   ├── exceptions.py            # Package exception hierarchy
    │   ├── preparation.py           # Single-point async initialization
    │   ├── state.py                 # Immutable global state management
    │   ├── application.py           # Application metadata and platform directories
    │   ├── configuration.py         # Hierarchical TOML configuration system
    │   ├── dictedits.py             # Configuration editing utilities
    │   ├── environment.py           # Environment variable processing
    │   ├── distribution.py          # Development vs production detection
    │   ├── cli.py                   # CLI command framework
    │   ├── introspection.py         # Self-inspection CLI commands
    │   ├── inscription.py           # Logging and diagnostic output
    │   ├── io.py                    # Cross-platform I/O utilities
    │   ├── asyncf.py                # Async utilities and patterns
    │   └── generics.py              # Result types and generic utilities
    

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

Component Integration
===============================================================================

Module Organization
-------------------------------------------------------------------------------

**Core Foundation Modules**
  - ``preparation.py`` - Single async ``prepare()`` function for application initialization
  - ``state.py`` - ``Globals`` dataclass for immutable application state
  - ``application.py`` - Application metadata and platform directory integration

**Configuration System**
  - ``configuration.py`` - TOML configuration with ``AcquirerAbc`` protocol
  - ``dictedits.py`` - Configuration merging and editing utilities
  - ``environment.py`` - Environment variable processing and integration

**CLI Framework**
  - ``cli.py`` - ``Command`` and ``Application`` base classes with rich output
  - ``introspection.py`` - Self-inspection commands (configuration, environment, directories)
  - ``inscription.py`` - Integrated logging and diagnostic output control

**Platform and Infrastructure**
  - ``distribution.py`` - Development vs production deployment detection
  - ``io.py`` - Cross-platform I/O utilities and helpers
  - ``asyncf.py`` - Async utilities and exception handling patterns
  - ``generics.py`` - Result types and generic programming utilities

**Exception Organization**

Package-wide exceptions are centralized in ``sources/appcore/exceptions.py``
following the standard hierarchy patterns documented in the `common practices guide
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_.

The exception hierarchy follows ``Omniexception`` → ``Omnierror`` → specific exceptions
with consistent naming patterns (``*Failure``, ``*Invalidity``, ``*Absence``).

Architecture Patterns
===============================================================================

The project implements several key architectural patterns:

**Single Point of Initialization**
  - The ``prepare()`` function in ``preparation.py`` coordinates all framework setup
  - Async design allows concurrent external initialization
  - Returns immutable ``Globals`` dataclass with all framework state

**Immutable Data Architecture**
  - All state management through immutable dataclasses
  - Configuration stored as accretive dictionary objects (immutable after assignment)
  - Thread-safe by design, prevents accidental mutation

**Extensible Configuration Protocol**
  - ``AcquirerAbc`` protocol enables pluggable configuration sources
  - Default TOML implementation with hierarchical loading
  - Template variables and environment overrides

**CLI Command Routing**
  - ``isinstance()`` type guards for command discovery
  - Rich terminal integration with automatic format detection
  - Stream routing to stdout, stderr, or files

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that can evolve as the
project grows. The modular structure supports future expansion while maintaining
clear separation of concerns. For organizational principles and patterns,
refer to the comprehensive common documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
