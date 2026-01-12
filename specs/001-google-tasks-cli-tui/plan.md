# Implementation Plan: Google Tasks CLI and TUI Manager

**Branch**: `001-google-tasks-cli-tui` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-google-tasks-cli-tui/spec.md`

## Summary

Build a Google Tasks management tool with both CLI commands for quick task operations and a Terminal User Interface (TUI) for visual task browsing. The implementation rebuilds the application with clean architecture supporting both interfaces, comprehensive test coverage, and proper separation of concerns. Reuses existing OAuth2 client configuration.

**Scope**: P1 (CLI Task Management) + P2 (Visual TUI Dashboard)
**Deferred**: P3 features (advanced tab navigation, full vim bindings) - will be added in future iterations

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Click 8.0+ (CLI framework)
- Textual 0.47+ (TUI framework)
- google-api-python-client 2.0+ (Google Tasks API)
- google-auth-oauthlib 1.0+ (OAuth2 authentication)
- google-auth-httplib2 0.2+ (HTTP transport for Google APIs)

**Storage**: Local filesystem (OAuth tokens in `~/.config/gtasks-manager/token.json`)
**Testing**:
- pytest (unit and integration tests)
- pytest-asyncio (async TUI testing)
- pytest-mock (mocking Google API calls)
- Coverage target: 90%+ for core modules

**Target Platform**: Linux/macOS/Windows terminals with UTF-8 support
**Project Type**: Single Python package with dual interfaces (CLI + TUI)
**Performance Goals**:
- CLI commands complete in <2 seconds
- TUI launches in <3 seconds
- Support 100+ tasks without performance degradation

**Constraints**:
- No offline mode (requires internet for Google Tasks API)
- Terminal minimum: 80x24 characters
- Python 3.11+ required

**Scale/Scope**:
- Single-user application
- Support up to 10,000 tasks across all lists
- 10-15 CLI commands
- Single TUI interface with multiple views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (No constitution defined - project does not have formal architecture principles)

**Notes**:
- Project has empty constitution template in `.specify/memory/constitution.md`
- No formal architectural constraints to validate against
- Following Python best practices and package standards
- Will establish testing standards as part of this implementation

## Project Structure

### Documentation (this feature)

```text
specs/001-google-tasks-cli-tui/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technical research and decisions
├── data-model.md        # Phase 1: Entity and data structures
├── quickstart.md        # Phase 1: Setup and usage guide
├── contracts/           # Phase 1: API interaction contracts
│   ├── google-tasks-api.md
│   └── tui-events.md
└── checklists/
    └── requirements.md  # Specification validation checklist
```

### Source Code (repository root)

```text
src/gtasks_manager/
├── __init__.py
├── core/                    # Core domain logic (framework-agnostic)
│   ├── __init__.py
│   ├── models.py           # Task, TaskList, Credentials entities
│   ├── services.py         # TaskService (business logic)
│   └── exceptions.py       # Custom exceptions
│
├── adapters/               # External integrations
│   ├── __init__.py
│   ├── google_tasks.py    # Google Tasks API client
│   └── storage.py         # Token and cache storage
│
├── cli/                    # Click CLI interface
│   ├── __init__.py
│   ├── main.py            # CLI entry point and command group
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── auth.py        # auth, logout commands
│   │   ├── tasks.py       # create, list, update, delete, complete
│   │   └── lists.py       # list management commands
│   └── formatters.py      # Output formatting utilities
│
├── tui/                    # Textual TUI interface
│   ├── __init__.py
│   ├── app.py             # Main TUI application
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── task_list.py   # Main task list view
│   │   └── help.py        # Help screen
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── task_item.py   # Individual task display
│   │   └── status_bar.py  # Status/info bar
│   └── keybindings.py     # Keyboard shortcut definitions
│
└── config.py              # Configuration (reuse CLIENT_CONFIG from existing)

tests/
├── __init__.py
├── conftest.py            # Shared pytest fixtures
│
├── unit/                  # Unit tests (isolated, fast)
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_cli_formatters.py
│   └── test_tui_widgets.py
│
├── integration/           # Integration tests (external APIs)
│   ├── __init__.py
│   ├── test_google_tasks_adapter.py
│   ├── test_storage_adapter.py
│   └── test_cli_commands.py
│
└── e2e/                   # End-to-end tests
    ├── __init__.py
    ├── test_cli_workflows.py
    └── test_tui_app.py

