# Change: Add ictr as First-Class Inscription System

## Why

The `Control` dataclass already carries `active_flavors`, `ictr_alias`, and
`trace_levels` fields, but `prepare()` only initializes Python `logging`.
The `ictr` dispatcher is never configured or installed, so application code
that calls `ic()` or uses ictr flavors gets no output. CLI also lacks
ictr-specific options.

## What Changes

- Add `_prepare_scribes_ictr()` to `inscription.py` that configures and
  installs the ictr dispatcher alongside logging.
- Add `_derive_ictr_flavors()` to map inscription levels to ictr flavor sets.
- Add `_produce_ictr_generalcfg()` for colorization control via compositor
  configuration.
- Update `prepare()` to call both `_prepare_scribes_logging()` and
  `_prepare_scribes_ictr()`.
- Add `trace_levels` and `active_flavors` CLI options to `InscriptionControl`
  in `cli/core.py`.
- Update `InscriptionControl.as_control()` to pass ictr fields through.

## Impact

- Affected specs: `inscription`
- Affected code: `sources/appcore/inscription.py`, `sources/appcore/cli/core.py`
