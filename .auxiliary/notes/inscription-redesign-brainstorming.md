# Inscription Redesign Brainstorming

## Overview

This document captures the brainstorming session for redesigning the `appcore.inscription` module to support a cleaner, more focused approach that provides a migration path toward `icecream-truck` while maintaining practical functionality today.

## Key Insights

### 1. Application-Centric Focus
- `appcore` is application core, not library core
- Should focus on application needs, not library integration patterns
- Remove library-focused modes (Null, Pass) in favor of application-focused modes

### 2. Logging vs Introspection Separation (Temporary)
- **Current state**: `logging` handles message logging, `icecream-truck` handles introspection
- **Future state**: `icecream-truck` will handle both logging and introspection
- **Pragmatic approach**: Focus on logging configuration now, prepare for future unification

### 3. Unified Configuration Vision
- Long-term goal: Replace `logging` with `ictruck` entirely
- Unified configuration ensures consistency of output targets
- Clean migration path as `icecream-truck` gains logging capabilities

## Redesigned Interface

### Control Object
```python
@dataclass(frozen=True)
class Control:
    mode: Literal['null', 'plain', 'rich'] = 'plain'
    level: str = 'info' 
    target: Optional[Union[Path, TextIO]] = None  # Default to stderr
```

### Mode Definitions

#### 1. **Null Mode**
- No logging configuration beyond setting root logger output handler
- Minimal intervention in application logging setup
- Use case: Applications that want full control over logging

#### 2. **Plain Mode** 
- Standard Python logging configuration
- Honors optional `level` argument (defaults to `logging.INFO`)
- Use case: Traditional logging needs, production applications

#### 3. **Rich Mode**
- Attempts to setup Rich logging for enhanced formatting
- Gracefully degrades to Plain mode if `rich` cannot be imported
- Use case: Development, enhanced logging experience

### Target Parameter
- Optional file path or stream for output routing
- Defaults to stderr if not specified
- Ensures consistent output targeting between logging and future introspection

## Implementation Strategy

### Phase 1: Current Implementation (Logging-Focused)
```python
def _configure_null_mode():
    # Minimal root logger handler setup
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler())

def _configure_plain_mode(level: str, target: Optional[Union[Path, TextIO]]):
    # Standard logging configuration
    handler = _create_handler(target)
    handler.setLevel(getattr(logging, level.upper()))
    # Configure formatter, etc.

def _configure_rich_mode(level: str, target: Optional[Union[Path, TextIO]]):
    try:
        from rich.logging import RichHandler
        from rich.console import Console
        # Setup rich logging
    except ImportError:
        # Gracefully degrade to plain mode
        _configure_plain_mode(level, target)
```

### Phase 2: Future Migration (icecream-truck Integration)
When `icecream-truck` gains logging capabilities:
```python
# Current approach - separate configurations
inscription = appcore.inscription.Control(mode='null')  # No logging setup
ictruck.recipes.sundae.configure(trace_levels=3)

# Future approach - unified through icecream-truck
inscription = appcore.inscription.Control(mode='rich', level='debug')
# Internally routes to: ictruck.recipes.logging_sundae.configure(level='debug', target=sys.stderr)
```

## Usage Patterns

### Simple Applications
```python
# Basic logging
inscription = appcore.inscription.Control(mode='plain', level='info')
globals_dto = await appcore.prepare(exits, inscription=inscription)
```

### Development Applications  
```python
# Rich logging + separate icecream debugging
inscription = appcore.inscription.Control(mode='rich', level='debug')
globals_dto = await appcore.prepare(exits, inscription=inscription)

# Separately configure icecream-truck for introspection
import ictruck.recipes.sundae
ictruck.recipes.sundae.configure(trace_levels=5)
```

### Production Applications
```python
# Structured logging to file
inscription = appcore.inscription.Control(
    mode='plain', 
    level='info', 
    target=Path('/var/log/myapp.log')
)
globals_dto = await appcore.prepare(exits, inscription=inscription)
```

## Benefits of This Approach

### 1. **Pragmatic Migration Path**
- Works today with standard logging
- Clear upgrade path as `icecream-truck` evolves
- No breaking changes when future unification occurs

### 2. **Simple Mental Model**
- Three modes cover common use cases
- Clear documentation: "This configures Python logging"
- No confusion about logging vs introspection

### 3. **Future-Proof Design**
- Interface remains stable as backend changes
- Unified configuration philosophy maintained
- Clean separation until unification is ready

### 4. **Minimal Complexity**
- No shadow implementations
- No artificial unification of different paradigms
- Each system focused on its core competency

## Integration with icecream-truck

### Current Complementary Usage
```python
# appcore handles logging
inscription = appcore.inscription.Control(mode='rich', level='debug')
globals_dto = await appcore.prepare(exits, inscription=inscription)

# icecream-truck handles introspection (configured separately)
import ictruck.recipes.sundae
ictruck.recipes.sundae.configure(trace_levels=3)
```

### Future Unified Usage
```python
# Single configuration point for both logging and introspection
inscription = appcore.inscription.Control(mode='rich', level='debug')
globals_dto = await appcore.prepare(exits, inscription=inscription)
# Internally configures icecream-truck recipes for both logging and introspection
```

## Rich Dependency Strategy

### Graceful Degradation
- Rich is optional dependency
- Rich mode attempts to import and use `rich.logging.RichHandler`
- Falls back to Plain mode if Rich unavailable
- Clear error messaging guides users to install Rich if desired

### Installation Options
```bash
# Lightweight installation
pip install appcore

# Full featured installation  
pip install appcore[rich]
```

## Implementation Tasks

1. **Update inscription module**
   - Replace current modes with new three-mode system
   - Implement graceful Rich degradation
   - Add target parameter support

2. **Update preparation integration**
   - Modify `prepare()` function to use new Control interface
   - Ensure proper handler configuration

3. **Write comprehensive tests**
   - Test all three modes
   - Test Rich availability/unavailability scenarios
   - Test target parameter functionality

4. **Update documentation**
   - Clear examples for each mode
   - Migration guide from current interface
   - Future roadmap explanation

## Decision Rationale

This approach was chosen because:
- **Recognizes current limitations**: `icecream-truck` doesn't have logging yet
- **Provides clear value today**: Enhanced logging with optional Rich formatting
- **Maintains future vision**: Unified configuration through single interface
- **Avoids complexity**: No artificial unification of disparate systems
- **Supports applications**: Focused on application needs, not library integration

The key insight is that this is a pragmatic stepping stone that provides immediate value while positioning for future unification when `icecream-truck` gains logging capabilities.