# Research: VIM Keybindings for TUI Task List

**Feature**: 003-vim-keybindings
**Date**: 2025-01-11

## Research Topics

### 1. Textual Key Event Handling

**Question**: How to capture and handle 'j', 'k', and 'enter' key events in Textual App?

**Investigation**:
- Textual provides a `BINDINGS` class attribute that maps keyboard shortcuts to action methods
- Keys are defined as tuples: `(key, action_name, description)`
- Action methods must be defined as `action_<name>()` in the App class
- The `on_key()` event handler can also be used for more granular key processing

**Decision**: Use Textual's BINDINGS list in App class to map keys to action methods

**Rationale**:
- This is the Textual-recommended pattern for keyboard shortcuts
- Aligns with existing code structure in app.py
- Provides automatic documentation in Footer widget
- Matches existing BINDINGS pattern in the codebase

**Implementation**:
```python
BINDINGS = [
    ("q", "quit", "Quit"),
    ("r", "refresh", "Refresh"),
    ("enter", "toggle_task", "Toggle task"),
    ("j", "move_down", "Move down"),
    ("k", "move_up", "Move up"),
]
```

**Alternatives Considered**:
1. **on_key() event handler**: More complex, requires manual key parsing
2. **KeyBindingManager integration**: Would require additional middleware layer

---

### 2. Textual ListView Navigation

**Question**: How to programmatically move selection in ListView widget and handle boundary conditions?

**Investigation**:
- ListView widget has an `index` property that tracks the currently selected item
- Setting `index` automatically moves the selection and highlights the item
- ListView provides built-in boundary handling (index wraps or clamps based on configuration)
- The existing code uses `list_view.index or 0` to handle None case

**Decision**: Use ListView.index property to get/set current selection, with explicit boundary checking

**Rationale**:
- ListView provides built-in selection tracking
- Existing code already uses this pattern (see app.py:110-126)
- Explicit boundary checking gives us control over behavior (no wrapping)
- Matches spec requirements (FR-003, FR-004)

**Implementation**:
```python
def action_cursor_down(self) -> None:
    """Move cursor down and update selected task."""
    list_view = self.query_one("#task-list-view", ListView)
    if len(self.tasks) > 0:
        current_index = list_view.index or 0
        if current_index < len(self.tasks) - 1:
            list_view.index = current_index + 1
        self._update_selected_task()
```

**Alternatives Considered**:
1. **Built-in cursor navigation**: Less control over boundary behavior
2. **Custom selection tracking**: Duplicates ListView functionality

---

### 3. Textual Testing with Pilot API

**Question**: How to test TUI interactions (key presses, selection changes) using Textual's testing framework?

**Investigation**:
- Textual provides `app.run_test()` method to create headless test environment
- Returns a `Pilot` object that can simulate user interactions
- `pilot.press("key")` simulates keyboard input
- Tests must use `pytest-asyncio` with `@pytest.mark.asyncio` decorator
- `await pilot.pause()` waits for pending messages to be processed
- Tests can directly inspect app state (attributes, reactive values)

**Decision**: Use pytest-asyncio with `@pytest.mark.asyncio` decorator and `app.run_test()` context manager

**Rationale**:
- Textual is async, so async testing is required
- Pilot API is the official Textual testing mechanism
- Matches existing test patterns in test_tui_navigation.py
- Recommended in Textual documentation

**Implementation**:
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

**Best Practices**:
1. Always use `@pytest.mark.asyncio` decorator
2. Use `await pilot.pause()` after setup to let app initialize
3. Test state after each interaction with `assert`
4. Use fixtures for app and mock service setup
5. Test both happy path and edge cases

**Alternatives Considered**:
1. **Manual testing**: Slow, error-prone, not automatable
2. **Snapshot testing**: Good for visual regression but doesn't test logic

---

### 4. Background Worker Integration

**Question**: How to offload I/O operations (task toggle) to background workers to prevent UI blocking?

**Investigation**:
- Textual provides `@work` decorator to run functions in background threads
- Background workers prevent the UI from freezing during I/O operations
- Optimistic updates are recommended: update UI immediately, then persist in background
- On failure, revert UI state to previous value
- The existing code uses this pattern in `_persist_toggle()` and `_revert_toggle()`

**Decision**: Use `@work` decorator for API calls during task toggle, with optimistic UI updates and rollback on failure

**Rationale**:
- Prevents UI blocking (constitution requirement)
- Matches existing pattern in app.py:179-198
- Provides responsive user experience
- Handles API errors gracefully with rollback