# Configuration files
pyproject.toml             # Updated with new dependencies
pytest.ini                 # Pytest configuration
.coveragerc               # Coverage configuration
```

**Structure Decision**:

Selected **Single project** structure with **Hexagonal Architecture** (Ports & Adapters):

- **Core**: Domain models and business logic (independent of frameworks)
- **Adapters**: External integrations (Google API, storage)
- **Interfaces**: CLI and TUI as separate interface layers
- **Tests**: Mirror source structure with unit/integration/e2e separation

This structure supports:
1. **Dual interfaces** (CLI + TUI) sharing the same core logic
2. **Testability** - core can be tested without Google API or UI frameworks
3. **Future extensibility** - easy to add web interface or mobile app later
4. **Clear boundaries** - each layer has specific responsibilities

## Complexity Tracking

> **No violations** - Project follows standard Python package structure with clean architecture principles. No constitution rules to justify violations against.

---

# Phase 0: Outline & Research

## Research Questions

Based on Technical Context, the following areas need research and decision-making:

### 1. Textual Framework Best Practices

**Question**: What are the recommended patterns for building production-ready Textual applications?

**Research areas**:
- Application lifecycle and async event handling
- Screen and widget composition patterns
- State management in Textual apps
- Testing strategies for Textual UIs
- Error handling and recovery patterns

### 2. Google Tasks API Integration

**Question**: What are the best practices for robust Google Tasks API integration?

**Research areas**:
- OAuth2 token management and refresh strategies
- API rate limiting and retry logic
- Offline behavior and error handling
- Batch operations vs individual API calls
- Minimal required scopes for task management

### 3. Testing Strategy for Dual-Interface Application

**Question**: How to achieve 90%+ coverage for both CLI and TUI interfaces?

**Research areas**:
- Pytest best practices for Click applications
- Async testing patterns for Textual
- Mocking Google API responses effectively
- Integration test strategies without hitting real API
- Test data fixtures and factories

### 4. CLI and TUI Coordination

**Question**: How should CLI and TUI share code while maintaining independence?

**Research areas**:
- Service layer patterns for shared business logic
- Data model serialization between layers
- Cache invalidation strategies
- Configuration sharing
- Error propagation from core to interfaces

---

# Phase 1: Design & Contracts

*Prerequisites: Phase 0 research complete*

## Data Models

Will be detailed in `data-model.md`:

**Core Entities**:
1. **Task** - Todo item with title, notes, due date, status
2. **TaskList** - Collection of tasks with name and ID
3. **Credentials** - OAuth2 tokens for API access

**Value Objects**:
1. **TaskStatus** - Enum (needsAction, completed)
2. **DateValue** - Date handling for due dates
3. **TaskReference** - Union type (task ID or index number)

## API Contracts

Will be documented in `contracts/` directory:

### 1. Google Tasks API Contract (`google-tasks-api.md`)

**Operations**:
- `authenticate()` - OAuth2 flow
- `refresh_token()` - Token refresh
- `list_task_lists()` - Get all lists
- `list_tasks(list_id, show_completed)` - Get tasks from list
- `create_task(list_id, task_data)` - Create new task
- `update_task(list_id, task_id, updates)` - Update task
- `delete_task(list_id, task_id)` - Delete task

**Error Handling**:
- Network failures
- Authentication errors
- Rate limiting
- Invalid data

### 2. TUI Events Contract (`tui-events.md`)

**Events**:
- `TaskSelected` - User selects a task
- `TaskAction` - User triggers action (complete, delete)
- `RefreshRequested` - User requests data refresh
- `QuitRequested` - User wants to exit

**State Updates**:
- Task list changes
- Loading states
- Error states

## Testing Strategy

Detailed in Phase 0 research, summary:

**Unit Tests** (60-70% of tests):
- All core models and services
- CLI formatters
- TUI widgets (isolated)
- Mocked external dependencies

**Integration Tests** (20-30% of tests):
- Google Tasks adapter with API responses
- Storage adapter with filesystem
- CLI commands end-to-end
- OAuth flow

**E2E Tests** (10% of tests):
- Complete CLI workflows
- TUI application flows
- Error scenarios

**Coverage Goals**:
- Core modules: 95%+
- Adapters: 90%+
- CLI/TUI: 85%+
- Overall: 90%+

---

# Phase 2: Implementation Milestones

*Note: Detailed tasks will be in `tasks.md` (created by `/speckit.tasks` command)*

## Milestone 1: Core Domain & Google API Integration

**Goal**: Implement core business logic and Google Tasks API adapter

**Deliverables**:
1. Core models (Task, TaskList, Credentials)
2. TaskService with all business operations
3. Google Tasks API adapter
4. Storage adapter for tokens
5. Unit tests for core (95%+ coverage)
6. Integration tests for adapters

**Success Criteria**:
- Can authenticate with Google Tasks
- Can perform all CRUD operations on tasks
- All core tests passing
- No framework dependencies in core layer

## Milestone 2: CLI Interface

**Goal**: Build complete CLI with all P1 commands

**Deliverables**:
1. Click command structure
2. All commands: auth, logout, create, list, update, delete, complete, lists
3. Output formatters (human-readable + JSON)
4. Error handling and user feedback
5. CLI integration tests

**Success Criteria**:
- All P1 acceptance scenarios passing
- CLI commands execute in <2 seconds
- Clear error messages for all failure cases
- Help documentation complete

## Milestone 3: TUI Interface

**Goal**: Build visual TUI interface with task viewing

**Deliverables**:
1. Textual application structure
2. Task list view screen
3. Task display widgets
4. Status bar
5. Basic keyboard navigation
6. Help screen
7. TUI tests

**Success Criteria**:
- All P2 acceptance scenarios passing
- TUI launches in <3 seconds
- Supports 80x24 terminal
- Handles 100+ tasks smoothly
- Basic keyboard shortcuts work (arrow keys, enter, q)

## Milestone 4: Testing & Documentation

**Goal**: Complete test coverage and user documentation

**Deliverables**:
1. Achieve 90%+ test coverage
2. E2E test suite
3. Quickstart guide
4. API documentation
5. Troubleshooting guide
6. Performance benchmarks

**Success Criteria**:
- Coverage reports show 90%+
- All success criteria from spec verified
- Documentation reviewed and complete
- Known issues documented

---

# Implementation Notes

## Reused Components

From existing codebase (`src/gtasks_manager/`):

1. **config.py** - Reuse entirely:
   - `CLIENT_CONFIG` with OAuth2 client setup
   - `SCOPES` configuration
   - `CONFIG_DIR`, `TOKEN_FILE` paths
   - `ensure_config_dir()` function

2. **Patterns to reference** (but rewrite with new architecture):
   - OAuth2 flow pattern from `auth.py`
   - Task formatting logic from `cli.py`
   - Cache concept from `task_cache.py`
   - API interaction patterns from `tasks.py`

## Key Architectural Decisions

### 1. Hexagonal Architecture

**Why**: Separate core business logic from external dependencies (Google API, CLI, TUI)

**Benefits**:
- Core logic testable without external services
- Easy to add new interfaces (web, mobile) later
- Clear separation of concerns
- Dependencies point inward (core has no external deps)

### 2. Dual Interface Strategy

**CLI**: Fast, scriptable, composable with other tools
**TUI**: Visual, interactive, better for browsing

**Shared**: Both use same `TaskService` from core layer

### 3. Testing Philosophy

**Test Pyramid**:
- Many fast unit tests (core logic)
- Moderate integration tests (adapters)
- Few slow E2E tests (full flows)

**Mocking Strategy**:
- Mock Google API in unit tests
- Use recorded responses in integration tests
- Real API in manual testing only

### 4. Error Handling

**Layers**:
1. Core: Raises domain exceptions
2. Adapters: Translate external errors to domain exceptions
3. Interfaces: Catch exceptions, show user-friendly messages

**Network Issues**:
- Detect and report clearly
- Suggest troubleshooting steps
- No silent failures

## Deferred to Future Iterations

The following P3 features are **out of scope** for this implementation:

1. **Advanced Tab Navigation** (P3 - User Story 3)
   - Tab switching with keyboard shortcuts
   - Multiple list views simultaneously
   - Will be added after basic TUI is stable

2. **Full Vim Bindings** (P3 - User Story 4)
   - Complete vim-style navigation (hjkl, gg, G, etc.)
   - Vim-like command mode
   - Will be added incrementally based on user feedback

**Why deferred**:
- P1+P2 provides complete functional value
- TUI foundation must be solid before advanced navigation
- Can gather user feedback on basic TUI first

**Basic keyboard support included**:
- Arrow keys for navigation
- Enter to select
- Space to toggle completion
- q to quit
- ? for help

---

# Next Steps

1. **Run Phase 0**: Execute research on the 4 research questions above
2. **Generate `research.md`**: Document decisions and rationales
3. **Run Phase 1**: Create detailed data models and contracts
4. **Update agent context**: Add Textual framework to AGENTS.md
5. **Generate `tasks.md`**: Break down milestones into actionable tasks (via `/speckit.tasks`)

---

**Plan Status**: Ready for Phase 0 Research
**Estimated Implementation Time**: 3-4 weeks for P1+P2 scope with comprehensive tests
**Next Command**: Continue with research phase automatically
