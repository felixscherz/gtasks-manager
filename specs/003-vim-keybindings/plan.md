# Implementation Plan: VIM Keybindings for TUI Task List

**Branch**: `003-vim-keybindings` | **Date**: 2025-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-vim-keybindings/spec.md`

## Summary

Add VIM-style navigation (j/k keys) and ENTER key toggle functionality to the TUI task list, maintaining backward compatibility with arrow keys. The implementation will leverage existing Textual framework features and follow the project's TDD and architectural principles.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Textual 0.47+ (TUI framework), pytest 7.4.0+, pytest-asyncio 0.21.0+ (testing)
**Storage**: Google Tasks API (external), task_cache.py (local JSON caching)
**Testing**: pytest with pytest-asyncio for async TUI testing
**Target Platform**: Terminal (CLI/TUI application)
**Project Type**: single (CLI + TUI application)
**Performance Goals**: UI responsiveness (<100ms for key press response), no blocking I/O operations
**Constraints**: Must use background workers for I/O operations, maintain backward compatibility with arrow keys
**Scale/Scope**: Individual task management, typical task list size 10-100 items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Design & Test Strategy
- ✅ PASS: Spec has clear requirements and testable acceptance criteria
- ✅ PASS: Testing approach defined (pytest + pytest-asyncio with Textual Pilot API)
- ✅ PASS: Data model requirements are clear from FR and key entities

### Gate 2: CI/CD Compliance
- ✅ PASS: Project uses pytest for testing (constitution requirement)
- ✅ PASS: Project uses ruff for linting (constitution requirement)
- ⚠️ NOTE: No type checking tool explicitly configured (mypy) - will need to add if constitution requires strict type checking

### Gate 3: Security
- ✅ PASS: No secrets or tokens introduced in this feature
- ✅ PASS: Feature operates on UI state, no credential handling

**Gate Status**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/003-vim-keybindings/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Not needed (no external APIs)
```

### Source Code (repository root)

```text
# Existing structure (hexagonal architecture)
src/
└── gtasks_manager/
    ├── core/
    │   ├── models.py       # Task, TaskList, TaskStatus, UIFocus, UIFocusPane (EXISTING)
    │   ├── services.py    # TaskService (EXISTING)
    │   └── ports.py       # ITaskAdapter port (EXISTING)
    ├── adapters/
    │   └── google_tasks.py # GoogleTasksAdapter (EXISTING)
    ├── tui/
    │   ├── app.py         # TasksApp with key handling (MODIFY)
    │   ├── keybindings.py  # KeyBindingManager (EXISTING - needs enhancement)
    │   └── widgets.py     # TUI widgets (EXISTING)
    └── cli/
        └── cli.py         # CLI commands (EXISTING - unchanged)

tests/
├── unit/
│   └── test_keybindings.py   # Unit tests for KeyBindingManager (ENHANCE)
└── integration/
    └── test_tui_navigation.py # Integration tests for TUI navigation (ENHANCE)
```

**Structure Decision**: Using existing single-project structure with hexagonal architecture. TUI code remains in `tui/` directory following project conventions. KeyBindingManager already exists but needs enhancement to integrate with TasksApp.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No violations present

---

## Phase 0: Research & Technical Decisions

### Research Topics

1. **Textual Key Event Handling**
   - How to capture 'j', 'k', and 'enter' keys in Textual App
   - How to bind keys to actions in Textual BINDINGS list
   - How to handle key events in Textual widget classes

2. **Textual ListView Navigation**
   - How to programmatically move selection in ListView widget
   - How to get and set ListView.index
   - How to detect boundary conditions (top/bottom of list)

3. **Textual Testing with Pilot API**
   - How to use `app.run_test()` to create headless test environment
   - How to use `pilot.press()` to simulate key presses
   - How to assert on app state after key presses
   - Best practices for async test setup and teardown

4. **Background Worker Integration**
   - How to use `@work` decorator for async task toggle operations
   - How to handle optimistic UI updates with rollback on API failure
   - How to prevent UI blocking during API calls

5. **Visual Feedback in Textual**
   - How to highlight selected task in ListView
   - How to update task status display (○ vs ✓) after toggle
   - How to ensure visual updates are reactive

### Research Findings

