# Data Model: VIM Keybindings for TUI Task List

**Feature**: 003-vim-keybindings
**Date**: 2025-01-11

## Overview

This document describes the data model for VIM keybindings functionality. The feature primarily operates on existing data structures without requiring new entities. The main additions are:
1. Selection state tracking (already exists in UIFocus)
2. Key action mappings (already exists in KeyBindingManager)
3. UI state for VIM mode (already exists in TasksApp.vim_enabled)

## Core Entities

### Task

**Status**: EXISTING (no changes required)
**Location**: `src/gtasks_manager/core/models.py`

Represents a single todo item in Google Tasks.

```python
class Task(BaseModel):
    """A single task in Google Tasks."""
    id: str
    title: str
    status: TaskStatus  # NEEDS_ACTION or COMPLETED
    list_id: str
    updated: Optional[datetime]
    notes: Optional[str] = None
    due: Optional[str] = None
```

**Key Fields for VIM Keybindings**:
- `id`: Unique identifier used to identify selected task for toggle
- `status`: Displayed as ○ (NEEDS_ACTION) or ✓ (COMPLETED) in TUI
- `title`: Displayed in ListView alongside status indicator

**State Transitions**:
```
NEEDS_ACTION --[ENTER]--> COMPLETED
    ^                          |
    |                          v
COMPLETED --[ENTER]--> NEEDS_ACTION
```

**Validation**:
- Status must be one of TaskStatus enum values
- ID is required and non-empty

---

### TaskStatus

**Status**: EXISTING (no changes required)
**Location**: `src/gtasks_manager/core/models.py`

Enumeration of task completion states.

```python
class TaskStatus(str, Enum):
    """Task completion status."""
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"
```

**Usage**:
- Controls visual indicator in TUI (○ vs ✓)
- Used to toggle task state on ENTER key press

---

### TaskList

**Status**: EXISTING (no changes required)
**Location**: `src/gtasks_manager/core/models.py`

Represents a collection of tasks (Google Tasks list).

```python
class TaskList(BaseModel):
    """A task list in Google Tasks."""
    id: str
    title: str
    updated: Optional[datetime]
```

**Relevance to Feature**:
- Tasks belong to a TaskList
- TUI displays tasks from a single TaskList at a time

---

### UIFocusPane

**Status**: EXISTING (no changes required)
**Location**: `src/gtasks_manager/core/models.py`

Enumeration of UI focus areas.

```python
class UIFocusPane(str, Enum):
    """UI focus pane."""
    SIDEBAR = "sidebar"
    TASK_LIST = "task_list"
```

**Relevance to Feature**:
- VIM navigation (h/l keys) moves focus between SIDEBAR and TASK_LIST
- Selection navigation (j/k keys) only works when focus is on TASK_LIST

---

### UIFocus

**Status**: EXISTING (no changes required)
**Location**: `src/gtasks_manager/core/models.py`

Tracks current UI focus state.

```python
class UIFocus(BaseModel):
    """UI focus state."""
    pane: UIFocusPane  # Currently focused pane
    index: Optional[int]  # Currently selected item index in focused pane
```

**Key Fields for VIM Keybindings**:
- `pane`: Determines which key mappings are active
- `index`: Current selection index in task list (0 to len(tasks)-1)

**State Transitions for Navigation**:
```
index: i --[j or down arrow]--> i+1 (if i < len(tasks) - 1)
index: i --[k or up arrow]--> i-1 (if i > 0)
```

**Boundary Conditions**:
- When index is 0: pressing 'k' has no effect
- When index is len(tasks) - 1: pressing 'j' has no effect
- When tasks list is empty: navigation keys have no effect

---

## KeyBindingManager

**Status**: EXISTING (may need minor enhancements)
**Location**: `src/gtasks_manager/tui/keybindings.py`

Manages VIM-style key mappings for the TUI.

```python
class KeyBindingManager:
    """Manages VIM-style keybindings for the TUI."""

    DEFAULT_MAPPINGS: dict[str, str] = {
        "j": "move_down",
        "k": "move_up",
        "h": "move_left",
        "l": "move_right",
        "enter": "toggle_completion",
    }

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.mappings: dict[str, str] = self.DEFAULT_MAPPINGS.copy()

    def get_action(self, key: str) -> str | None:
        """Get the action associated with a key."""
        if not self.enabled:
            return None
        return self.mappings.get(key)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable VIM bindings."""
        self.enabled = enabled

    def is_enabled(self) -> bool:
        """Check if VIM bindings are currently enabled."""
        return self.enabled

    def update_mapping(self, key: str, action: str) -> None:
        """Update or add a key mapping."""
        self.mappings[key] = action

    def remove_mapping(self, key: str) -> bool:
        """Remove a key mapping."""
        if key in self.mappings:
            del self.mappings[key]
            return True
        return False
```

**Key Fields**:
- `enabled`: Boolean flag to enable/disable VIM keybindings
- `mappings`: Dictionary mapping keys to action names

**Default Mappings**:
- `j` → "move_down": Navigate down in task list
- `k` → "move_up": Navigate up in task list
- `h` → "move_left": Move focus to left pane (sidebar)
- `l` → "move_right": Move focus to right pane (task list)
- `enter` → "toggle_completion": Toggle selected task completion

**Validation**:
- Keys are case-sensitive (lowercase only for VIM keys)
- Actions must be valid method names in TasksApp (prefixed with "action_")
- Unknown keys return None from `get_action()`

