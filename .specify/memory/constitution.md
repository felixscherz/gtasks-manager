# gtasks-manager Constitution

## Core Principles

### I. Python Best Practices & Architecture
- **MUST** use Python 3.11+ with strict type hinting for all function signatures and complex data structures.
- **MUST** follow Hexagonal Architecture (Ports & Adapters). Core domain logic in `src/gtasks_manager/core/` MUST NOT import from `adapters`, `cli`, or `tui`.
- **MUST** use `ruff` for linting and formatting to ensure PEP 8 compliance.
- **SHOULD** favor composition over inheritance in class design.

### II. Unified Dependency Management (uv)
- **MUST** use `uv` as the exclusive tool for dependency management and virtual environment handling.
- **MUST** run all development commands (tests, lint, start) via `uv run`.
- **MUST** ensure the `uv.lock` file is updated and committed with any dependency changes.

### III. Test-First Development (TDD)
- **MUST** produce a test strategy or checklist before starting any implementation task.
- **MUST** write failing tests (red) before writing the corresponding implementation code (green).
- **MUST** verify all logic via `pytest`. Async logic (TUI/API) MUST use `pytest-asyncio`.
- **SHOULD** maintain 90%+ code coverage for the `core` and `adapters` packages.

### IV. Textual TUI Standards
- **MUST** use the `Textual` framework for the TUI interface.
- **MUST** use `reactive` attributes for auto-updating UI states.
- **MUST** offload all I/O and API calls to background workers using the `@work` decorator to prevent UI hangs.
- **SHOULD** follow Textual's message-passing patterns for inter-widget communication.

## Development Quality Gates

### Quality Gate 1: Design & Test Strategy
- No implementation code may be written until the corresponding data models and test strategy are approved.

### Quality Gate 2: CI/CD Compliance
- Every PR **MUST** pass linting (`ruff`), type checking (`mypy`), and the full test suite (`pytest`) in the CI environment.

### Quality Gate 3: Security
- **MUST NOT** commit secrets or user tokens. `token.json` and `credentials.json` MUST be in `.gitignore`.
- **MUST** use appropriate file permissions (600) when storing local authentication tokens.

## Governance
- This constitution supersedes all other project documentation.
- Any deviation from these principles must be documented as a "Technical Exception" with a clear rationale and sunset date.

**Version**: 1.0.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-08
