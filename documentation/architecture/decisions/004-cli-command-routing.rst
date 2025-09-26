*******************************************************************************
004. CLI Command Routing via Type Guards
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

CLI applications need flexible command routing that supports subcommands,
argument parsing, and help generation. Traditional approaches use string-based
routing or complex decorator patterns that lack type safety and IDE support.

The framework integrates with ``tyro`` for argument parsing and needs routing
patterns that work with type annotations, support ``isinstance()`` checks, and
enable clean command composition patterns.

Decision
===============================================================================

Use ``isinstance()`` type guards for command routing within CLI applications.
Commands inherit from base ``Command`` class and applications route using type
checks, following the Liskov Substitution Principle for clean inheritance
patterns. Integration with ``tyro`` provides automatic argument parsing and help
generation based on type annotations.

Alternatives
===============================================================================

**String-based command routing**
  - Rejected: Would lack type safety and IDE integration
  - Rejected: Would require manual argument parsing and validation

**Decorator-based routing**
  - Rejected: Would create coupling between routing logic and command implementation
  - Rejected: Would complicate testing and command composition

**Registry-based command discovery**
  - Rejected: Would require explicit registration and create hidden dependencies
  - Rejected: Would complicate command module organization

Consequences
===============================================================================

**Positive**
  - Type-safe command routing with full IDE support
  - Clean integration with ``tyro`` argument parsing
  - Commands are regular classes enabling standard inheritance patterns
  - Easy testing through direct class instantiation
  - Clear command composition and extension patterns

**Negative**
  - Requires explicit ``isinstance()`` checks in application routing logic
  - Command inheritance hierarchy must be carefully designed
  - Learning curve for developers expecting decorator-based routing

**Neutral**
  - Type guard patterns increasingly common in modern Python applications
  - ``isinstance()`` checks are explicit and readable