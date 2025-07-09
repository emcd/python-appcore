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
Test Structure and Organization
*******************************************************************************

This document describes the structure and numbering semantics of the test
suite for the ``appcore`` package.

Directory Structure
===============================================================================

The test suite is organized as follows::

    tests/
    ├── README.rst                    # This file
    └── test_000_appcore/            # appcore package tests
        ├── __init__.py              # Test package initialization
        ├── fixtures.py              # Common test fixtures and utilities
        ├── test_000_package.py      # Package-level tests
        ├── test_010_base.py         # Base classes and foundational code
        ├── test_100_exceptions.py   # Exception handling
        ├── test_110_generics.py     # Generic utilities
        ├── test_120_asyncf.py       # Async function utilities
        ├── test_130_dictedits.py    # Dictionary editing utilities
        ├── test_140_io.py           # I/O operations
        ├── test_200_application.py  # Application information
        ├── test_210_distribution.py # Distribution discovery
        ├── test_300_configuration.py # Configuration management
        ├── test_400_state.py        # State management
        ├── test_410_environment.py  # Environment handling
        ├── test_420_inscription.py  # Inscription/logging
        └── test_500_preparation.py  # Application preparation/integration

Namespace Rationale
===============================================================================

The ``test_000_appcore`` directory provides a unique namespace for the test
modules, which serves several purposes:

1. **Future Multi-Package Support**: If this project ever needs to test
   multiple packages, we can add ``test_001_otherpackage``, etc.

2. **Import Isolation**: The unique namespace prevents test module name
   conflicts with source modules.

3. **Clear Test Organization**: It's immediately clear that these tests
   belong to the ``appcore`` package.

Test File Numbering System
===============================================================================

Test files use a three-digit numbering system to enforce execution order and
logical grouping:

Range 000-099: Foundation and Package Tests
---------------------------------------------------------------

- **000-009**: Package-level tests (imports, metadata, structure)
- **010-019**: Base classes and foundational infrastructure

Range 100-199: Core Utilities
---------------------------------------------------------------

- **100-109**: Exception handling and error management
- **110-119**: Generic utilities and type handling
- **120-129**: Async function utilities and coroutine support
- **130-139**: Dictionary editing and manipulation utilities
- **140-149**: I/O operations and file handling

Range 200-299: Application Layer
---------------------------------------------------------------

- **200-209**: Application information and metadata
- **210-219**: Distribution discovery and package introspection
- **220-299**: *Reserved for future application-layer components*

Range 300-399: Configuration System
---------------------------------------------------------------

- **300-309**: Configuration management and TOML processing
- **310-399**: *Reserved for future configuration components*

Range 400-499: State and Environment Management
---------------------------------------------------------------

- **400-409**: State management and globals handling
- **410-419**: Environment detection and variable processing
- **420-429**: Inscription (logging) and output handling
- **430-499**: *Reserved for future state/environment components*

Range 500-599: Integration and Preparation
---------------------------------------------------------------

- **500-509**: Application preparation and initialization
- **510-599**: *Reserved for future integration components*

Range 600-999: Reserved for Future Use
---------------------------------------------------------------

These ranges are reserved for future package expansion and new component
categories.

Test Function Naming Within Files
===============================================================================

Within each test file, test functions follow a consistent naming pattern:

1. **Descriptive Names**: Function names describe the behavior being tested,
   not the implementation details.

2. **Hierarchical Organization**: Tests are typically organized by the
   component or method being tested, then by scenario.

3. **Async Indicators**: Async tests include ``_async`` in the name when
   testing async-specific behavior.

Example naming pattern::

    def test_basic_functionality():
        ''' Basic feature works as expected. '''
        
    def test_error_handling():
        ''' Error conditions are handled gracefully. '''
        
    @pytest.mark.asyncio
    async def test_async_operations():
        ''' Async operations complete successfully. '''

Fixtures and Utilities
===============================================================================

The ``fixtures.py`` file contains common test utilities and fixtures used
across multiple test files:

- **create_temp_directories_and_distribution()**: Creates temporary directory
  structures and distribution information for testing file operations.

- **create_globals_with_temp_dirs()**: Creates complete globals DTOs with
  temporary directories for integration testing.

- **create_config_template_files()**: Creates configuration template files
  for testing configuration processing.

These fixtures follow the dependency injection patterns described in the
`Test Writing Guide <../.auxiliary/notes/test-writing-guide.md>`_.

Test Execution Order
===============================================================================

The numbering system ensures that tests run in dependency order:

1. **Foundation first** (000-099): Package structure and base classes
2. **Core utilities** (100-199): Building blocks for higher-level components
3. **Application layer** (200-299): Application-specific functionality
4. **Configuration** (300-399): Configuration processing and management
5. **State management** (400-499): Environment and state handling
6. **Integration** (500-599): End-to-end application preparation

This order ensures that fundamental components are tested before the
components that depend on them.

Coverage and Quality Standards
===============================================================================

The test suite maintains high coverage standards:

- **Target**: 100% line and branch coverage
- **Current**: 99% coverage with systematic gap closure
- **Strategy**: Coverage-driven test development targeting specific uncovered lines

All tests must follow the standards defined in the
`Test Writing Guide <../.auxiliary/notes/test-writing-guide.md>`_:

- Behavior-focused docstrings
- No blank lines in function bodies
- Dependency injection over monkey-patching
- Real temporary directories for file operations
- Strategic use of ``pyfakefs`` for sync filesystem operations

Adding New Tests
===============================================================================

When adding new tests:

1. **Choose the appropriate range** based on the component being tested
2. **Use the next available number** within that range
3. **Follow naming conventions** for both files and functions
4. **Include behavior-focused docstrings** for all test functions
5. **Use existing fixtures** from ``fixtures.py`` when possible
6. **Follow the patterns** established in the Test Writing Guide

For questions about test organization or to propose new numbering ranges,
consult the development team.