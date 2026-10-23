## 1. Inscription Module

- [x] 1.1 Add `_prepare_scribes_ictr()` function to configure and install ictr dispatcher
- [x] 1.2 Add `_derive_ictr_flavors()` function to map inscription level to flavor set
- [x] 1.3 Add `_produce_ictr_generalcfg()` function with custom printer factory for ANSI stripping in Plain/Null modes
- [x] 1.4 Add `install_ictr` field to `Control` dataclass (default `True`)
- [x] 1.5 Update `prepare()` to call `_prepare_scribes_ictr()` after logging setup

## 2. CLI Integration

- [x] 2.1 Add `trace_levels` option to `InscriptionControl` in `cli/core.py`
- [x] 2.2 Add `active_flavors` option to `InscriptionControl` in `cli/core.py`
- [x] 2.3 Update `InscriptionControl.as_control()` to pass ictr fields to `inscription.Control`

## 3. Environment Variables

- [x] 3.1 Support `{APP}_ACTIVE_FLAVORS` environment variable for flavor control
- [x] 3.2 Support `{APP}_TRACE_LEVELS` environment variable for trace depth
- [x] 3.3 Document precedence: explicit Control args > app-specific env > ictr env > defaults

## 4. Testing

- [x] 4.1 Add tests for `_prepare_scribes_ictr()` dispatcher installation
- [x] 4.2 Add tests for `_derive_ictr_flavors()` level-to-flavor mapping
- [x] 4.3 Add tests for CLI option passthrough
- [x] 4.4 Add tests for environment variable overrides and precedence
- [x] 4.5 Add tests for `install_ictr=False` (dispatcher not installed)
