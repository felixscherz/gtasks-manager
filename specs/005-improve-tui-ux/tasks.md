---

description: "Task breakdown for improving TUI UX"
---

# Tasks: Improve TUI UX

**Input**: Design documents from `/specs/005-improve-tui-ux/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per constitution (TDD) and contracts (explicit test requirements)
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create TUI subpackage structure in src/gtasks_manager/tui/ with __init__.py
- [ ] T002 [P] Create TUI application file in src/gtasks_manager/tui/app.py
- [ ] T003 [P] Create TUI widgets file in src/gtasks_manager/tui/widgets.py
- [ ] T004 [P] Create TUI state management file in src/gtasks_manager/tui/state.py
- [ ] T005 [P] Create unit test file for TUI components in tests/unit/test_tui.py
- [ ] T006 [P] Create unit test file for TUI state management in tests/unit/test_state.py
- [ ] T007 [P] Create integration test file for TUI workflows in tests/integration/test_tui_flow.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core TUI framework that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Implement TUI application class in src/gtasks_manager/tui/app.py with Textual App setup
- [ ] T009 [P] Implement TUIApplicationState dataclass in src/gtasks_manager/tui/state.py with selection, list metadata, loading, and error fields
- [ ] T010 [P] Implement TUISelectionState dataclass in src/gtasks_manager/tui/state.py with task_id, preserved flag, and timestamp
- [ ] T011 [P] Implement TaskListMetadata dataclass in src/gtasks_manager/tui/state.py with list_id, name, fetched_at, and is_cached fields
- [ ] T012 Implement TUI application launch() method in src/gtasks_manager/tui/app.py that initializes TUI and blocks until closed
- [ ] T013 [P] Implement base TaskListWidget in src/gtasks_manager/tui/widgets.py with compose() method for task list display
- [ ] T014 [P] Implement base header layout in src/gtasks_manager/tui/widgets.py for TUI header area
- [ ] T015 Add Textual imports and basic app configuration in src/gtasks_manager/tui/app.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Default to TUI on No Command (Priority: P1) 🎯 MVP

**Goal**: Make `gtasks` without subcommand launch the TUI automatically

**Independent Test**: Run `gtasks` with no arguments and verify TUI opens successfully without error messages

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Write failing unit test test_cli_launches_tui_when_no_subcommand in tests/unit/test_cli.py
- [ ] T017 [P] [US1] Write failing unit test test_gui_command_launches_tui in tests/unit/test_cli.py
- [ ] T018 [P] [US1] Write failing integration test test_gtasks_without_args_launches_tui in tests/integration/test_tui_flow.py
- [ ] T019 [P] [US1] Write failing integration test test_invalid_args_show_help_not_tui in tests/integration/test_tui_flow.py

### Implementation for User Story 1

- [ ] T020 [P] [US1] Modify src/gtasks_manager/cli.py to add invoke_without_command=True to main group decorator
- [ ] T021 [P] [US1] Implement main group logic in src/gtasks_manager/cli.py to detect ctx.invoked_subcommand is None and call launch_tui()
- [ ] T022 [US1] Import launch_tui function from .tui.app in src/gtasks_manager/cli.py
- [ ] T023 [US1] Update docstring of main group in src/gtasks_manager/cli.py to document default TUI behavior
- [ ] T024 [US1] Verify existing gui command in src/gtasks_manager/cli.py continues to work identically

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Maintain Backward Compatibility (Priority: P1)

**Goal**: Ensure all existing CLI commands continue to work exactly as before

**Independent Test**: Run each existing CLI command (auth, list, create, complete, uncomplete, delete, gui) and verify behavior is unchanged

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T025 [P] [US2] Write failing unit test test_gtasks_gui_launches_tui_identical_to_default in tests/unit/test_cli.py
- [ ] T026 [P] [US2] Write failing unit test test_existing_commands_unchanged for auth in tests/unit/test_cli.py
- [ ] T027 [P] [US2] Write failing unit test test_existing_commands_unchanged for list in tests/unit/test_cli.py
- [ ] T028 [P] [US2] Write failing unit test test_existing_commands_unchanged for create in tests/unit/test_cli.py
- [ ] T029 [P] [US2] Write failing unit test test_existing_commands_unchanged for complete in tests/unit/test_cli.py
- [ ] T030 [P] [US2] Write failing unit test test_existing_commands_unchanged for uncomplete in tests/unit/test_cli.py
- [ ] T031 [P] [US2] Write failing unit test test_existing_commands_unchanged for delete in tests/unit/test_cli.py
- [ ] T032 [P] [US2] Write failing integration test test_gtasks_without_auth_redirects_to_auth_then_tui in tests/integration/test_tui_flow.py

### Implementation for User Story 2

- [ ] T033 [US2] Verify gui command implementation in src/gtasks_manager/cli.py calls same launch_tui() function as default behavior
- [ ] T034 [US2] Test all existing commands (auth, list, create, complete, uncomplete, delete) work without changes in src/gtasks_manager/cli.py
- [ ] T035 [US2] Verify authentication flow in src/gtasks_manager/cli.py is triggered when gtasks runs without credentials
- [ ] T036 [US2] Ensure error handling in src/gtasks_manager/cli.py shows help for invalid arguments, not TUI

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Preserve Task Selection on Toggle (Priority: P2)

**Goal**: Maintain selection on same task after toggling its completion state

**Independent Test**: Select task in middle of list, toggle its state, verify selection remains on same task

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T037 [P] [US3] Write failing unit test test_set_selection_highlights_task in tests/unit/test_tui.py
- [ ] T038 [P] [US3] Write failing unit test test_preserve_selection_stores_task_id in tests/unit/test_tui.py
- [ ] T039 [P] [US3] Write failing unit test test_restore_selection_moves_highlight_to_correct_index in tests/unit/test_tui.py
- [ ] T040 [P] [US3] Write failing unit test test_selection_state_transitions in tests/unit/test_state.py
- [ ] T041 [P] [US3] Write failing integration test test_task_toggle_preserves_selection_across_refresh in tests/integration/test_tui_flow.py
- [ ] T042 [P] [US3] Write failing integration test test_selection_restoration_handles_moved_task_in_sorted_list in tests/integration/test_tui_flow.py

### Implementation for User Story 3

- [ ] T043 [P] [US3] Implement selected_task_id reactive attribute in src/gtasks_manager/tui/widgets.py for TaskListWidget
- [ ] T044 [P] [US3] Implement watch_selected_task_id method in src/gtasks_manager/tui/widgets.py to highlight task by ID
- [ ] T045 [P] [US3] Implement preserve_selection() method in src/gtasks_manager/tui/app.py that stores current task_id in selection state
- [ ] T046 [P] [US3] Implement restore_selection() method in src/gtasks_manager/tui/app.py that finds task by ID and moves highlight
- [ ] T047 [US3] Modify TaskListWidget in src/gtasks_manager/tui/widgets.py to emit TaskSelected event when task is selected
- [ ] T048 [US3] Modify TaskListWidget in src/gtasks_manager/tui/widgets.py to emit TaskToggled event when task state is toggled
- [ ] T049 [US3] Implement TaskToggled event handler in src/gtasks_manager/tui/app.py that preserves selection, calls API, refreshes list, and restores selection
- [ ] T050 [US3] Add toggle_task_state async method in src/gtasks_manager/tui/app.py with @work decorator for background API call
- [ ] T051 [US3] Add error handling in src/gtasks_manager/tui/app.py for selection restoration when task ID not found

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Display List Name in Header (Priority: P2)

**Goal**: Display current task list name in TUI header area

**Independent Test**: Open TUI and verify list name is displayed in header, verify it updates when switching lists

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T052 [P] [US4] Write failing unit test test_set_list_name_updates_header in tests/unit/test_tui.py
- [ ] T053 [P] [US4] Write failing unit test test_list_name_display_truncates_long_names in tests/unit/test_tui.py
- [ ] T054 [P] [US4] Write failing unit test test_list_name_display_shows_default_when_unavailable in tests/unit/test_tui.py
- [ ] T055 [P] [US4] Write failing integration test test_list_name_updates_when_switching_lists in tests/integration/test_tui_flow.py
- [ ] T056 [P] [US4] Write failing integration test test_api_error_displays_message_and_fallback_to_cache in tests/integration/test_tui_flow.py

### Implementation for User Story 4

- [ ] T057 [P] [US4] Implement ListNameDisplay widget class in src/gtasks_manager/tui/widgets.py with reactive list_name attribute
- [ ] T058 [P] [US4] Implement watch_list_name method in src/gtasks_manager/tui/widgets.py to update display with truncation
- [ ] T059 [P] [US4] Implement set_list_name() method in src/gtasks_manager/tui/app.py that updates ListNameDisplay widget
- [ ] T060 [P] [US4] Add get_task_list_name() method in src/gtasks_manager/tasks.py to fetch list metadata from Google Tasks API
- [ ] T061 [US4] Add list_name field initialization in TUIApplicationState in src/gtasks_manager/tui/state.py
- [ ] T062 [US4] Modify TUI launch() method in src/gtasks_manager/tui/app.py to fetch and display list name on initialization
- [ ] T063 [US4] Add ListNameUpdated event handling in src/gtasks_manager/tui/app.py to update header when list name changes
- [ ] T064 [US4] Add caching logic in src/gtasks_manager/tui/app.py for task list name (5 minute cache)
- [ ] T065 [US4] Add error handling in src/gtasks_manager/tui/app.py for API errors when fetching list name (fallback to "Default List")

**Checkpoint**: At this point, ALL user stories should be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T066 [P] Add comprehensive error handling and user feedback in src/gtasks_manager/tui/app.py for all API failures
- [ ] T067 [P] Implement loading indicator in src/gtasks_manager/tui/widgets.py with set_loading() method support
- [ ] T068 [P] Add show_error() method in src/gtasks_manager/tui/app.py to display errors in footer/modal
- [ ] T069 [P] Add type hints to all new functions in src/gtasks_manager/tui/ following constitution requirements
- [ ] T070 [P] Add docstrings to all public methods in src/gtasks_manager/tui/ per project conventions
- [ ] T071 [P] Run ruff linting and fix all auto-fixable issues in src/gtasks_manager/tui/
- [ ] T072 [P] Run ruff formatting in src/gtasks_manager/tui/ to ensure PEP 8 compliance
- [ ] T073 [P] Run mypy type checking in src/gtasks_manager/tui/ to verify type hints
- [ ] T074 [P] Run full test suite in tests/ to verify all tests pass
- [ ] T075 Validate quickstart.md examples work correctly by testing each scenario
- [ ] T076 Update AGENTS.md with any new patterns or conventions established during implementation
- [ ] T077 Clean up any temporary code or debug statements in src/gtasks_manager/tui/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 implementation but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 TUI framework but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 TUI framework but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per constitution)
- State models before widgets
- Widgets before TUI app logic
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models and widgets within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write failing unit test test_cli_launches_tui_when_no_subcommand in tests/unit/test_cli.py"
Task: "Write failing unit test test_gui_command_launches_tui in tests/unit/test_cli.py"
Task: "Write failing integration test test_gtasks_without_args_launches_tui in tests/integration/test_tui_flow.py"
Task: "Write failing integration test test_invalid_args_show_help_not_tui in tests/integration/test_tui_flow.py"

# Launch implementation tasks in parallel:
Task: "Modify src/gtasks_manager/cli.py to add invoke_without_command=True to main group decorator"
Task: "Implement main group logic in src/gtasks_manager/cli.py to detect ctx.invoked_subcommand is None and call launch_tui()"
Task: "Import launch_tui function from .tui.app in src/gtasks_manager/cli.py"
```