#### Textual Key Event Handling
- **Decision**: Use Textual's BINDINGS list in App class to map keys to action methods
- **Rationale**: This is the Textual-recommended pattern for keyboard shortcuts, aligns with existing code structure
- **Implementation**: Add ("j", "move_down", "Move down"), ("k", "move_up", "Move up"), ("enter", "toggle_task", "Toggle task") to BINDINGS

#### Textual ListView Navigation
- **Decision**: Use ListView.index property to get/set current selection, with boundary checking
- **Rationale**: ListView provides built-in selection tracking; existing code already uses this pattern
- **Implementation**: Check index against list bounds (0 to len(tasks)-1) before updating

#### Textual Testing with Pilot API
- **Decision**: Use pytest-asyncio with `@pytest.mark.asyncio` decorator and `app.run_test()` context manager
- **Rationale**: Textual is async; Pilot API is the official testing mechanism; matches existing test patterns
- **Implementation**: Follow pattern from test_tui_navigation.py and Textual documentation

#### Background Worker Integration
- **Decision**: Use `@work` decorator for API calls during task toggle, with optimistic UI updates
- **Rationale**: Prevents UI blocking; matches constitution requirement for offloading I/O to background workers
- **Implementation**: Immediate UI update + background persist call with rollback on failure (pattern from app.py)

#### Visual Feedback in Textual
- **Decision**: Use reactive attributes (tasks, task status) with watch methods to trigger UI updates
- **Rationale**: Textual's reactivity system automatically updates UI when data changes; matches existing app.py pattern
- **Implementation**: tasks reactive attribute triggers watch_tasks() to rebuild ListView

## Phase 1: Design & Contracts

### Data Model

#### Core Entities (from spec)

```python
# Task (EXISTING in models.py - no changes needed)
class Task:
    id: str
    title: str
    status: TaskStatus  # NEEDS_ACTION or COMPLETED
    list_id: str
    updated: Optional[datetime]

# TaskStatus (EXISTING enum - no changes needed)
class TaskStatus(Enum):
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"

# UIFocus (EXISTING in models.py - no changes needed)
class UIFocus:
    pane: UIFocusPane  # TASK_LIST or SIDEBAR
    index: Optional[int]  # Current selection index in list
```

#### Selection State (Existing in app.py)

The TasksApp class already has reactive attributes for managing state:
- `tasks: reactive[List[Task]]` - List of tasks displayed in TUI
- `vim_enabled: reactive[bool]` - Whether VIM bindings are enabled
- `ui_focus` - Tracks current selection state

#### State Transitions

**Task Toggle Transition**:
```
NEEDS_ACTION --[ENTER]--> COMPLETED (optimistic update)
    ^                          |
    |                          v
COMPLETED --[ENTER]--> NEEDS_ACTION (optimistic update)
```

On API failure, revert to previous state (implemented in app.py:179-198).

**Navigation Transitions**:
```
Selection index i --[j]--> i+1 (if i < len(tasks) - 1)
Selection index i --[k]--> i-1 (if i > 0)
```

### API Contracts

No external API contracts required. This feature operates on:
1. **TaskService** (existing) - `list_tasks()`, `toggle_task_completion()`
2. **KeyBindingManager** (existing) - `get_action()`, `is_enabled()`

### Test Strategy

#### Test Structure

```text
tests/
├── unit/
│   └── test_keybindings.py          # ENHANCE: Add tests for KeyBindingManager
└── integration/
    └── test_tui_navigation.py       # ENHANCE: Add comprehensive VIM navigation tests
```

#### Unit Tests (test_keybindings.py)

**Test Cases**:
1. `test_get_action_returns_mapped_action()` - Verify j/k/enter map to correct actions
2. `test_get_action_returns_none_when_disabled()` - Verify disabled state
3. `test_get_action_returns_none_for_unknown_key()` - Verify unmapped keys return None
4. `test_update_mapping_adds_new_binding()` - Verify custom key mappings work
5. `test_remove_mapping_deletes_binding()` - Verify key unbinding works

#### Integration Tests (test_tui_navigation.py)

**Test Cases** (EXISTING tests verify basic functionality):

1. `test_j_key_moves_selection_down()` - Press 'j', verify index increments
2. `test_k_key_moves_selection_up()` - Press 'k', verify index decrements
3. `test_j_key_respects_list_boundaries()` - Verify 'j' doesn't go past last item
4. `test_k_key_respects_list_boundaries()` - Verify 'k' doesn't go past first item
5. `test_h_key_moves_focus_left()` - Press 'h', verify focus moves to sidebar
6. `test_l_key_moves_focus_right()` - Press 'l', verify focus moves to task list

