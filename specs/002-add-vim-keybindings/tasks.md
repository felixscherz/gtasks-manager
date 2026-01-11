---

description: "Tasks for Add VIM Keybindings feature"
---

# Tasks: Add VIM Keybindings

**Input**: Design documents from `/specs/002-add-vim-keybindings/`
**Prerequisites**: `plan.md`, `spec.md` (required); `research.md`, `data-model.md`, `contracts/`, `quickstart.md` (available)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and developer tooling required to implement the feature

- [X] T001 Update developer README to document `uv` usage and dev commands in `README.md`
- [X] T002 Ensure `uv.lock` is present and add instruction to update it in `docs/README.md`
- [X] T003 Add/verify `ruff` configuration in `pyproject.toml` (lint/format rules) at `pyproject.toml`
- [X] T004 Update CI workflow to run dev/test commands with `uv run` in `.github/workflows/python.yml`
- [X] T005 Add pytest configuration for Textual async tests in `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core code and test scaffolding that MUST be complete before user stories

- [X] T006 [P] [FOUNDATION] Create skeleton module `KeyBindingManager` in `src/gtasks_manager/tui/keybindings.py`
- [X] T007 [P] [FOUNDATION] Add `UI Focus` representation and validations to `src/gtasks_manager/core/models.py`
- [X] T008 [FOUNDATION] Add optimistic toggle API wrapper method `toggle_task_completion(task_id: str)` to `src/gtasks_manager/tasks.py` (background-friendly signature)
- [X] T009 [P] [FOUNDATION] Add Textual helper utilities for transient notifications and accessibility announcements in `src/gtasks_manager/tui/utils.py`
- [X] T010 [FOUNDATION] Add test scaffolding files: `tests/unit/test_keybindings.py`, `tests/integration/test_tui_navigation.py`, `tests/integration/test_toggle_completion.py`
- [X] T011 [P] [FOUNDATION] Document keybinding configuration schema in `specs/002-add-vim-keybindings/data-model.md` (confirm defaults and mappings)

**Checkpoint**: Once T006-T011 complete, user stories can be implemented independently

---

## Phase 3: User Story 1 - Navigate task list with VIM keys (Priority: P1) 🎯 MVP

**Goal**: Implement `h`, `j`, `k`, `l` navigation in the TUI so users can move selection and change pane focus.

**Independent Test**: With the TUI open and a list visible, pressing `j` moves selection down, `k` moves up, `h` moves focus left, `l` moves focus right. Tests should run via `uv run pytest`.

### Tests (TDD-first)

- [X] T012 [P] [US1] Create unit tests for `KeyBindingManager` in `tests/unit/test_keybindings.py` verifying mapping and enabled/disabled behavior
- [X] T013 [P] [US1] Create integration test `tests/integration/test_tui_navigation.py` using `app.run_test()` to assert `j/k/h/l` change selection and focus

### Implementation

- [X] T014 [P] [US1] Implement `KeyBindingManager` mappings and enable/disable flag in `src/gtasks_manager/tui/keybindings.py` (depends on T006)
- [X] T015 [US1] Wire `on_key` handlers in `src/gtasks_manager/tui/app.py` (or the relevant TaskList widget) to call `KeyBindingManager` actions (depends on T014)
- [X] T016 [US1] Update UI components to use `reactive` attributes for selection/index in `src/gtasks_manager/tui/app.py` and `src/gtasks_manager/tui/widgets.py` (or the file that defines the task list)
- [X] T017 [US1] Ensure key handling returns early when focus is inside input widgets (update `src/gtasks_manager/tui/app.py` or helper `src/gtasks_manager/tui/utils.py`) (depends on T009)
- [X] T018 [US1] Add visual highlight/selection update behavior to `src/gtasks_manager/tui/app.py` and ensure latency < 100ms for local env

**Checkpoint**: US1 should be fully functional and testable after T012-T018

---

## Phase 4: User Story 2 - Toggle task completion with Enter (Priority: P1)

**Goal**: Pressing `Enter` toggles the selected task's completion state with optimistic UI update and background persistence.

**Independent Test**: With a task selected, pressing `Enter` updates the UI and then persists the change; on persistence failure the UI reverts and shows a transient error.

### Tests (TDD-first)

- [X] T019 [P] [US2] Create unit test `tests/unit/test_toggle_optimistic.py` for optimistic toggle logic (in-memory toggle and revert)
- [X] T020 [P] [US2] Create integration test `tests/integration/test_toggle_completion.py` that simulates a successful and a failing persistence (mock `src/gtasks_manager/tasks.py` API call)

### Implementation

- [X] T021 [P] [US2] Add `Enter` mapping to `KeyBindingManager` in `src/gtasks_manager/tui/keybindings.py` (depends on T014)
- [X] T022 [US2] Implement optimistic UI update in `src/gtasks_manager/tui/app.py` (update Task.status reactively) and call `toggle_task_completion` from `src/gtasks_manager/tasks.py` inside a `@work` background worker (depends on T008, T014, T016)
- [X] T023 [US2] Implement persistence method `toggle_task_completion` in `src/gtasks_manager/tasks.py` to call adapters/google API and raise on failure (depends on T008)
- [X] T024 [US2] On persistence failure, revert status and show transient error using `src/gtasks_manager/tui/utils.py` (depends on T009, T022)
- [X] T025 [US2] Add logging for toggle operations in `src/gtasks_manager/tasks.py` and `src/gtasks_manager/tui/keybindings.py`

**Checkpoint**: US2 should be independently testable after T019-T025

---

## Phase 5: User Story 3 - Respect existing shortcuts and accessibility (Priority: P2)

**Goal**: Ensure VIM bindings coexist with existing shortcuts, don't trigger in inputs, and focus changes are announced for accessibility.

**Independent Test**: Existing non-VIM shortcuts (e.g., `c` for create) still function when VIM bindings enabled; a screen reader-equivalent accessibility announcement is emitted on focus change.

### Tests

- [X] T026 [P] [US3] Create unit tests `tests/unit/test_shortcut_conflicts.py` ensuring that non-VIM shortcuts still invoke their handlers when applicable
- [X] T027 [P] [US3] Create integration accessibility test `tests/integration/test_accessibility_focus.py` asserting focus announcements on pane changes

### Implementation

- [X] T028 [US3] Add conflict-resolution logic to `KeyBindingManager` to respect existing shortcuts configured in `src/gtasks_manager/cli/` and `src/gtasks_manager/tui/` (update `src/gtasks_manager/tui/keybindings.py`)
- [X] T029 [US3] Ensure key handlers check for input focus and do not act when typing in `src/gtasks_manager/tui/app.py` (depends on T017)
- [X] T030 [US3] Implement accessibility announcements on focus change using `src/gtasks_manager/tui/utils.py` (depends on T009)
- [X] T031 [US3] Add small VIM status indicator in `src/gtasks_manager/tui/app.py` showing if VIM bindings are enabled (toggleable via `KeyBindingManager.enabled`)
- [ ] T032 [US3] Document any shortcut conflicts and resolution order in `specs/002-add-vim-keybindings/quickstart.md`

**Checkpoint**: US3 should be independently testable after T026-T032

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, tests, and release prep

- [X] T033 [P] Update `specs/002-add-vim-keybindings/quickstart.md` with final usage and developer notes (mirror changes made during implementation)
- [ ] T034 [P] Add/extend unit tests in `tests/unit/` for edge cases (rapid key repeats, input typing)
- [X] T035 [P] Run `uv run ruff` and fix linting issues in modified files
- [ ] T036 [P] Run `uv run pytest` and fix failing tests
- [ ] T037 Update changelog/commit message template with feature entry in `CHANGELOG.md`
- [ ] T038 [P] Verify `uv.lock` is up-to-date and commit changes
- [ ] T039 [P] Final manual accessibility review checklist in `docs/accessibility.md`

---

## Dependencies & Execution Order

- Phase 1 (Setup) tasks T001-T005: can start immediately
- Phase 2 (Foundational) tasks T006-T011: BLOCKS all user story implementation
- User Stories (Phase 3+) tasks may start only after T006-T011 complete
- Suggested execution order for MVP: Complete T001-T011 → T012-T018 (US1) → Validate → then T019-T025 (US2) → then T026-T032 (US3)

### Dependency graph (story completion order)

- Foundation (T006-T011) → US1 (T012-T018)
- Foundation (T006-T011) → US2 (T019-T025)
- Foundation (T006-T011) → US3 (T026-T032)

**Note**: US1 and US2 are both P1 and can be worked on in parallel after Foundation, but US1 is recommended as MVP.

---

## Parallel execution examples

- Example: Parallelize test creation and model implementation for US1

```bash
# Create unit test and integration test in parallel
# Task: create tests/unit/test_keybindings.py and tests/integration/test_tui_navigation.py
```

- Example: Once Foundation is done, developers can be split:

```bash
# Developer A: implement KeyBindingManager and wire UI (T014,T015,T016)
# Developer B: implement toggle flow and tasks API (T021,T022,T023,T024)
# Developer C: implement accessibility and conflicts (T028,T029,T030)
```

---

## Implementation Strategy

- MVP First: Focus on User Story 1 (navigation) as the smallest independent increment that delivers visible value. Complete Foundation and US1 first, run tests, demo.
- Incremental delivery: After MVP, implement US2 (toggle) then US3 (conflicts/accessibility).
- TDD: For each story, write tests first (unit then integration), ensure they FAIL, implement code, then ensure they PASS.

---

## Notes & Validation

- All tasks follow the required checklist format with sequential IDs, `[P]` when parallelizable, story labels for story phases, and include exact file paths.
- Tests are included per the project's TDD requirement (constitution) and FR-010 in spec.md.

(End of tasks)
