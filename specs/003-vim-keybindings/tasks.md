# Tasks: VIM Keybindings for TUI Task List

**Input**: Design documents from `/specs/003-vim-keybindings/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Single project with hexagonal architecture**: `src/gtasks_manager/core/`, `src/gtasks_manager/tui/`, `src/gtasks_manager/adapters/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify environment and prepare for feature implementation

- [ ] T001 Verify development environment is configured with required dependencies (Python 3.11+, Textual 0.47+, pytest-asyncio 0.21.0+)
- [ ] T002 Run existing test suite to establish baseline in tests/
- [ ] T003 Review existing TUI code structure in src/gtasks_manager/tui/app.py and keybindings.py

**Checkpoint**: Environment verified and existing code understood

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T004 Fix TasksApp.__init__ to initialize KeyBindingManager in src/gtasks_manager/tui/app.py (adds self.keybinding_manager = KeyBindingManager())
- [ ] T005 Verify existing BINDINGS list in TasksApp includes required keys (j, k, enter, h, l, q, r) in src/gtasks_manager/tui/app.py
- [ ] T006 Verify existing action methods (action_move_down, action_move_up, action_toggle_completion, action_cursor_down, action_cursor_up) are implemented in src/gtasks_manager/tui/app.py
- [ ] T007 Ensure watch_tasks() method properly rebuilds ListView with task status indicators (○ vs ✓) in src/gtasks_manager/tui/app.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - VIM Navigation (Priority: P1) 🎯 MVP

**Goal**: Enable VIM-style navigation (j/k keys) to move up and down through the task list

