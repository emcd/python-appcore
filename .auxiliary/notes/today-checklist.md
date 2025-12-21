# Today's Implementation Checklist

**Goal**: Complete ictr integration in appcore
**Date**: 2025-12-20

## ✅ Completed

- [x] Add `ictr` dependency to pyproject.toml
- [x] Add `ictr` import to `__/imports.py`
- [x] Extend `Control` with ictr fields (using `Absential` and ictr type aliases)
- [x] Add CLI parsing for `active_flavors` and `trace_levels` with `UseAppendAction`
- [x] Update Tyro to 1.0.2
- [x] Refactor CLI doc annotations (`__.ddoc.Doc` + `__.tyro.conf.arg`)
- [x] Add `_parse_active_flavors()` and `_parse_trace_levels()` helpers
- [x] Update `InscriptionControl.as_control()` to use parsing helpers
- [x] Add `colorize` parameter to `ictr.produce_printer_factory_default()`
- [x] Complete `_prepare_scribes_ictr()` implementation
- [x] Call `_prepare_scribes_ictr()` from `prepare()`
- [x] Fix DisplayOptions/Globals type issues
  - Removed `provide_stream()` and `determine_colorization()`
  - Now uses `provide_printer()` returning `ictr.standard.Printer`
- [x] **Implement presentation selection system**
  - Created `presentations_registry` in `cli/core.py`
  - Added `presentation: str` field to `DisplayOptions`
  - Added `clioptions_json: ictrstd.JsonPresentation` to `Application`
  - Implemented `render_and_print()` with registry lookup and rendering
  - Updated `intercept_errors()` to render exceptions
- [x] **Update introspection commands**
  - Added per-command result dataclasses (ConfigurationResult, DirectoriesResult, EnvironmentResult)
  - Commands now return renderable results instead of calling auxdata.display.render()
  - Application.execute() calls render_and_print() with command results

## 🎯 Remaining Work (Priority 1)

### Testing & Bug Fixes

- [x] **Create Tyro bug reproducer and submit report** - DONE!
  - Created minimal reproducer with `frozen=True` dataclass and `init=False` field
  - Submitted issue #415 to Tyro project
  - Bug blocks `hatch run appcore configuration` from running
- [ ] **Wait for Tyro fix or submit PR** - BLOCKED
  - Issue in line 163 of `_struct_spec_dataclass.py`
  - Proposed fix: use `object.__setattr__()` instead of `setattr()`

## 📝 Documentation & Testing (Priority 2)

- [ ] **Test ictr installation**
  - Create simple CLI app that uses ictr
  - Verify `--active-flavor note` works
  - Verify `--trace-level 0` works
  - Verify `--active-flavor mylib:debug` works (per-address)

- [ ] **Update appcore introspection CLI**
  - Use new ictr system for debug output
  - Test colorization modes

## 🎨 Display Integration (Priority 3 - Optional)

- [ ] **Remove DisplayOptions from Globals** (if time permits)
  - Keep in Application only
  - Add progress_reporter callback to Globals
  - Update existing commands to use callback instead of display options

## 🚫 Out of Scope for Today

- Rich presentation integration (future)
- TOML rendering (not in ictr yet)
- Custom introducer configurations
- Per-library flavor registration patterns
- DisplayOptions removal from Globals

---

## Summary

Core ictr integration is **complete**! All major components implemented:
- ✅ ictr scribes preparation with dispatcher configuration
- ✅ CLI parsing for active_flavors and trace_levels
- ✅ Presentation selection system with extensible registry
- ✅ render_and_print() with full presentation support
- ✅ Introspection commands using renderable result dataclasses

**Current blocker**: Tyro bug with frozen/immutable dataclasses prevents `appcore configuration` from running.
Next step: Create minimal reproducer and submit bug report.
