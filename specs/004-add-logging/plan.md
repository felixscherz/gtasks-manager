# Implementation Plan: Add Application Logging

**Branch**: `004-add-logging` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-add-logging/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a comprehensive logging system to the gtasks-manager CLI application using Python's built-in `logging` module with `RotatingFileHandler`. The system automatically writes application events, warnings, and errors to OS-specific log files (`~/.config/gtasks-manager/logs/gtasks.log` on macOS/Linux, `%APPDATA%\gtasks-manager\logs\gtasks.log` on Windows). Supports configurable verbosity levels via -v flag (WARNING/ERROR by default, INFO with -v, DEBUG with -vv), includes timestamps and stack traces for errors, handles concurrent writes via OS file locking, implements log rotation at 10MB with 5 backup files, and documents log file locations in help text.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Python logging module (stdlib), Click 8.0+ (existing CLI framework)
**Storage**: File system (log files)
**Testing**: pytest, pytest-asyncio
**Target Platform**: macOS, Linux, Windows
**Project Type**: single (CLI application)
**Performance Goals**: Log file creation within 100ms of first command execution
**Constraints**: Maximum log file size 10MB with automatic rotation, handle concurrent writes without corruption
**Scale/Scope**: Individual user instances, multiple concurrent processes per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Python Best Practices & Architecture
- ✓ Python 3.11+ with strict type hinting
- ✓ Follow Hexagonal Architecture (Ports & Adapters)
- ✓ Use ruff for linting and formatting
- ✓ Favor composition over inheritance

### Unified Dependency Management (uv)
- ✓ Use uv for dependency management
- ✓ Run development commands via uv run
- ✓ Update and commit uv.lock

### Test-First Development (TDD)
- ✓ Produce test strategy before implementation
- ✓ Write failing tests before implementation (red-green-refactor)
- ✓ Verify logic via pytest
- ✓ Maintain 90%+ code coverage for core and adapters

### Textual TUI Standards
- ✓ Use Textual framework for TUI
- ✓ Use reactive attributes for auto-updating UI
- ✓ Offload I/O to background workers with @work decorator
- ✓ Follow Textual message-passing patterns

### Atomic Commits & Verification
- ✓ Run tests and linters before committing
- ✓ Create meaningful git commits
- ✓ Include clear description in commit message

### Quality Gates
- ✓ Quality Gate 1: Design & Test Strategy - Will create test strategy before implementation
- ✓ Quality Gate 2: CI/CD Compliance - Will ensure ruff, mypy, and pytest pass
- ✓ Quality Gate 3: Security - Will not commit secrets, will use appropriate permissions

### Violations Found
None - All constitution requirements are compatible with this feature.

### Post-Design Re-Check
After completing Phase 1 design, all constitution requirements remain compatible:
- No new external dependencies required (Python logging module is stdlib)
- Architecture follows Hexagonal pattern (logging_config.py is core, CLI integration is adapter)
- Test strategy defined before implementation
- All quality gates will be met

## Project Structure

### Documentation (this feature)

```text
specs/004-add-logging/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command) - COMPLETED
├── data-model.md        # Phase 1 output (/speckit.plan command) - COMPLETED
├── quickstart.md        # Phase 1 output (/speckit.plan command) - COMPLETED
├── contracts/           # Phase 1 output (/speckit.plan command) - COMPLETED
│   └── README.md        # No external contracts needed for this feature
├── checklists/
│   └── requirements.md   # Spec quality checklist (from /speckit.specify)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── gtasks_manager/
│   ├── __init__.py
│   ├── cli.py              # Add -v flag option
│   ├── config.py           # Add log file path constants
│   └── logging_config.py   # NEW: Logging setup and configuration
│
tests/
├── unit/
│   └── test_logging_config.py  # NEW: Unit tests for logging
└── integration/
    └── test_logging_integration.py  # NEW: Integration tests for logging
```

**Structure Decision**: Single project structure selected as this is a CLI application. New logging configuration module will be added to existing src/gtasks_manager/ directory. Tests will follow existing structure in tests/ with unit and integration separation. Logging configuration will integrate with existing CLI via -v flag.
