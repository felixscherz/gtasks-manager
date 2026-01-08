# Tasks: Google Tasks CLI and TUI Manager

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure required by all phases

- [X] T001 Initialize Python project and ensure `pyproject.toml` includes required dependencies: `click`, `textual`, `google-api-python-client`, `google-auth-oauthlib`, `pydantic`, `pytest`, `pytest-asyncio` (file: `pyproject.toml`)
- [X] T002 [P] Create package directories per plan: `src/gtasks_manager/core`, `src/gtasks_manager/adapters`, `src/gtasks_manager/cli`, `src/gtasks_manager/tui` (create `__init__.py` files) (paths: `src/gtasks_manager/`)
- [X] T003 [P] Reuse existing `src/gtasks_manager/config.py` and verify `CLIENT_CONFIG`, `SCOPES`, `CONFIG_DIR`, `TOKEN_FILE`, and `ensure_config_dir()` are present and importable (file: `src/gtasks_manager/config.py`)
- [X] T004 [P] Add pytest configuration and basic `tests/conftest.py` with fixtures for `event_loop`, `tmp_path`, and a `mock_api` fixture (file: `pytest.ini`, `tests/conftest.py`)
- [X] T005 [P] Add basic CI config placeholder (e.g., `.github/workflows/python.yml`) with job to run `pytest` (file: `.github/workflows/python.yml`)
- [X] T006 [P] Configure project formatting tools (recommended: `ruff`/`black`) and add minimal config files (`pyproject.toml` entries or config files) (file: `pyproject.toml`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story implementation

- [ ] T007 Implement core domain models in `src/gtasks_manager/core/models.py`: `Task`, `TaskList`, `UserCredentials`, `TaskStatus`, `TaskReference` (file: `src/gtasks_manager/core/models.py`)
- [ ] T008 Implement `TaskCache` in `src/gtasks_manager/core/task_cache.py` per data-model.md with index→ID mapping and `get_task_id()`/`update()` methods (file: `src/gtasks_manager/core/task_cache.py`)
- [ ] T009 Implement domain exceptions in `src/gtasks_manager/core/exceptions.py` (`APIError`, `AuthenticationError`, `NotFoundError`, `ValidationError`, `RateLimitError`, `NetworkError`) (file: `src/gtasks_manager/core/exceptions.py`)
- [ ] T010 [P] Implement `TasksAPIProtocol` interface in `src/gtasks_manager/core/ports.py` matching `google-tasks-api.md` adapter protocol (file: `src/gtasks_manager/core/ports.py`)
- [ ] T011 Implement `TaskService` in `src/gtasks_manager/core/services.py` that depends only on `TasksAPIProtocol` and `TaskCache` and exposes business operations: `list_tasks`, `get_task`, `create_task`, `update_task`, `delete_task`, `complete_task` (file: `src/gtasks_manager/core/services.py`)
- [ ] T012 [P] Implement adapters: Google Tasks adapter skeleton in `src/gtasks_manager/adapters/google_tasks.py` that implements `TasksAPIProtocol` and uses `src/gtasks_manager/config.py` for `CLIENT_CONFIG` and token storage (file: `src/gtasks_manager/adapters/google_tasks.py`)
- [ ] T013 Implement storage adapter for token and cache in `src/gtasks_manager/adapters/storage.py` using `pathlib.Path` and `ensure_config_dir()` (file: `src/gtasks_manager/adapters/storage.py`)
- [ ] T014 Implement DTOs (Pydantic) for Google API in `src/gtasks_manager/adapters/dtos.py` (`GoogleTaskDTO`, `GoogleTaskListDTO`) as per `data-model.md` (file: `src/gtasks_manager/adapters/dtos.py`)
- [ ] T015 Implement pagination and retry helper utilities in `src/gtasks_manager/adapters/utils.py` (file: `src/gtasks_manager/adapters/utils.py`)
- [ ] T016 Implement unit tests for core models and TaskCache in `tests/unit/test_models.py` and `tests/unit/test_task_cache.py` (file: `tests/unit/test_models.py`, `tests/unit/test_task_cache.py`)
- [ ] T017 Add CI step to run unit tests and fail fast if foundational tests fail (file: `.github/workflows/python.yml`)

---

## Phase 3: User Story 1 - Quick Task Management via CLI Commands (Priority: P1) 🎯 MVP

**Goal**: Provide CLI commands to create, list, update, delete, and complete tasks; include authentication commands.

**Independent Test**: Use Click's `CliRunner` to run `gtasks auth`, `gtasks create`, `gtasks list`, `gtasks update`, `gtasks delete`, `gtasks complete` commands against a mocked `TasksAPIProtocol` and assert expected behavior and outputs.

### Tests for User Story 1

- [ ] T018 [P] [US1] Add contract tests for adapter methods in `tests/contract/test_google_tasks_adapter.py` (file: `tests/contract/test_google_tasks_adapter.py`)
- [ ] T019 [P] [US1] Add integration tests for CLI commands in `tests/integration/test_cli_commands.py` using `CliRunner` and mocked API adapter (file: `tests/integration/test_cli_commands.py`)
- [ ] T020 [US1] Add unit tests for `TaskService` business logic in `tests/unit/test_services.py` (file: `tests/unit/test_services.py`)

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create CLI entrypoint `src/gtasks_manager/cli/main.py` with `click` command group `gtasks` and commands stubbed (file: `src/gtasks_manager/cli/main.py`)
- [ ] T022 [P] [US1] Implement `auth` and `logout` commands in `src/gtasks_manager/cli/commands/auth.py` calling adapter `authenticate()` and storage clear (file: `src/gtasks_manager/cli/commands/auth.py`)
- [ ] T023 [P] [US1] Implement `tasks` commands in `src/gtasks_manager/cli/commands/tasks.py`: `create`, `list`, `update`, `delete`, `complete` and the `--list-id` option (file: `src/gtasks_manager/cli/commands/tasks.py`)
- [ ] T024 [US1] Implement `lists` command in `src/gtasks_manager/cli/commands/lists.py` to show available task lists (file: `src/gtasks_manager/cli/commands/lists.py`)
- [ ] T025 [US1] Implement `formatters` in `src/gtasks_manager/cli/formatters.py` to produce human-readable and JSON output (file: `src/gtasks_manager/cli/formatters.py`)
- [ ] T026 [US1] Wire CLI to `TaskService` in `src/gtasks_manager/cli/main.py` and ensure dependency injection (file: `src/gtasks_manager/cli/main.py`)
- [ ] T027 [US1] Implement CLI-specific error handling to translate domain exceptions to user-friendly `click.echo()` messages (file: `src/gtasks_manager/cli/main.py`)
- [ ] T028 [US1] Add unit tests for CLI formatters and command error handling in `tests/unit/test_cli_formatters.py` (file: `tests/unit/test_cli_formatters.py`)
- [ ] T029 [US1] Add integration test for full CLI workflow in `tests/integration/test_cli_workflow.py` (file: `tests/integration/test_cli_workflow.py`)

**Checkpoint**: After these tasks, US1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - Visual Task Dashboard with TUI (Priority: P2)

**Goal**: Provide a Textual TUI to visually browse tasks, show title/due/status, empty state, and basic keyboard navigation.

**Independent Test**: Use Textual's `app.run_test()` to launch `TasksApp`, simulate loading tasks via a mocked `TasksAPIProtocol`, and assert widgets display expected content and reactive attributes update.

### Tests for User Story 2

- [ ] T030 [P] [US2] Add unit tests for TUI widgets in `tests/unit/test_tui_widgets.py` (file: `tests/unit/test_tui_widgets.py`)
- [ ] T031 [P] [US2] Add integration tests for TUI app in `tests/integration/test_tui_app.py` using `app.run_test()` and mocked API (file: `tests/integration/test_tui_app.py`)

### Implementation for User Story 2

- [ ] T032 [P] [US2] Create `src/gtasks_manager/tui/app.py` with `TasksApp` class skeleton and reactive attributes (`tasks`, `selected_task_index`, `loading`, `current_list_id`, `current_list_name`) (file: `src/gtasks_manager/tui/app.py`)
- [ ] T033 [P] [US2] Implement `src/gtasks_manager/tui/screens/task_list.py` with `TaskListView` screen that renders list of tasks and handles key events (file: `src/gtasks_manager/tui/screens/task_list.py`)
- [ ] T034 [P] [US2] Implement widget `src/gtasks_manager/tui/widgets/task_item.py` for individual task display and status indicator (file: `src/gtasks_manager/tui/widgets/task_item.py`)
- [ ] T035 [US2] Implement `src/gtasks_manager/tui/widgets/status_bar.py` for status and notifications (file: `src/gtasks_manager/tui/widgets/status_bar.py`)
- [ ] T036 [US2] Implement keybindings in `src/gtasks_manager/tui/keybindings.py` and connect to `TasksApp.BINDINGS` (file: `src/gtasks_manager/tui/keybindings.py`)
- [ ] T037 [US2] Implement async workers for `load_tasks` and `complete_task` in `src/gtasks_manager/tui/app.py` using Textual `@work` (file: `src/gtasks_manager/tui/app.py`)
- [ ] T038 [US2] Wire TUI `TasksApp` to `TaskService`/adapter via dependency injection in `src/gtasks_manager/tui/app.py` (file: `src/gtasks_manager/tui/app.py`)
- [ ] T039 [US2] Add TUI help screen `src/gtasks_manager/tui/screens/help.py` (file: `src/gtasks_manager/tui/screens/help.py`)
- [ ] T040 [US2] Add integration test for keyboard navigation and loading in `tests/integration/test_tui_keyboard.py` (file: `tests/integration/test_tui_keyboard.py`)

**Checkpoint**: After these tasks, US2 should be independently testable and provide visual task browsing.

---

## Phase 5: User Story 3 - Multi-List Navigation with Tabs (Priority: P3) [Deferred]

**Goal**: Support multiple task lists and tab navigation in the TUI. (Deferred until P2 complete)

**Independent Test**: Launch TUI with multiple lists and verify tab switching shows tasks from each list.

- [ ] T041 [P] [US3] Implement `TaskList` tab UI in `src/gtasks_manager/tui/widgets/tab_bar.py` and integrate with `TasksApp` (file: `src/gtasks_manager/tui/widgets/tab_bar.py`)
- [ ] T042 [US3] Add CLI option `--list-id` improvements and list selection prompts in `src/gtasks_manager/cli/commands/tasks.py` (file: `src/gtasks_manager/cli/commands/tasks.py`)
- [ ] T043 [US3] Add tests for multi-list behavior in `tests/integration/test_multi_list.py` (file: `tests/integration/test_multi_list.py`)
- [ ] T044 [US3] Update `TaskService` to support switching current list and caching per-list task indices (file: `src/gtasks_manager/core/services.py`)

---

## Phase 6: User Story 4 - Keyboard-Driven Navigation (Priority: P3) [Deferred]

**Goal**: Add vim-style keyboard navigation for power users. (Deferred until P2 complete)

**Independent Test**: Simulate keypresses (j/k/h/l) in `app.run_test()` and assert selection and actions occur.

- [ ] T045 [P] [US4] Implement additional keybindings and action handlers for vim-like navigation in `src/gtasks_manager/tui/keybindings.py` (file: `src/gtasks_manager/tui/keybindings.py`)
- [ ] T046 [US4] Add unit tests for vim key handling in `tests/unit/test_vim_bindings.py` (file: `tests/unit/test_vim_bindings.py`)
- [ ] T047 [US4] Update TUI help screen to document vim bindings in `src/gtasks_manager/tui/screens/help.py` (file: `src/gtasks_manager/tui/screens/help.py`)

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, CI, coverage, and performance work that applies across stories

- [ ] T048 [P] Update `docs/quickstart.md` and `specs/001-google-tasks-cli-tui/quickstart.md` with setup and usage steps (file: `docs/quickstart.md`, `specs/001-google-tasks-cli-tui/quickstart.md`)
- [ ] T049 [P] Add comprehensive tests and coverage reporting in CI and require coverage threshold (file: `.github/workflows/python.yml`)
- [ ] T050 [P] Run performance benchmarks for CLI and TUI and document results in `specs/001-google-tasks-cli-tui/research.md` (file: `specs/001-google-tasks-cli-tui/research.md`)
- [ ] T051 [P] Security review: ensure `token.json` is in `.gitignore` and file permissions are set when writing tokens (file: `.gitignore`, `src/gtasks_manager/adapters/storage.py`)
- [ ] T052 [P] Code cleanup and minor refactors across `src/gtasks_manager/` (file: `src/gtasks_manager/`)

---

## Dependencies & Execution Order

- Setup (Phase 1) ➜ Foundational (Phase 2) ➜ User Stories (Phase 3: US1) ➜ User Stories (Phase 4: US2) ➜ Deferred (Phases 5-6: US3/US4) ➜ Polish (Final Phase)

## Parallel Execution Examples

- Setup tasks `T002`, `T003`, `T004` can run in parallel
- Foundational tasks `T010`, `T012`, `T014` are marked [P] and safe to run concurrently
- Within US1, tasks `T021` and `T022` (CLI entrypoint, auth command) can be worked on in parallel by different developers
- TUI widget implementations `T033`, `T034`, `T035` can be implemented in parallel

## Implementation Strategy

- MVP first: focus on Phase 1, Phase 2, and Phase 3 (US1)
- Validate US1 independently with unit and integration tests before proceeding to US2
- Keep core domain free of Click/Textual imports
- Reuse `CLIENT_CONFIG` from `src/gtasks_manager/config.py` for OAuth client configuration

---

## Validation Summary

- Tasks file written to: `specs/001-google-tasks-cli-tui/tasks.md`
- Total tasks: 52
- Tasks by story:
  - Foundational (Phase 2): 10 (T007-T016)
  - US1 (Phase 3): 12 (T018-T029)
  - US2 (Phase 4): 10 (T030-T040)
  - US3 (Phase 5): 4 (T041-T044)
  - US4 (Phase 6): 3 (T045-T047)
  - Setup (Phase 1): 6 (T001-T006)
  - Polish (Final Phase): 5 (T048-T052)
- Parallelizable tasks (marked [P]): T002, T003, T004, T005, T006, T010, T012, T014, T018, T019, T021, T022, T032, T033, T034, T048, T049, T050, T051, T052

**Format validation**: All tasks follow checklist format `- [ ] T### [P?] [USx?] Description with file path`.

**Suggested MVP**: Complete User Story 1 (Phase 3) only.

**[NEEDS CLARIFICATION]**: 0 items - all required docs present and sufficient assumptions made.
