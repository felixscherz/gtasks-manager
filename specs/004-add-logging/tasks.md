---

description: "Task list for Add Application Logging feature"
---

# Tasks: Add Application Logging

**Input**: Design documents from `/specs/004-add-logging/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature follows TDD approach per constitution requirements. Tests are included and should be written BEFORE implementation (red-green-refactor).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the plan.md structure for gtasks-manager CLI application

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create test directory structure if not exists: tests/unit/ and tests/integration/
- [X] T002 Verify existing project structure: src/gtasks_manager/ with cli.py, config.py, etc.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core logging infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] [US1] Write failing unit test for get_log_dir() function in tests/unit/test_logging_config.py
- [X] T004 [P] [US1] Write failing unit test for setup_logging() function in tests/unit/test_logging_config.py
- [X] T005 [US1] Create src/gtasks_manager/logging_config.py module with get_log_dir() function for OS-specific log directory paths
- [X] T006 [US1] Implement setup_logging() function in src/gtasks_manager/logging_config.py with RotatingFileHandler configuration
- [X] T007 [US1] Add logging configuration constants to src/gtasks_manager/logging_config.py (DEFAULT_LOG_FILENAME, MAX_LOG_SIZE_BYTES, BACKUP_FILE_COUNT, LOG_FORMAT, LOG_DATE_FORMAT, VERBOSITY_TO_LOG_LEVEL)
- [X] T008 [US1] Add directory creation with error handling in setup_logging() function in src/gtasks_manager/logging_config.py
- [X] T009 [US1] Add permission error handling with user-friendly error message in setup_logging() function in src/gtasks_manager/logging_config.py

**Checkpoint**: Foundation ready - logging_config.py module complete with all core functionality, user story implementation can now begin

---

## Phase 3: User Story 1 - Automatic File Logging (Priority: P1) 🎯 MVP

**Goal**: Application events and errors are automatically written to a log file at OS-specific location with timestamps and stack traces

**Independent Test**: Run any gtasks command, verify log file is created at ~/.config/gtasks-manager/logs/gtasks.log (or Windows equivalent) with timestamped entries

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Write failing unit test test_get_log_dir_posix() in tests/unit/test_logging_config.py (verify Linux/macOS path)
- [X] T011 [P] [US1] Write failing unit test test_get_log_dir_windows() in tests/unit/test_logging_config.py (verify Windows path with APPDATA)
- [X] T012 [P] [US1] Write failing unit test test_setup_logging_creates_directory() in tests/unit/test_logging_config.py (verify directory auto-creation)
- [X] T013 [P] [US1] Write failing unit test test_setup_logging_creates_log_file() in tests/unit/test_logging_config.py (verify log file creation)
- [X] T014 [P] [US1] Write failing unit test test_setup_logging_timestamp_format() in tests/unit/test_logging_config.py (verify ISO 8601 timestamp format)
- [X] T015 [P] [US1] Write failing unit test test_setup_logging_error_stack_trace() in tests/unit/test_logging_config.py (verify stack trace inclusion)
- [X] T016 [P] [US1] Write failing unit test test_setup_logging_permission_error() in tests/unit/test_logging_config.py (verify error handling)
- [X] T017 [P] [US1] Write failing integration test test_log_file_created_on_command() in tests/integration/test_logging_integration.py (end-to-end log file creation)

### Implementation for User Story 1

- [X] T018 [US1] Implement get_log_dir() in src/gtasks_manager/logging_config.py with sys.platform detection (win32 vs POSIX)
- [X] T019 [US1] Implement directory auto-creation with Path.mkdir(parents=True, exist_ok=True) in setup_logging() in src/gtasks_manager/logging_config.py
- [X] T020 [US1] Configure log formatter with LOG_FORMAT and LOG_DATE_FORMAT for ISO 8601 timestamps in src/gtasks_manager/logging_config.py
- [X] T021 [US1] Configure RotatingFileHandler with MAX_LOG_SIZE_BYTES and BACKUP_FILE_COUNT in src/gtasks_manager/logging_config.py
- [X] T022 [US1] Add error handling for PermissionError and OSError in setup_logging() in src/gtasks_manager/logging_config.py
- [X] T023 [US1] Add log entry writing with timestamp and level to logging_config.py (via logging.info(), logging.error())
- [X] T024 [US1] Add stack trace inclusion for error logging using exc_info=True in src/gtasks_manager/logging_config.py
- [X] T025 [US1] Add unit test coverage verification: run pytest tests/unit/test_logging_config.py to ensure all tests pass

**Checkpoint**: At this point, User Story 1 should be fully functional - running any gtasks command creates log file with timestamps

---

## Phase 4: User Story 2 - Configurable Verbosity Level (Priority: P1)

**Goal**: Users can control log detail via -v flag (WARNING by default, INFO with -v, DEBUG with -vv)

**Independent Test**: Run same command with -v, -vv, and no flag; verify log file contains appropriate level of detail for each

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T026 [P] [US2] Write failing unit test test_setup_logging_default_verbosity() in tests/unit/test_logging_config.py (verify WARNING level)
- [X] T027 [P] [US2] Write failing unit test test_setup_logging_info_verbosity() in tests/unit/test_logging_config.py (verify INFO level with -v)
- [X] T028 [P] [US2] Write failing unit test test_setup_logging_debug_verbosity() in tests/unit/test_logging_config.py (verify DEBUG level with -vv)
- [X] T029 [P] [US2] Write failing unit test test_verbosity_flag_filters_logs() in tests/integration/test_logging_integration.py (verify log level filtering)
- [X] T030 [P] [US2] Write failing unit test test_log_level_filtering() in tests/unit/test_logging_config.py (verify only appropriate levels logged)

### Implementation for User Story 2

- [X] T031 [US2] Verify VERBOSITY_TO_LOG_LEVEL mapping in src/gtasks_manager/logging_config.py (0=WARNING, 1=INFO, 2+=DEBUG)
- [X] T032 [US2] Import setup_logging and get_log_dir in src/gtasks_manager/cli.py
- [X] T033 [US2] Add @click.option('-v', '--verbose', count=True, help='Increase verbosity level (use -v or -vv)') to all CLI commands in src/gtasks_manager/cli.py (create, list, complete, delete, lists, auth, logout)
- [X] T034 [US2] Call setup_logging(verbosity) at start of each command in src/gtasks_manager/cli.py
- [X] T035 [US2] Handle setup_logging() return value (False on error) in src/gtasks_manager/cli.py
- [X] T036 [US2] Add logging statements to existing command implementations in src/gtasks_manager/cli.py (logging.info() for command start, logging.error() with exc_info=True for errors)
- [X] T037 [US2] Add unit test coverage verification: run pytest tests/unit/test_logging_config.py to ensure all US2 tests pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - logging with configurable verbosity

---

## Phase 5: User Story 3 - Discoverable Log File Location (Priority: P2)

**Goal**: Users can easily discover log file location via help text and documentation

**Independent Test**: Run gtasks --help; verify log file location is displayed (e.g., "Logs written to: ~/.config/gtasks-manager/logs/gtasks.log")

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T038 [P] [US3] Write failing unit test test_get_log_file_path() in tests/unit/test_logging_config.py (verify log file path string)
- [ ] T039 [P] [US3] Write failing integration test test_help_shows_log_location() in tests/integration/test_logging_integration.py (verify --help output)

### Implementation for User Story 3

- [ ] T040 [US3] Add get_log_file_path() function to src/gtasks_manager/config.py that returns OS-specific log file path string
- [ ] T041 [US3] Import get_log_file_path in src/gtasks_manager/cli.py
- [ ] T042 [US3] Add log file location to @main.command() or --help output in src/gtasks_manager/cli.py (e.g., as footer or separate help section)
- [ ] T043 [US3] Format log file location for display in src/gtasks_manager/cli.py (include platform-specific path)
- [ ] T044 [US3] Add unit test coverage verification: run pytest tests/unit/test_logging_config.py to ensure all US3 tests pass

**Checkpoint**: All user stories should now be independently functional - complete logging system with discoverable log location

---

## Phase 6: Additional Integration Tests

**Purpose**: Validate cross-cutting concerns and edge cases

- [X] T045 [P] Write failing integration test test_log_file_rotation() in tests/integration/test_logging_integration.py (verify 10MB rotation triggers)
- [X] T046 [P] Write failing integration test test_concurrent_writes_no_corruption() in tests/integration/test_logging_integration.py (verify multiple processes write safely)
- [X] T047 [P] Write failing integration test test_log_file_exists_after_crash() in tests/integration/test_logging_integration.py (verify log integrity)
- [X] T048 [P] Write failing integration test test_large_log_handling() in tests/integration/test_logging_integration.py (verify no performance degradation)
- [X] T049 Implement log rotation test in tests/integration/test_logging_integration.py (write >10MB, verify backup files created)
- [X] T050 Implement concurrent writes test in tests/integration/test_logging_integration.py (spawn 5 processes, verify no corruption)
- [X] T051 Implement crash recovery test in tests/integration/test_logging_integration.py (simulate crash, verify log intact)
- [X] T052 Verify all integration tests pass: run pytest tests/integration/test_logging_integration.py

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, performance, and documentation

- [ ] T053 [P] Run ruff linting on src/gtasks_manager/logging_config.py and fix all issues
- [ ] T054 [P] Run ruff formatting on src/gtasks_manager/logging_config.py to ensure code style
- [ ] T055 [P] Run ruff linting on tests/unit/test_logging_config.py and fix all issues
- [ ] T056 [P] Run ruff formatting on tests/unit/test_logging_config.py
- [ ] T057 [P] Run ruff linting on tests/integration/test_logging_integration.py and fix all issues
- [ ] T058 [P] Run ruff formatting on tests/integration/test_logging_integration.py
- [ ] T059 Run mypy type checking on src/gtasks_manager/logging_config.py with strict mode
- [ ] T060 Run mypy type checking on tests/ to verify type hints
- [ ] T061 [P] Run pytest with coverage to verify 90%+ coverage for logging_config.py
- [ ] T062 Update AGENTS.md with logging patterns and examples (see quickstart.md for common patterns)
- [ ] T063 Update README.md or documentation with logging feature description and usage examples
- [ ] T064 Add logging usage examples to quickstart.md if not already comprehensive
- [ ] T065 Run performance test: verify log file creation within 100ms (SC-001)
- [ ] T066 Run full test suite: uv run pytest tests/unit/test_logging_config.py tests/integration/test_logging_integration.py
- [ ] T067 Verify all success criteria from spec.md are met (SC-001 through SC-008)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational (Phase 2) - Integrates with US1 but should be independently testable
  - User Story 3 (P2): Can start after Foundational (Phase 2) - Can work independently of US1/US2
- **Integration Tests (Phase 6)**: Depends on all user stories being complete
- **Polish (Phase 7)**: Depends on all implementation phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core logging infrastructure must exist first
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Requires CLI integration, but can be tested independently
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Requires get_log_file_path() function, but minimal dependency on US1/US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per constitution)
- All tests for a story marked [P] can run in parallel
- Core implementation (T018, T031, T040) comes before integration tasks
- Story complete before moving to next priority

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T001 and T002 are independent and can run in parallel

**Within Foundational (Phase 2)**:
- T003 and T004 can run in parallel (different test functions)
- T005, T006, T007 can run in parallel (different file sections)
- T008 and T009 can run in parallel (different error handling scenarios)

**Within User Story 1 (Phase 3)**:
- All tests T010-T017 can run in parallel (different test functions, no dependencies)
- Implementation tasks T018-T025 have dependencies (must complete in order)

**Within User Story 2 (Phase 4)**:
- All tests T026-T030 can run in parallel
- T031 is verification task (no dependencies)
- T032-T037 have CLI integration dependencies (must complete in order)

**Within User Story 3 (Phase 5)**:
- Tests T038-T039 can run in parallel
- T040-T044 have dependencies (must complete in order)

**Within Integration Tests (Phase 6)**:
- All tests T045-T048 can run in parallel
- Implementation tasks T049-T052 can run in parallel (different test implementations)

**Within Polish (Phase 7)**:
- All linting tasks T053-T058 can run in parallel (different files)
- T059 and T060 can run in parallel (different directories)
- T061 is standalone
- Documentation tasks T062-T064 can run in parallel
- Final verification tasks T065-T067 must run in sequence

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write these FIRST):
Task: "Write failing unit test test_get_log_dir_posix() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_get_log_dir_windows() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_setup_logging_creates_directory() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_setup_logging_creates_log_file() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_setup_logging_timestamp_format() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_setup_logging_error_stack_trace() in tests/unit/test_logging_config.py"
Task: "Write failing unit test test_setup_logging_permission_error() in tests/unit/test_logging_config.py"
Task: "Write failing integration test test_log_file_created_on_command() in tests/integration/test_logging_integration.py"

# After all tests fail, implement sequentially:
Task: "Implement get_log_dir() in src/gtasks_manager/logging_config.py"
Task: "Implement directory auto-creation with Path.mkdir() in setup_logging()"
Task: "Configure log formatter with ISO 8601 timestamps"
Task: "Configure RotatingFileHandler with size and backup count"
Task: "Add error handling for PermissionError and OSError"
Task: "Add log entry writing with timestamp and level"
Task: "Add stack trace inclusion for error logging"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T009) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T010-T025)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Run: `uv run pytest tests/unit/test_logging_config.py`
   - Run: `gtasks list` (or any command)
   - Verify: Log file exists at ~/.config/gtasks-manager/logs/gtasks.log
   - Verify: Log file contains timestamped entries
5. Commit and deploy if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T009)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (T010-T025)
3. Add User Story 2 → Test independently → Deploy/Demo (T026-T037)
4. Add User Story 3 → Test independently → Deploy/Demo (T038-T044)
5. Add Integration Tests → Full test coverage (T045-T052)
6. Polish and documentation → Production ready (T053-T067)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (T010-T025)
   - Developer B: User Story 2 (T026-T037)
   - Developer C: User Story 3 (T038-T044)
3. All developers complete integration tests together (T045-T052)
4. Team completes polish phase together (T053-T067)

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD approach**: Verify tests fail before implementing (constitution requirement)
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- Follow constitution: Python 3.11+ type hints, ruff linting, pytest testing
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

- **Total Tasks**: 67
- **Setup (Phase 1)**: 2 tasks
- **Foundational (Phase 2)**: 7 tasks
- **User Story 1 (Phase 3)**: 16 tasks (8 tests + 8 implementation)
- **User Story 2 (Phase 4)**: 12 tasks (5 tests + 7 implementation)
- **User Story 3 (Phase 5)**: 7 tasks (2 tests + 5 implementation)
- **Integration Tests (Phase 6)**: 8 tasks (4 tests + 4 implementation)
- **Polish (Phase 7)**: 15 tasks
- **Parallel Opportunities**: 48 tasks marked [P] for parallel execution
- **Test-First Approach**: 19 test tasks written before implementation per TDD constitution

---

## Format Validation

All tasks follow the required checklist format:
- ✅ Checkbox: `- [ ]` at start
- ✅ Task ID: Sequential T001-T067
- ✅ [P] marker: Only on parallelizable tasks (48 tasks)
- ✅ [Story] label: Only on user story phase tasks (US1, US2, US3)
- ✅ Description: Clear action with exact file paths
- ✅ Independent test criteria: Defined for each user story phase
- ✅ Dependencies: Clearly documented
- ✅ Parallel execution: Examples and opportunities identified
