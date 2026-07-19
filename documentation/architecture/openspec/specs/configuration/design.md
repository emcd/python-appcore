# Design: Extensible Configuration Protocol

## Context

Applications require diverse configuration sources: TOML files, environment
variables, databases, APIs, and custom formats. A framework configuration
system must support TOML out-of-box while enabling integration with existing
configuration infrastructure.

Configuration loading involves complex requirements: hierarchical merging,
template variable processing, environment overrides, and validation. Different
sources need consistent behavior while supporting source-specific features.

## Goals / Non-Goals

**Goals:**
- TOML configuration works out-of-box for standard use cases
- Custom configuration sources integrate cleanly with framework patterns
- Consistent merging and override behavior across all sources
- Framework adoption possible in environments with existing configuration systems

**Non-Goals:**
- Runtime configuration hot-reloading
- Configuration validation schemas (deferred to future work)
- Distributed configuration (etcd, Consul, etc.)
- Configuration encryption or secrets management

## Decisions

### Protocol-Based Configuration Sources

**Decision:** Implement `AcquirerAbc` protocol for pluggable configuration
sources with default TOML implementation. All acquirers support consistent
merging behavior, template variables, and environment overrides while allowing
source-specific extensions.

**Alternatives considered:**
- Fixed TOML-only configuration — Rejected: prevents integration with existing
  configuration systems, limits adoption
- Plugin architecture with discovery — Rejected: adds complexity without clear
  benefit for core use cases, requires dynamic loading
- Multiple separate configuration APIs — Rejected: fragments the interface,
  prevents consistent behavior

### Configuration Edit Mechanism

**Decision:** Provide a `configedits` parameter to `prepare()` that accepts
a sequence of edit operations. Edits are applied after loading and before
state assembly.

**Rationale:** Applications need to modify configuration programmatically
(e.g., based on command-line arguments) without replacing the entire
configuration system.

### Environment Variable Override Pattern

**Decision:** Environment variables follow the pattern `{APP_UPPER}_CONFIG_{KEY}`
where the key uses double-underscore for nesting (e.g., `MY_APP_CONFIG_SERVER__PORT`).

**Rationale:** Consistent with common Python application patterns. The
application name prefix prevents collisions between applications.

## Risks / Trade-offs

- **Risk:** Protocol implementation requires understanding of internal
  configuration handling
  → Mitigation: Clear protocol documentation and reference implementation
- **Risk:** Custom acquirers must implement template variable and merging logic
  → Mitigation: Provide helper functions for common patterns
- **Risk:** Additional abstraction layer for configuration processing
  → Mitigation: Minimal overhead, protocol is simple

## Implementation Notes

The `AcquirerAbc` protocol:

```python
class AcquirerAbc(Protocol):
    async def __call__(
        self,
        exits: AsyncExitStack,
        distribution: DistributionInformation,
        application: ApplicationInformation,
    ) -> dict[str, Any]: ...
```

The `TomlAcquirer` provides the default implementation, loading from
`{directories.user_config_path}/configuration.toml` with includes and
template variable processing.
