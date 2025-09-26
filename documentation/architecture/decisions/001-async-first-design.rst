*******************************************************************************
001. Async-First Design Pattern
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

Python applications increasingly use async patterns for I/O operations, network
requests, and concurrent processing. Traditional synchronous initialization
patterns create barriers for applications that need to coordinate async resource
setup with framework initialization.

Framework initialization typically involves file system operations, configuration
loading, and logging setup that could benefit from async patterns while maintaining
deterministic initialization order.

Decision
===============================================================================

Adopt async-first design for all initialization and resource management patterns.
The primary ``prepare()`` function and all derived initialization methods use
async patterns with ``AsyncExitStack`` integration for proper resource cleanup.

Alternatives
===============================================================================

**Synchronous initialization with async adaptation layer**
  - Rejected: Would require complex adaptation patterns and prevent clean
    integration with async application code
  - Rejected: Would limit future flexibility for async configuration sources

**Dual sync/async APIs**
  - Rejected: Would double the API surface area and create maintenance overhead
  - Rejected: Would lead to inconsistent patterns across the framework

**Mixed approach with sync core and async extensions**
  - Rejected: Would create unclear boundaries and inconsistent usage patterns

Consequences
===============================================================================

**Positive**
  - Applications can initialize external async resources during framework setup
  - Proper resource cleanup through ``AsyncExitStack`` integration
  - Future-ready for async configuration sources (databases, APIs, etc.)
  - Clean integration with modern async application architectures

**Negative**
  - Requires ``asyncio.run()`` wrapper for simple synchronous applications
  - Slight complexity increase for basic use cases
  - Learning curve for developers unfamiliar with async patterns

**Neutral**
  - Async patterns are becoming standard in modern Python applications
  - Framework async requirement aligns with target user expectations