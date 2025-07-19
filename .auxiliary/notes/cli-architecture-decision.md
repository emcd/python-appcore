# CLI Architecture Decision

**Date**: 2025-07-16
**Context**: Post-1.2 release planning
**Status**: Decided

## Problem Statement

The `emcd-appcore` package has successfully reduced redundancy in CLI
applications by providing common application initialization patterns. However,
CLI applications still duplicate actual CLI skeletons based on the `tyro` CLI
generator (e.g., `../python-project-common/sources/emcdproj/cli.py`).

**Question**: Should we create a separate `emcd-appcore-cli` package
distribution for CLI foundation, or add it as an optional dependency group
within `emcd-appcore`?

## Options Considered

### Option 1: Separate Package (`emcd-appcore-cli`)
**Pros:**
- Clean separation of concerns
- Core package stays minimal
- Independent versioning possible
- Clear namespace separation

**Cons:**
- Version compatibility matrix to maintain
- API compatibility challenges between packages
- Separate release cycles and CI/CD overhead
- Discovery challenges for users
- Maintenance burden across multiple repos

### Option 2: Optional Dependency Group (Recommended)
**Pros:**
- Tight integration with core appcore systems
- Guaranteed API compatibility
- Single release cycle ensures cohesion
- Better user experience (`pip install emcd-appcore[cli]`)
- Shared infrastructure (tests, docs, CI)
- Core package stays lightweight (optional deps only when requested)
- Easy migration path if extraction needed later

**Cons:**
- Slightly more complex package structure
- All dependencies under one repo

## Decision

**Chosen**: Optional dependency group approach within `emcd-appcore`

### Rationale
1. **Consistency with existing patterns**: This approach aligns with `icecream-truck` package architecture, which uses "recipes" as optional dependency groups
2. **Tight integration benefits**: CLI scaffolding will be tightly coupled with appcore's preparation/configuration system
3. **Practical user experience**: Users already depending on appcore for CLI apps can simply add `[cli]`
4. **Maintenance efficiency**: Single repo, CI/CD, documentation site
5. **Future flexibility**: Can extract to separate package later if complexity grows

## Implementation Plan

### Package Structure
```
sources/appcore/
├── __init__.py              # Core exports
├── cli/                     # New CLI module
│   ├── __init__.py         # CLI exports (only if [cli] installed)
│   ├── foundation.py       # Base CLI scaffolding
│   ├── preparation.py      # CLI-specific preparation helpers
│   └── commands.py         # Common command patterns
├── application.py          # Existing core
├── preparation.py          # Existing core
└── ...                     # Other existing modules
```

### Dependencies
```toml
[project.optional-dependencies]
cli = ["tyro>=0.8.0", "rich>=13.0.0"]  # CLI-specific dependencies
```

### Usage Pattern
```python
# In CLI applications
from appcore.cli import CliFoundation  # Only works with [cli] extra
from appcore import prepare            # Always available

class MyCli(CliFoundation):
    """Built on appcore patterns"""
    pass
```

## Migration Strategy

### Phase 1: Foundation (1.3.0)
- Add `cli` optional dependency group
- Implement basic `CliFoundation` class
- Create CLI-specific preparation helpers

### Phase 2: Enhancement (1.4.0)
- Add common command patterns
- Implement configuration integration
- Add CLI-specific utilities

### Phase 3: Adoption
- Migrate existing CLI applications to use new foundation
- Document patterns and best practices

## Success Criteria

1. **Reduced duplication**: CLI applications can use common scaffolding
2. **Maintained flexibility**: Core package stays lightweight
3. **Integration quality**: CLI features work seamlessly with appcore patterns
4. **User experience**: Simple installation and discovery

## Future Considerations

**When to reconsider separate package:**
- CLI becomes very complex (>3-4 modules)
- Need to support multiple application frameworks beyond appcore
- CLI dependencies become heavy (like GUI frameworks)

## References

- Post-1.2 release discussion
- `icecream-truck` package architecture (recipes as optional dependencies)
- Existing CLI applications using appcore patterns
