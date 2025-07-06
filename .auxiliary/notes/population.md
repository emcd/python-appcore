# Python AppCore Population Plan

## Overview

This document outlines the plan for populating the `python-appcore` library with common application configuration and initialization functionality extracted from `python-mimeogram` and `python-project-common`.

## Architecture Changes from Feedback

### Module Structure
- Modules are placed directly under `appcore/` (not `appcore/__/`) since they are public interfaces
- The `__/` subpackage remains for internal imports and utilities

### Import Aliases
- `frigid` → `immut` (immutable data structures)
- `accretive` → `accret` (accretive dictionaries)
- `dynadoc` → `ddoc` (dynamic documentation)
- Replace `__.typx.Doc` with `__.ddoc.Doc`

### Immutability Strategy
- Use `frigid` dictionaries instead of `accretive` for truly immutable configurations
- Use `accretive` dictionaries only when accretion behavior is desired

## Target Architecture

```
appcore/
├── __/              # Internal imports and utilities
│   ├── __init__.py
│   ├── imports.py   # Common imports (expanded)
│   └── nomina.py    # Type aliases and names
├── application.py   # Application information management
├── distribution.py  # Distribution detection and management
├── configuration.py # Configuration reading and management
├── globals.py       # Global state DTO and management
├── initialization.py # Async initialization framework
├── debug.py         # Debug output support
└── exceptions.py    # Custom exception hierarchy (existing)
```

## Key Dependencies

### Core Dependencies
- `frigid` (~4.1) - Immutable data structures
- `platformdirs` - Cross-platform directories
- `tomli` - TOML parsing
- `importlib-metadata` - Package metadata
- `icecream-truck` (~1.4) - Debug output (not direct `icecream`)
- `absence` (~1.1) - Optional value handling
- `accretive` - Accretive dictionaries
- `aiofiles` - Async file I/O
- `dynadoc` - Dynamic documentation

### Optional Dependencies
- `tyro` - CLI argument parsing with dataclass integration
- `rich` - Enhanced logging output
- `python-dotenv` - Environment variable loading

## Migration Strategy

### Phase 1: Infrastructure Setup
1. Update `pyproject.toml` with required dependencies
2. Expand `__/imports.py` with new import aliases
3. Update `__/nomina.py` with additional type aliases

### Phase 2: Core Modules
1. **Application Information** (`application.py`)
   - Package name detection
   - Version and publisher information
   - Platform-aware directory management

2. **Distribution Detection** (`distribution.py`)
   - Development vs production environment detection
   - Editable installation handling
   - Package resource management

### Phase 3: Configuration System
1. **Configuration Management** (`configuration.py`)
   - TOML-based configuration loading
   - Hierarchical configuration merging
   - Template-based default configurations
   - Environment variable integration
   - Immutable configuration containers

### Phase 4: State Management
1. **Global State DTO** (`globals.py`)
   - Immutable state containers using `frigid`
   - Centralized application state DTO
   - Resource lifecycle management with `AsyncExitStack`

### Phase 5: Initialization Framework
1. **Async Initialization** (`initialization.py`)
   - Async preparation patterns
   - Dependency injection support
   - Concurrent initialization of components

### Phase 6: Debug Support
1. **Debug Output** (`debug.py`)
   - Conditional debug output
   - Integration with `icecream-truck`
   - Environment-based debug enabling

## Code Migration Principles

### Preservation Requirements
- **Preserve all comments**, including TODOs
- **Preserve code structure** and patterns where applicable
- **Preserve function signatures** and interfaces
- **Preserve error handling** patterns

### Adaptation Guidelines
- Extract common patterns without application-specific logic
- Make functions lightweight (≤30 lines)
- Use dependency injection for configuration
- Prefer immutability using `frigid`
- Support async-first patterns
- Follow existing code style and conventions

## Common Patterns to Extract

### From Both Projects
1. **Application Information Pattern**
   - Package name detection: `package_name = __name__.split('.', maxsplit=1)[0]`
   - Version and metadata extraction
   - Platform directory management

2. **Distribution Detection Pattern**
   - Development vs production detection
   - Editable installation handling
   - Resource management

3. **Configuration Loading Pattern**
   - TOML parsing with `tomli`
   - Template-based defaults
   - Hierarchical merging

4. **Global State Pattern**
   - Immutable state containers
   - AsyncExitStack for resource management
   - Dependency injection support

5. **Initialization Pattern**
   - Async preparation functions
   - Concurrent component initialization
   - Error handling and resource cleanup

## Testing Strategy

- Ensure package imports correctly
- Verify linters pass: `hatch --env develop run linters`
- Verify tests pass: `hatch --env develop run testers`
- Verify documentation builds: `hatch --env develop run docsgen`

## Implementation Notes

### Import Management
- Expand `__/imports.py` with new aliases
- Keep imports organized and documented
- Avoid namespace pollution

### Type Safety
- Use comprehensive type annotations
- Leverage `dynadoc` for documentation
- Use `TypeAlias` for complex types

### Error Handling
- Extend existing `exceptions.py` hierarchy
- Provide contextual error messages
- Support both sync and async error handling

### Resource Management
- Use `AsyncExitStack` for cleanup
- Support both development and production scenarios
- Handle temporary resource extraction

## Success Criteria

1. **Functional**: All extracted patterns work correctly
2. **Clean**: Linters pass without errors
3. **Tested**: All functionality is tested
4. **Documented**: API documentation generates correctly
5. **Reusable**: Can be consumed by other projects as intended
6. **Maintainable**: Code follows established patterns and conventions

## Implementation Status

- [x] Analysis and planning
- [ ] Dependencies and infrastructure
- [ ] Core modules implementation
- [ ] Configuration system
- [ ] State management
- [ ] Initialization framework
- [ ] Debug support
- [ ] Testing and validation