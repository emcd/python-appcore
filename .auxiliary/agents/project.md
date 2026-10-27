# Project Guidance

Project-owned knowledge the generated `AGENTS.md` entrypoint must not own.
Structured tracking stays in `nb`.

## Purpose

Appcore is a Python library providing application foundation components:
streamlined async initialization, configuration management, platform directories,
logging setup, and environment handling for Python applications.

## Tech Stack

- **Language**: Python 3.12+ (CPython)
- **Build**: Hatch (hatchling backend)
- **Linting**: Ruff, Pyright, isort, vulture
- **Testing**: pytest, pytest-asyncio, pytest-mock, pyfakefs, coverage
- **Documentation**: Sphinx (Furo theme, MyST parser)
- **Key dependencies**: platformdirs, aiofiles, tomllib (stdlib), python-dotenv, ictr, absence, dynadoc, frigid

## Notes

<!-- Accumulate project-specific knowledge, constraints, deviations, and durable
     links here. For structured items, use `nb`.

     Migration: if upgrading from an AGENTS.md that still had inline Purpose,
     Tech Stack, or Project Notes sections, move that body here once, then accept
     the template-owned AGENTS.md pointer.

     TODO: If this project uses multiple agent/clone roles, create a stable
     team-organization note in `nb`, modeled after one of the examples at:
     https://raw.githubusercontent.com/emcd/agents-common/master/examples/nb-notes/team-organization/README.md
     Then link the note here, for example:
     - Team org, role ownership, signoff policy, and merge workflow: `coordination/general/<n>` -->

## nb Component Folders

- `engine` — core preparation, state, application foundation
- `configuration` — TOML acquirer, dictedits, environment
- `cli` — command framework, display options, rendering
- `inscription` — logging, ictr integration, diagnostic output
- `exceptions` — exception hierarchy, rendering methods
- `tests` — test suite organization and coverage