---

## TasksApp State

**Status**: EXISTING (no new fields required)
**Location**: `src/gtasks_manager/tui/app.py`

The main TUI application class with reactive attributes for state management.

```python
class TasksApp(App):
    """A Textual app for managing Google Tasks."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("enter", "toggle_task", "Toggle task"),
    ]

    tasks: reactive[List[Task]] = reactive([])
    task_lists: reactive[List[TaskList]] = reactive([])
    current_list_id: reactive[str] = reactive("@default")
    loading_state: reactive[bool] = reactive(False)
    vim_enabled: reactive[bool] = reactive(True)
```

**Reactive Attributes for VIM Keybindings**:

1. **tasks**: List of tasks displayed in TUI
   - Type: `List[Task]`
   - Reactivity: Triggers `watch_tasks()` when changed
   - Usage: Rebuilds ListView when tasks change

2. **vim_enabled**: Whether VIM keybindings are active
   - Type: `bool`
   - Reactivity: Triggers `watch_vim_enabled()` when changed
   - Usage: Updates KeyBindingManager.enabled and displays [VIM] indicator

3. **selected_task_id**: (implicit, tracked via UIFocus)
   - Type: `Optional[str]`
   - Usage: Identifies task for ENTER toggle operation

**Action Methods** (must be defined in TasksApp):
- `action_move_down()`: Handle 'j' key or down arrow
- `action_move_up()`: Handle 'k' key or up arrow
- `action_toggle_completion()`: Handle 'enter' key
- `action_move_left()`: Handle 'h' key (focus sidebar)
- `action_move_right()`: Handle 'l' key (focus task list)

---

## Data Flow

### Navigation Flow

```
User presses 'j' key
    ↓
Textual BINDINGS maps 'j' → "action_move_down"
    ↓
TasksApp.action_move_down() is called
    ↓
Updates app.ui_focus.index (if not at bottom)
    ↓
watch_tasks() or manual update refreshes ListView
    ↓
ListView highlights new selected task
```

### Toggle Flow

```
User presses ENTER key
    ↓
Textual BINDINGS maps 'enter' → "action_toggle_task"
    ↓
TasksApp.action_toggle_task() is called
    ↓
Get selected task (via selected_task_id)
    ↓
Toggle task.status (NEEDS_ACTION ↔ COMPLETED)
    ↓
Optimistic UI update: watch_tasks() refreshes ListView
    ↓
Background worker: @work _persist_toggle() calls API
    ↓
If API fails: revert to old_status
```

---

## Relationships

```
TaskList 1--* Task
         |
         +--* (displayed in TasksApp.tasks)

UIFocus
    ├─→ UIFocusPane (TASK_LIST or SIDEBAR)
    └─→ index (selection index in current pane)

TasksApp
    ├─→ tasks: List[Task] (reactive)
    ├─→ vim_enabled: bool (reactive)
    └─→ ui_focus: UIFocus (selection state)

KeyBindingManager
    ├─→ enabled: bool
    └─→ mappings: dict[str, str]
```

---

## Invariants

1. **Task Index Validity**: `ui_focus.index` must satisfy `0 <= index < len(tasks)` or be `None`
2. **Task Status**: Every task must have a valid TaskStatus enum value
3. **Selection Consistency**: When `ui_focus.pane == TASK_LIST`, `ui_focus.index` should point to a valid task
4. **VIM Mappings**: All keys in `KeyBindingManager.mappings` must have corresponding action methods in TasksApp
5. **Optimistic Updates**: When task.status changes in UI, pending API updates must be tracked for potential rollback

---

## Edge Cases

### Empty Task List

- `tasks` is empty: `[]`
- `ui_focus.index` should be `None` or 0 (no selection)
- Navigation keys (j/k) should have no effect
- ENTER key should have no effect (no task to toggle)

### No Selection

- `ui_focus.index` is `None`
- ENTER key should have no effect
- Navigation should be allowed (if tasks exist)

### API Failure During Toggle

- Task status is toggled optimistically in UI
- Background API call fails
- Task status must revert to previous value
- UI should display error message or visual indicator of failure

### Boundary Navigation

- At index 0: pressing 'k' or up arrow has no effect
- At index len(tasks) - 1: pressing 'j' or down arrow has no effect
- Selection should remain at current position

---

## Validation Rules

1. **Task Status Validation**:
   - Status must be `TaskStatus.NEEDS_ACTION` or `TaskStatus.COMPLETED`
   - Invalid status values should raise ValidationError

2. **Index Validation**:
   - When setting `ui_focus.index`, must check `0 <= index < len(tasks)`
   - Out-of-bounds values should be clamped or ignored

3. **Key Validation**:
   - Keys in KeyBindingManager.mappings must be lowercase
   - Actions must be valid method names starting with "action_"

4. **Focus Validation**:
   - When `ui_focus.pane` is SIDEBAR, navigation keys (j/k) should not affect task list
   - Only TASK_LIST pane should respond to j/k keys

---

## Summary

This feature primarily uses existing data structures without requiring new entities. The core enhancements are:

1. **Integration**: Connect KeyBindingManager to TasksApp's BINDINGS list
2. **Selection Tracking**: Use existing UIFocus for navigation state
3. **Reactive Updates**: Leverage existing reactive attributes for UI updates
4. **Error Handling**: Use existing optimistic update pattern with rollback

No new database tables, API endpoints, or external services are required. The feature operates entirely within the TUI layer using existing domain models.
