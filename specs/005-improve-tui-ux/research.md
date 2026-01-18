# Research & Design Decisions

**Feature**: Improve TUI UX
**Date**: 2026-01-17
**Phase**: Phase 0 - Research Complete

## Research Topics

### 1. Click CLI: Detecting Empty Invocation

**Question**: How to detect when Click CLI is executed without any subcommand or arguments?

**Decision**: Use Click's `invoke_without_command` decorator on the main group, combined with checking if `ctx.invoked_subcommand` is `None`.

**Rationale**:
- Click provides built-in support for this pattern via `@main.group(invoke_without_command=True)`
- When invoked without subcommand, `ctx.invoked_subcommand` will be `None`
- This allows the default function to run and trigger the TUI
- Maintains backward compatibility with `gtasks gui` subcommand

**Alternatives Considered**:
1. Custom argument parsing (rejected: breaks Click's decorator-based design)
2. Shell alias (rejected: doesn't work for all users/platforms)
3. Separate entry point (rejected: adds complexity)

**Implementation Pattern**:
```python
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Google Tasks Manager CLI"""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, launch TUI
        from .tui.app import launch_tui
        launch_tui()
```

### 2. Textual: Preserving Selection Across State Changes

**Question**: How to maintain selection on the same task after toggling its completion state in Textual?

**Decision**: Use a combination of reactive attributes and task ID tracking rather than list index tracking.

**Rationale**:
- Task positions may change due to sorting after state change
- Task IDs are stable identifiers that don't change
- Textual's `watch_*` methods can react to data changes
- Selection can be restored by task ID after list refresh

**Alternatives Considered**:
1. Track list index (rejected: index changes when tasks are sorted/moved)
2. Freeze list during toggle (rejected: prevents sorting updates)
3. No selection preservation (rejected: poor UX, creates user frustration)

**Implementation Pattern**:
```python
class TaskListWidget(Static):
    selected_task_id = reactive(str)

    def watch_selected_task_id(self, old_id, new_id):
        """Restore selection by task ID after list updates"""
        if new_id:
            # Find and highlight the task with matching ID
            for index, task in enumerate(self.tasks):
                if task['id'] == new_id:
                    self.task_list.highlighted = index
                    self.task_list.scroll_to_highlight()
                    break
```

### 3. Google Tasks API: Fetching Task List Metadata

**Question**: How to retrieve the name of the current task list from Google Tasks API?

**Decision**: Use `service.tasklists().get(tasklist=task_list_id)` to fetch list metadata separately or include in task list response.

**Rationale**:
- Google Tasks API provides separate endpoint for task list metadata
- Task list responses include title field
- Should cache the list name to avoid repeated API calls
- Fallback to "Default List" if API fails

**Alternatives Considered**:
1. Parse from URL/hash (rejected: unreliable, API structure may change)
2. Store in separate local cache (rejected: adds complexity, risk of stale data)
3. Only show list ID (rejected: poor UX, not user-friendly)

**Implementation Pattern**:
```python
def get_task_list_name(self, task_list_id: str) -> str:
    """Fetch task list name from API"""
    try:
        result = self.service.tasklists().get(
            tasklist=task_list_id
        ).execute()
        return result.get('title', 'Default List')
    except HttpError as error:
        print(f'Error fetching list name: {error}')
        return 'Default List'
```

### 4. Textual: Handling Task Position Changes After Sorting

**Question**: How to handle selection when tasks change position after toggling state in a sorted list?

**Decision**: Selection follows the task by ID, not by index. Use task ID to re-locate task after list refresh.

**Rationale**:
- Tasks may move to different positions due to sorting criteria
- User expects to stay focused on the same task they interacted with
- Task ID provides stable reference point
- Textual can scroll to the task's new position automatically

**Alternatives Considered**:
1. Keep selection at original index (rejected: selects different task)
2. Clear selection after toggle (rejected: user loses context)
3. Prevent sorting during TUI session (rejected: limits functionality)

**Implementation Pattern**:
```python
async def toggle_task_state(self, task_id: str):
    """Toggle task completion state and preserve selection"""
    # Store current task ID before state change
    current_id = self.selected_task_id

    # Toggle task state (API call in background worker)
    await self._toggle_task_async(task_id)

    # Refresh task list (may cause re-sorting)
    await self.refresh_tasks()

    # Restore selection by task ID (follows task to new position)
    self.selected_task_id = current_id
```

### 5. Textual: Header Widget for Dynamic List Name

**Question**: How to display the task list name in the TUI header area with dynamic updates?

**Decision**: Create a custom `Static` widget in the header with a reactive attribute for the list name.

**Rationale**:
- Textual's `Static` widget is suitable for simple text display
- Reactive attributes trigger automatic UI updates when value changes
- Header is a natural place for context information
- Can truncate long names using Textual's built-in text overflow handling

**Alternatives Considered**:
1. Use Label widget (rejected: unnecessary overhead for static text)
2. Use Header widget (rejected: meant for app title, not dynamic data)
3. Show in footer (rejected: less visible, harder to scan)

**Implementation Pattern**:
```python
class ListNameDisplay(Static):
    """Displays current task list name in header"""
    list_name = reactive(str)

    def watch_list_name(self, old_name, new_name):
        """Update display when list name changes"""
        # Truncate if too long (e.g., max 50 chars)
        display_name = new_name[:47] + '...' if len(new_name) > 50 else new_name
        self.update(f"List: {display_name}")
```

## Technology Choices

### Python 3.11+ with Strict Type Hinting
- Required by constitution
- All function signatures will have type hints
- Complex data structures will use `typing` module (`Optional`, `List`, `Dict`)

### Click 8.0+ for CLI
- Existing framework in codebase
- `invoke_without_command` for default behavior
- Backward compatible with `gtasks gui`

### Textual 0.47+ for TUI
- Existing framework in codebase
- Reactive attributes for state management
- `@work` decorator for non-blocking API calls
- Message passing for inter-widget communication

### pytest + pytest-asyncio for Testing
- Required by constitution
- Unit tests for CLI detection logic
- Integration tests for TUI flow
- Async tests for TUI widget behavior

## Architecture Decisions

### Hexagonal Architecture Compliance
- Core domain logic remains in existing `src/gtasks_manager/`
- TUI components in new `src/gtasks_manager/tui/` subpackage
- CLI modifications in `src/gtasks_manager/cli.py` (existing)
- No circular dependencies between core and TUI/CLI

### State Management Pattern
- TUI state tracked in `tui/state.py` module
- Selection state preserved across UI updates
- Task list metadata cached locally
- Reactive patterns for automatic UI updates

### Error Handling Strategy
- API errors logged but don't crash TUI
- Fallback values for missing metadata (e.g., "Default List")
- User-friendly error messages in CLI
- Graceful degradation when offline

## Performance Considerations

- Task list name fetched once per TUI session (not per refresh)
- Selection restoration uses O(n) scan for task ID (acceptable for typical list sizes)
- API calls in background workers to prevent UI blocking
- Local cache for task metadata reduces API calls

## Open Questions Resolved

All questions from the specification have been resolved through research and analysis. No remaining technical uncertainties.