---

## Parallel Example: User Story 3 (Selection Preservation)

```bash
# Launch all tests for User Story 3 together:
Task: "Write failing unit test test_set_selection_highlights_task in tests/unit/test_tui.py"
Task: "Write failing unit test test_preserve_selection_stores_task_id in tests/unit/test_tui.py"
Task: "Write failing unit test test_restore_selection_moves_highlight_to_correct_index in tests/unit/test_tui.py"
Task: "Write failing integration test test_task_toggle_preserves_selection_across_refresh in tests/integration/test_tui_flow.py"

# Launch widget and state work in parallel:
Task: "Implement selected_task_id reactive attribute in src/gtasks_manager/tui/widgets.py for TaskListWidget"
Task: "Implement watch_selected_task_id method in src/gtasks_manager/tui/widgets.py to highlight task by ID"
Task: "Implement preserve_selection() method in src/gtasks_manager/tui/app.py that stores current task_id in selection state"
Task: "Implement restore_selection() method in src/gtasks_manager/tui/app.py that finds task by ID and moves highlight"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL
3. Complete Phase 3: User Story 1 (T016-T024)
4. **STOP and VALIDATE**: Test User Story 1 independently - `gtasks` launches TUI
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T007) + Foundational (T008-T015) together
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T024)
   - Developer B: User Story 2 (T025-T036)
   - Developer C: User Story 3 (T037-T051)
   - Developer D: User Story 4 (T052-T065)
3. Stories complete and integrate independently
4. Team completes Polish phase (T066-T077) together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests MUST fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
