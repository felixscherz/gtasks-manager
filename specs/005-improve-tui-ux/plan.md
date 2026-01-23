# Implementation Plan: Improve TUI UX

**Branch**: `[005-improve-tui-ux]` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-improve-tui-ux/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature improves the TUI UX by (1) making `gtasks` launch the TUI by default when no subcommand is provided, (2) maintaining backward compatibility with `gtasks gui`, (3) preserving task selection when toggling task state, and (4) displaying the current task list name in the header. The implementation will modify the CLI command structure to detect empty invocations, enhance the TUI state management to track selection across updates, and fetch task list metadata for display in the header.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click 8.0+, Textual 0.47+, Google API Python Client 2.0+
**Storage**: Google Tasks API (external), local JSON cache for task metadata
**Testing**: pytest 7.4.0+, pytest-asyncio 0.21.0+
**Target Platform**: CLI/TUI application (terminal-based, cross-platform Linux/macOS/Windows)
**Project Type**: Single project (CLI + TUI in one package)
**Performance Goals**: Responsive TUI (non-blocking UI), <200ms for API operations, immediate task selection preservation
**Constraints**: Must work offline with cached data, graceful error handling for API failures, terminal width compatibility (80+ chars)
**Scale/Scope**: Small to medium codebase, individual user workloads, single task list focus

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Check

**Quality Gate 1: Design & Test Strategy**
- ✅ No implementation code yet (specification only)
- ✅ Data models and test strategy will be defined in Phase 1 before implementation

**Quality Gate 2: CI/CD Compliance**
- ✅ Will use `ruff` for linting
- ✅ Will use `mypy` for type checking
- ✅ Will use `pytest` for testing (including pytest-asyncio for TUI)
- ✅ All PRs will pass CI checks before merging

**Quality Gate 3: Security**
- ✅ Will not commit secrets or tokens
- ✅ Token files already in `.gitignore`
- ✅ Will maintain proper file permissions (600) for local authentication tokens

**Core Principles Compliance**
- ✅ Python 3.11+ with strict type hinting will be used
- ✅ Hexagonal Architecture will be followed (core domain isolated from adapters/CLI/TUI)
- ✅ `uv` will be used for dependency management
- ✅ TDD approach will be followed (tests before implementation)
- ✅ Textual framework patterns will be used (reactive attributes, @work decorator)
- ✅ Atomic commits will be made after each discrete task

### Post-Phase 1 Check (to be completed after design)
- [x] Data models approved and documented in data-model.md
- [x] Test strategy documented in contracts (TUI application and CLI entry point)
- [x] No implementation details leaked into specification

**Status**: ✅ PASSED - Ready for Phase 2 (task breakdown)

**Design Artifacts Generated**:
- ✅ research.md - All technical questions resolved
- ✅ data-model.md - Core entities and data structures defined
- ✅ contracts/ - Interface contracts for TUI and CLI components
- ✅ quickstart.md - Developer getting started guide
- ✅ Agent context updated with new technologies

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── gtasks_manager/
    ├── __init__.py          # Package metadata
    ├── cli.py               # Click CLI commands and entry point (MODIFIED)
    ├── auth.py              # OAuth2 authentication
    ├── tasks.py             # TasksManager class (API interactions)
    ├── config.py            # Configuration constants and paths
    ├── task_cache.py        # TaskCache class (local task indexing)
    └── tui/                 # TUI application (NEW for feature)
        ├── __init__.py
        ├── app.py           # Main TUI application class (NEW)
        ├── widgets.py       # Custom TUI widgets (NEW)
        └── state.py         # TUI state management (NEW)

tests/
├── unit/
│   ├── test_cli.py          # CLI command tests (MODIFIED)
│   ├── test_tui.py          # TUI component tests (NEW)
│   └── test_state.py        # TUI state management tests (NEW)
└── integration/
    └── test_tui_flow.py     # TUI integration tests (NEW)
```

**Structure Decision**: Single project structure following existing gtasks-manager layout. The TUI components are organized in a dedicated `tui/` subpackage to maintain clear separation from CLI and core domain logic, adhering to Hexagonal Architecture principles.