**Implementation**:
```python
def _toggle_completion(self) -> None:
    """Toggle completion status of selected task."""
    if not self.selected_task_id:
        return
    task = next((t for t in self.tasks if t.id == self.selected_task_id), None)
    if not task:
        return

    old_status = task.status
    new_status = (
        TaskStatus.COMPLETED
        if old_status == TaskStatus.NEEDS_ACTION
        else TaskStatus.NEEDS_ACTION
    )

    # Optimistic update
    task.status = new_status
    self._persist_toggle(task.id, old_status)

@work
async def _persist_toggle(self, task_id: str, old_status: TaskStatus) -> None:
    """Persist toggle in background with rollback on failure."""
    try:
        success = manager.toggle_task_completion(task_id)
        if not success:
            self._revert_toggle(task_id, old_status)
    except Exception as e:
        self._revert_toggle(task_id, old_status)
```

**Alternatives Considered**:
1. **Synchronous API calls**: Would block UI, violates constitution
2. **No optimistic updates**: Poor user experience, feels laggy

---

### 5. Visual Feedback in Textual

**Question**: How to provide visual feedback when tasks are toggled and when selection changes?

**Investigation**:
- Textual's `reactive` module provides reactive attributes that trigger updates when changed
- Define reactive attributes: `tasks = reactive([])` and `vim_enabled = reactive(True)`
- Implement `watch_<attribute>()` methods to respond to changes
- ListView automatically re-renders when items change
- Task status can be displayed with different visual indicators (○ vs ✓)
- Highlighting is handled automatically by ListView for selected items

**Decision**: Use reactive attributes (tasks, task status) with watch methods to trigger UI updates

**Rationale**:
- Textual's reactivity system automatically updates UI when data changes
- Matches existing pattern in app.py (watch_tasks, watch_loading_state, watch_vim_enabled)
- Declarative and maintainable
- Provides real-time visual feedback

**Implementation**:
```python
tasks: reactive[List[Task]] = reactive([])

def watch_tasks(self, tasks: list[Task]) -> None:
    """Called when tasks change."""
    list_view = self.query_one("#task-list-view", ListView)
    list_view.clear()
    for task in tasks:
        status = "✓" if task.status == TaskStatus.COMPLETED else "○"
        list_view.append(ListItem(Static(f"{status} {task.title}")))
    self._update_selected_task()
```

**Alternatives Considered**:
1. **Manual refresh calls**: Error-prone, requires remembering to call update methods
2. **Reactive ListView**: Textual doesn't support reactive ListView directly

---

## Technical Decisions Summary

| Decision | Rationale | Alternative Rejected |
|-----------|------------|---------------------|
| Textual BINDINGS list | Framework best practice, matches existing code | on_key() event handler (more complex) |
| ListView.index with boundary checking | Existing pattern, explicit control | Built-in navigation (less control) |
| Pilot API for testing | Official mechanism, matches existing tests | Manual testing (slow, not automatable) |
| @work decorator for I/O | Prevents blocking, matches constitution | Synchronous calls (violates constitution) |
| Reactive attributes for UI updates | Textual best practice, matches existing code | Manual refresh (error-prone) |

## Additional Findings

### Existing Code Analysis

1. **KeyBindingManager** (`src/gtasks_manager/tui/keybindings.py`):
   - Already implements VIM key mappings (j, k, h, l, enter)
   - Has `get_action()` method to map keys to actions
   - Not currently integrated with TasksApp's BINDINGS list
   - Can be used as reference or enhanced for better integration

2. **TasksApp** (`src/gtasks_manager/tui/app.py`):
   - Already has some VIM bindings defined in BINDINGS list
   - Has `action_move_down()`, `action_move_up()`, `action_toggle_completion()` methods
   - Implements optimistic updates with `_persist_toggle()` and `_revert_toggle()`
   - Uses reactive attributes for state management
   - Some references to `self.keybinding_manager` (line 84) but this attribute doesn't exist in `__init__`

3. **Existing Tests** (`tests/integration/test_tui_navigation.py`):
   - Already has tests for j/k navigation
   - Tests use Pilot API correctly
   - Test fixtures for mock service and app setup are well-defined
   - Missing tests for ENTER toggle and edge cases

### Integration Strategy

1. **Phase 1: Fix Existing Code**:
   - Add `keybinding_manager` initialization to TasksApp.__init__
   - Verify existing VIM bindings work correctly
   - Ensure KeyBindingManager is properly integrated

2. **Phase 2: Enhance Tests**:
   - Add tests for ENTER toggle functionality
   - Add tests for edge cases (empty list, no selection, boundary conditions)
   - Add tests for backward compatibility (arrow keys)

3. **Phase 3: Documentation**:
   - Document VIM keybindings in app help
   - Update quickstart guide

---

## References

1. [Textual Testing Guide](https://textual.textualize.io/guide/testing/)
2. [Textual App API](https://textual.textualize.io/api/app/)
3. [Textual Widgets API](https://textual.textualize.io/widgets/)
4. [Textual Reactive Module](https://textual.textualize.io/guide/reactivity/)