**Additional Test Cases to Add**:

7. `test_enter_key_toggles_task_completion()` - Press ENTER, verify status changes
8. `test_enter_key_toggles_task_back()` - Press ENTER twice, verify status reverts
9. `test_enter_key_does_nothing_when_no_selection()` - Press ENTER with no task selected
10. `test_arrow_keys_still_work_with_vim_enabled()` - Verify backward compatibility
11. `test_rapid_key_presses_handled_correctly()` - Verify multiple presses don't break state
12. `test_empty_task_list_handles_key_presses()` - Verify graceful handling of empty list

#### Test Implementation Pattern (from Textual docs)

```python
@pytest.mark.asyncio
async def test_j_key_moves_selection_down(app):
    """Test pressing 'j' moves selection down."""
    async with app.run_test() as pilot:
        await pilot.pause()
        app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
        await pilot.press("j")
        assert app.ui_focus.index == 1
```

### Quickstart Guide

#### Development Workflow

1. **Setup Environment**:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py -v
   ```

2. **Run Specific Test**:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py::test_j_key_moves_selection_down -v
   ```

3. **Run All TUI Tests**:
   ```bash
   uv run pytest tests/ -k "tui or keybindings" -v
   ```

4. **Linting**:
   ```bash
   uv run ruff check src/gtasks_manager/tui/
   ```

5. **Formatting**:
   ```bash
   uv run ruff format src/gtasks_manager/tui/
   ```

#### Running the TUI

```bash
# Run TUI with VIM bindings enabled (default)
uv run gtasks tui

# Navigation:
# - j or down arrow: move selection down
# - k or up arrow: move selection up
# - enter: toggle task completion
# - q: quit
```

#### Testing Keybindings Manually

```bash
# Start TUI
uv run gtasks tui

# Test navigation:
# 1. Press 'j' - selection should move down
# 2. Press 'k' - selection should move up
# 3. Press 'enter' - task should toggle between ○ and ✓
# 4. Test boundary conditions (top/bottom of list)
# 5. Test arrow keys still work
```

## Phase 1 Completion: Architecture Review

### Post-Design Constitution Check

✅ **Gate 1 (Design & Test Strategy)**: PASSED
- Clear data model defined
- Comprehensive test strategy with unit and integration tests
- Test-first approach documented in quickstart

✅ **Gate 2 (CI/CD Compliance)**: PASSED
- Using pytest (constitution requirement)
- Tests use pytest-asyncio for async TUI testing (constitution requirement)
- Linting with ruff documented (constitution requirement)
- Code follows hexagonal architecture (constitution requirement)

✅ **Gate 3 (Security)**: PASSED
- No credential handling
- No secrets introduced
- Feature operates on UI state only

**ALL GATES PASSED - Ready for Phase 2 Implementation**

### Key Technical Decisions Summary

1. **Textual BINDINGS list** for key-to-action mapping (framework best practice)
2. **ListView.index** for selection management with boundary checking
3. **Pilot API** for testing (official Textual testing mechanism)
4. **@work decorator** for background I/O operations (constitution requirement)
5. **Reactive attributes** for UI state updates (Textual best practice)
6. **Optimistic updates with rollback** for task toggle (existing pattern)

### Remaining Open Questions

None - all technical decisions resolved in Phase 0 and Phase 1.

---

## Notes

1. **Existing Code**: The TasksApp already has some VIM keybinding infrastructure in place (j/k/h/l/enter bindings), but integration with actual key event handling may need verification and enhancement.

2. **Backward Compatibility**: Arrow keys must continue working alongside VIM keys. This is enforced by test case `test_arrow_keys_still_work_with_vim_enabled()`.

3. **Error Handling**: Task toggle failures should revert the UI state (optimistic update pattern). The existing `_persist_toggle()` and `_revert_toggle()` methods in app.py handle this.

4. **Performance**: All I/O operations (task toggle, list refresh) use the `@work` decorator to prevent UI blocking, satisfying the constitution requirement.

5. **Testing Coverage**: New tests ensure 100% coverage of VIM navigation and toggle functionality, meeting the constitution's 90%+ coverage goal for core code.

6. **Type Safety**: All new code will use strict type hints as required by the constitution (Python 3.11+).

7. **Linting/Formatting**: Code will be checked with `ruff` before committing, satisfying constitution requirements.
