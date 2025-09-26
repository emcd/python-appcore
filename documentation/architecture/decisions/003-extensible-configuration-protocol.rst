*******************************************************************************
003. Extensible Configuration Protocol
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

Applications require diverse configuration sources: TOML files, environment
variables, databases, APIs, and custom formats. A framework configuration
system must support TOML out-of-box while enabling integration with existing
configuration infrastructure.

Configuration loading involves complex requirements: hierarchical merging,
template variable processing, environment overrides, and validation. Different
sources need consistent behavior while supporting source-specific features.

Decision
===============================================================================

Implement ``AcquirerAbc`` protocol for pluggable configuration sources with
default TOML implementation. All acquirers support consistent merging behavior,
template variables, and environment overrides while allowing source-specific
extensions.

Alternatives
===============================================================================

**Fixed TOML-only configuration**
  - Rejected: Would prevent integration with existing configuration systems
  - Rejected: Would limit framework adoption in environments with established patterns

**Plugin architecture with discovery**
  - Rejected: Would add complexity without clear benefit for core use cases
  - Rejected: Would require dynamic loading and version management

**Multiple separate configuration APIs**
  - Rejected: Would fragment the configuration interface and complicate usage
  - Rejected: Would prevent consistent behavior across configuration sources

Consequences
===============================================================================

**Positive**
  - TOML configuration works out-of-box for standard use cases
  - Custom configuration sources integrate cleanly with framework patterns
  - Consistent merging and override behavior across all sources
  - Framework adoption possible in environments with existing configuration systems

**Negative**
  - Protocol implementation requires understanding of internal configuration handling
  - Custom acquirers must implement template variable and merging logic
  - Additional abstraction layer for configuration processing

**Neutral**
  - Protocol pattern common in modern Python frameworks
  - Configuration extensibility expected by framework users