**Independent Test**: Can be fully tested by opening TUI and pressing 'j' and 'k' to verify list selection moves up and down, without any other features being implemented.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Verify existing test_j_key_moves_selection_down in tests/integration/test_tui_navigation.py passes
- [ ] T009 [P] [US1] Verify existing test_k_key_moves_selection_up in tests/integration/test_tui_navigation.py passes
- [ ] T010 [P] [US1] Verify existing test_j_key_respects_list_boundaries in tests/integration/test_tui_navigation.py passes
- [ ] T011 [P] [US1] Verify existing test_k_key_respects_list_boundaries in tests/integration/test_tui_navigation.py passes
- [ ] T012 [P] [US1] Add test_empty_task_list_handles_vim_navigation in tests/integration/test_tui_navigation.py (verify 'j' and 'k' keys don't crash with empty task list)

### Implementation for User Story 1

- [ ] T013 [US1] Enhance action_cursor_down() to properly handle VIM 'j' key with boundary checking in src/gtasks_manager/tui/app.py (ensure selection doesn't go past last task)
- [ ] T014 [US1] Enhance action_cursor_up() to properly handle VIM 'k' key with boundary checking in src/gtasks_manager/tui/app.py (ensure selection doesn't go before first task)
- [ ] T015 [US1] Verify _update_selected_task() correctly updates selected_task_id based on current ui_focus.index in src/gtasks_manager/tui/app.py
- [ ] T016 [US1] Ensure empty task list is handled gracefully when pressing 'j' or 'k' (no errors, no index out of bounds) in src/gtasks_manager/tui/app.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Toggle Task with ENTER (Priority: P1) 🎯 MVP

**Goal**: Enable ENTER key to toggle completion status of selected task

**Independent Test**: Can be fully tested by opening the TUI, selecting a task, and pressing ENTER to verify the task's completion state toggles between done and undone.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US2] Add test_enter_key_toggles_task_completion in tests/integration/test_tui_navigation.py (press ENTER, verify task.status changes from NEEDS_ACTION to COMPLETED)
- [ ] T018 [P] [US2] Add test_enter_key_toggles_task_back in tests/integration/test_tui_navigation.py (press ENTER twice, verify status toggles back)
- [ ] T019 [P] [US2] Add test_enter_key_does_nothing_when_no_selection in tests/integration/test_tui_navigation.py (press ENTER with ui_focus.index = None, verify no change)
- [ ] T020 [P] [US2] Add test_rapid_key_presses_handled_correctly in tests/integration/test_tui_navigation.py (press ENTER multiple times rapidly, verify state doesn't break)

### Implementation for User Story 2

- [ ] T021 [US2] Enhance action_toggle_completion() to handle ENTER key press and toggle selected task status in src/gtasks_manager/tui/app.py
- [ ] T022 [US2] Verify _toggle_completion() method correctly toggles task.status (NEEDS_ACTION ↔ COMPLETED) in src/gtasks_manager/tui/app.py
- [ ] T023 [US2] Ensure _persist_toggle() background worker is called with @work decorator to prevent UI blocking in src/gtasks_manager/tui/app.py
- [ ] T024 [US2] Verify _revert_toggle() method properly restores previous task status on API failure in src/gtasks_manager/tui/app.py
- [ ] T025 [US2] Ensure watch_tasks() immediately updates ListView display when task.status changes (visual feedback: ○ ↔ ✓) in src/gtasks_manager/tui/app.py
- [ ] T026 [US2] Add error handling for API failures during task toggle (catch exception, revert state, log error) in src/gtasks_manager/tui/app.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Arrow Keys Continue Working (Priority: P2)

**Goal**: Ensure arrow keys continue to work alongside VIM keys for backward compatibility

**Independent Test**: Can be tested by verifying that arrow keys still function correctly before and after implementing VIM keybindings.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T027 [P] [US3] Add test_arrow_keys_still_work_with_vim_enabled in tests/integration/test_tui_navigation.py (press down/up arrow, verify selection moves)
- [ ] T028 [P] [US3] Add test_alternating_keys_work_correctly in tests/integration/test_tui_navigation.py (alternate between arrow keys and j/k, verify consistent behavior)

### Implementation for User Story 3

- [ ] T029 [US3] Verify action_cursor_down() and action_cursor_up() work for both VIM keys (j/k) AND arrow keys in src/gtasks_manager/tui/app.py
- [ ] T030 [US3] Ensure no regression in existing arrow key navigation after adding VIM key support in src/gtasks_manager/tui/app.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Visual Feedback for Selected Task (Priority: P3)

**Goal**: Ensure currently selected task has clear visual highlighting

**Independent Test**: Can be tested by verifying that navigating through the list shows clear visual indication of the selected item.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T031 [P] [US4] Add test_selected_task_is_visually_highlighted in tests/integration/test_tui_navigation.py (verify ListView highlights current index)
- [ ] T032 [P] [US4] Add test_highlight_removed_when_selection_moves in tests/integration/test_tui_navigation.py (verify previous task loses highlight when moving to next task)

### Implementation for User Story 4

- [ ] T033 [US4] Verify ListView automatically highlights selected item when ui_focus.index changes in src/gtasks_manager/tui/app.py
- [ ] T034 [US4] Ensure CSS styling provides clear visual distinction for selected vs non-selected tasks in src/gtasks_manager/tui/app.py (inverted colors, bold, or other indicator)
- [ ] T035 [US4] Verify visual feedback works with limited color support (terminals without 256 colors) in src/gtasks_manager/tui/app.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T036 [P] Add unit tests for KeyBindingManager in tests/unit/test_keybindings.py (test_get_action_returns_mapped_action, test_get_action_returns_none_when_disabled, test_get_action_returns_none_for_unknown_key, test_update_mapping_adds_new_binding, test_remove_mapping_deletes_binding)
- [ ] T037 [P] Run full test suite and verify all tests pass: uv run pytest tests/ -k "tui or keybindings" -v
- [ ] T038 [P] Run linting on TUI code: uv run ruff check src/gtasks_manager/tui/
- [ ] T039 [P] Format TUI code: uv run ruff format src/gtasks_manager/tui/
- [ ] T040 Manually test TUI with all keybindings (j, k, enter, arrow keys) following quickstart.md procedures
- [ ] T041 Test edge cases: empty task list, no selection, rapid key presses, API failures during toggle
- [ ] T042 Commit changes with descriptive commit message for feature completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (US1 P1 → US2 P1 → US3 P2 → US4 P3)
  - US1 and US2 can potentially be worked in parallel by different developers (both P1)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Can be parallel with US1 (both P1), but should be independently testable
- **User Story 3 (P2)**: Depends on US1 and US2 completion (arrow keys must work alongside VIM keys)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Enhances existing UI, no hard dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Tests within a story marked [P] can run in parallel
- Implementation tasks build on each other within the story
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Tests within each user story marked [P] can run in parallel
- US1 and US2 tests can run in parallel (both P1 priority)
- US1 and US2 implementation can potentially work in parallel by different developers
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Verify existing test_j_key_moves_selection_down in tests/integration/test_tui_navigation.py passes"
Task: "Verify existing test_k_key_moves_selection_up in tests/integration/test_tui_navigation.py passes"
Task: "Verify existing test_j_key_respects_list_boundaries in tests/integration/test_tui_navigation.py passes"
Task: "Verify existing test_k_key_respects_list_boundaries in tests/integration/test_tui_navigation.py passes"
Task: "Add test_empty_task_list_handles_vim_navigation in tests/integration/test_tui_navigation.py"

# Run all tests:
uv run pytest tests/integration/test_tui_navigation.py::test_j_key_moves_selection_down -v
uv run pytest tests/integration/test_tui_navigation.py::test_k_key_moves_selection_up -v
uv run pytest tests/integration/test_tui_navigation.py::test_j_key_respects_list_boundaries -v
uv run pytest tests/integration/test_tui_navigation.py::test_k_key_respects_list_boundaries -v
uv run pytest tests/integration/test_tui_navigation.py::test_empty_task_list_handles_vim_navigation -v
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - CRITICAL
3. Complete Phase 3: User Story 1 - VIM Navigation (T008-T016)
4. Complete Phase 4: User Story 2 - Toggle Task with ENTER (T017-T026)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Manually test TUI with VIM navigation and ENTER toggle
7. Demo MVP: Users can navigate with j/k and toggle tasks with ENTER

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (VIM Navigation) → Test independently → Feature works
3. Add User Story 2 (ENTER Toggle) → Test independently → MVP Complete!
4. Add User Story 3 (Arrow Keys) → Test independently → Backward Compatible
5. Add User Story 4 (Visual Feedback) → Test independently → Polished UX
6. Polish phase → Quality validated
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T016)
   - Developer B: User Story 2 (T017-T026) - parallel with US1
3. After US1 and US2 complete:
   - Developer A: User Story 3 (T027-T030)
   - Developer B: User Story 4 (T031-T035)
4. Team completes Polish phase together (T036-T042)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group (constitution requirement)
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- MVP includes User Story 1 (VIM Navigation) and User Story 2 (ENTER Toggle) - both P1 priority
- User requested TDD approach and Textual testing documentation as reference
- Existing tests (test_tui_navigation.py) already cover basic VIM navigation - verify and enhance them
