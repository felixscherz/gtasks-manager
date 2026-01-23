# TUI Application Contract

**Version**: 1.0
**Feature**: Improve TUI UX
**Date**: 2026-01-17

## Purpose

Defines the interface contract for the TUI application, including initialization, state management, and user interaction handling.

## Interface: TUIApplication

### Responsibilities

- Launch and manage the TUI application
- Display task list with header showing current list name
- Handle user interactions (navigation, task selection, state toggling)
- Preserve task selection across state changes
- Display loading states and error messages

### Methods

#### `launch() -> None`

**Purpose**: Launch the TUI application

**Parameters**: None

**Returns**: None

**Behavior**:
- Initializes TUI with default task list
- Fetches task list metadata (name)
- Displays tasks in list view
- Blocks until TUI is closed

**Errors**:
- Authentication required → Launch authentication flow
- API error → Display error message, fallback to cached data

---

#### `set_list_name(name: str) -> None`

**Purpose**: Update the task list name displayed in the header

**Parameters**:
- `name` (str): Task list name to display

**Returns**: None

**Behavior**:
- Updates header widget with new list name
- Triggers reactive UI update
- Truncates name if exceeds display width (max 50 chars displayed)

**Validation**:
- `name` must be non-empty string
- If `name` is empty or None, display "Default List"

---

#### `set_selection(task_id: str) -> None`

**Purpose**: Set the currently selected task

**Parameters**:
- `task_id` (str): Unique identifier of the task to select

**Returns**: None

**Behavior**:
- Highlights the specified task in the list
- Scrolls to bring selected task into view
- Updates internal selection state

**Validation**:
- `task_id` must be a valid task ID present in the current task list
- If `task_id` not found, clear selection

---

#### `preserve_selection() -> None`

**Purpose**: Mark the current selection for preservation across state changes

**Parameters**: None

**Returns**: None

**Behavior**:
- Stores the current `task_id` in selection state
- Sets `preserved` flag to true
- Stores current timestamp

**Use Case**: Called before task state toggle or list refresh

---

#### `restore_selection() -> None`

**Purpose**: Restore selection to the previously preserved task

**Parameters**: None

**Returns**: None

**Behavior**:
- Retrieves preserved `task_id` from selection state
- Finds task with matching ID in refreshed task list
- Moves highlight to task's current position
- Scrolls to bring task into view
- Clears `preserved` flag

**Edge Cases**:
- If task ID not found in refreshed list → Clear selection
- If no preserved selection → Do nothing

---

#### `set_loading(is_loading: bool) -> None`

**Purpose**: Update the loading state of the TUI

**Parameters**:
- `is_loading` (bool): True if loading, False otherwise

**Returns**: None

**Behavior**:
- Updates loading indicator in UI
- Disables user interactions while loading
- Shows/hides spinner or progress indicator

---

#### `show_error(message: str) -> None`

**Purpose**: Display an error message to the user

**Parameters**:
- `message` (str): Error message to display

**Returns**: None

**Behavior**:
- Displays error message in footer or modal
- Clears error after user dismisses or timeout
- Allows user to continue working

**Validation**:
- `message` must be non-empty string

---

## Events

### TaskSelected

**Emitted when**: User selects a task in the list

**Payload**:
```python
{
    "task_id": str,
    "timestamp": datetime
}
```

**Handlers**: Update selection state, highlight task

---

### TaskToggled

**Emitted when**: User toggles task completion state

**Payload**:
```python
{
    "task_id": str,
    "new_status": str,  # "needsAction" or "completed"
    "preserve_selection": bool
}
```

**Handlers**:
- Preserve selection before toggle
- Call API to update task
- Refresh task list
- Restore selection

---

### ListNameUpdated

**Emitted when**: Task list name changes

**Payload**:
```python
{
    "list_id": str,
    "name": str,
    "is_cached": bool
}
```

**Handlers**: Update header widget with new name

---

### LoadingStateChanged

**Emitted when**: Loading state changes

**Payload**:
```python
{
    "is_loading": bool,
    "operation": str  # e.g., "toggling_task", "refreshing_list"
}
```

**Handlers**: Update loading indicator, enable/disable interactions

---

## Error Handling Contract

### API Errors

**Behavior**:
- Log error with details
- Display user-friendly message in TUI
- Fallback to cached data if available
- Allow user to continue working

**Example Messages**:
- "Failed to update task. Please try again."
- "Unable to load task list name. Using cached data."
- "API error: Connection timed out. Retrying..."

### Validation Errors

**Behavior**:
- Log validation error
- Display specific validation message
- Prevent invalid state transitions

**Example Messages**:
- "Task not found in current list."
- "Invalid task ID format."
- "Task list name is required."

---

## Performance Contract

### Response Time Targets

- TUI launch: < 500ms (after authentication)
- Selection highlight: < 50ms
- List name update: < 100ms
- Selection restoration: < 200ms (for lists up to 1000 tasks)

### Resource Limits

- Memory: < 100MB for typical usage (100 tasks)
- CPU: Minimal during idle, spikes during API calls
- Network: One API call per user action (cached where possible)

---

## Testing Contract

### Unit Tests Required

- `test_launch_initializes_tui_with_default_list`
- `test_set_list_name_updates_header`
- `test_set_selection_highlights_task`
- `test_preserve_selection_stores_task_id`
- `test_restore_selection_moves_highlight_to_correct_index`
- `test_set_loading_toggles_loading_indicator`
- `test_show_error_displays_message`

### Integration Tests Required

- `test_task_toggle_preserves_selection_across_refresh`
- `test_list_name_updates_when_switching_lists`
- `test_api_error_displays_message_and_fallback_to_cache`
- `test_selection_restoration_handles_moved_task_in_sorted_list`

---

## Version History

- 1.0 (2026-01-17): Initial contract for TUI UX improvements
