# TUI Events Contract

**Feature**: Google Tasks CLI and TUI Manager
**Branch**: `001-google-tasks-cli-tui`
**Date**: 2026-01-07

## Purpose

This document defines the event system for the Textual TUI interface, including user actions, system events, state updates, and message passing between widgets.

---

## Event Architecture

The TUI uses Text's native message passing system for communication between components:

```
User Input → Keyboard/Mouse Events → Widget Handlers → Custom Messages → State Updates → UI Refresh
```

**Key Concepts**:
1. **Built-in Events**: Textual's standard events (key press, mouse click, focus, etc.)
2. **Custom Messages**: Application-specific messages for domain events
3. **Reactive Attributes**: Automatic UI updates when state changes
4. **Message Bubbling**: Events propagate up the widget tree unless stopped

---

## Built-in Textual Events

### Keyboard Events

```python
from textual.events import Key

class TaskListView(Static):
    async def on_key(self, event: Key) -> None:
        """Handle all key presses."""
        if event.key == "j":
            self.move_selection_down()
        elif event.key == "k":
            self.move_selection_up()
        elif event.key == "enter":
            self.activate_selected_task()
```

**Common Key Events**:
- `j`, `k`: Navigate up/down (vim-style)
- `arrow_down`, `arrow_up`: Navigate up/down
- `enter`: Activate/select item
- `space`: Toggle completion
- `d`: Delete task
- `r`: Refresh from API
- `?`: Show help
- `q`, `escape`: Quit/cancel

### Mouse Events

```python
from textual.events import Click

async def on_click(self, event: Click) -> None:
    """Handle mouse clicks on task items."""
    self.select_task_at_position(event.y)
```

### Focus Events

```python
from textual.events import Focus, Blur

async def on_focus(self, event: Focus) -> None:
    """Widget gained focus."""
    self.add_class("focused")

async def on_blur(self, event: Blur) -> None:
    """Widget lost focus."""
    self.remove_class("focused")
```

---

## Custom Application Messages

### TaskSelected

Emitted when a task is selected in the list.

```python
from textual.message import Message

class TaskSelected(Message):
    """A task was selected."""

    def __init__(self, task_id: str, task_title: str) -> None:
        self.task_id = task_id
        self.task_title = task_title
        super().__init__()

# Usage in widget
def select_task(self, task: Task) -> None:
    """Select a task and emit event."""
    self.selected_task_id = task.id
    self.post_message(TaskSelected(task.id, task.title))

# Usage in app
async def on_task_selected(self, message: TaskSelected) -> None:
    """Handle task selection."""
    self.status_bar.update(f"Selected: {message.task_title}")
```

### TaskCompleted

Emitted when a task is marked complete.

```python
class TaskCompleted(Message):
    """A task was marked as completed."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__()

# Handler
async def on_task_completed(self, message: TaskCompleted) -> None:
    """Handle task completion."""
    self.loading = True
    try:
        await self.api.complete_task(self.current_list_id, message.task_id)
        await self.refresh_tasks()
        self.notify("Task completed!")
    except APIError as e:
        self.notify(f"Error: {e}", severity="error")
    finally:
        self.loading = False
```

### TaskDeleted

Emitted when a task is deleted.

```python
class TaskDeleted(Message):
    """A task was deleted."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__()
```

### TaskCreated

Emitted when a new task is created.

```python
class TaskCreated(Message):
    """A new task was created."""

    def __init__(self, title: str, notes: Optional[str] = None, due: Optional[datetime] = None) -> None:
        self.title = title
        self.notes = notes
        self.due = due
        super().__init__()
```

### TaskUpdated

Emitted when a task is updated.

```python
class TaskUpdated(Message):
    """A task was updated."""

    def __init__(self, task_id: str, updates: dict) -> None:
        self.task_id = task_id
        self.updates = updates
        super().__init__()
```

### RefreshRequested

Emitted when user requests data refresh from API.

```python
class RefreshRequested(Message):
    """User requested data refresh."""

    def __init__(self) -> None:
        super().__init__()

# Handler
async def on_refresh_requested(self, message: RefreshRequested) -> None:
    """Refresh tasks from API."""
    await self.load_tasks()
```

### ErrorOccurred

Emitted when an error occurs that should be shown to the user.

```python
class ErrorOccurred(Message):
    """An error occurred."""

    def __init__(self, error_message: str, error_type: str = "error") -> None:
        self.error_message = error_message
        self.error_type = error_type  # "error", "warning", "info"
        super().__init__()

# Handler
async def on_error_occurred(self, message: ErrorOccurred) -> None:
    """Display error to user."""
    self.notify(message.error_message, severity=message.error_type)
```

---

## State Management with Reactive Attributes

The TUI uses Textual's reactive system for automatic UI updates:

```python
from textual.reactive import reactive

class TasksApp(App):
    """Main TUI application."""

    # Reactive state - UI auto-updates when these change
    tasks = reactive(list, init=False)
    selected_task_index = reactive(0)
    loading = reactive(False)
    current_list_id = reactive("")
    current_list_name = reactive("My Tasks")

    def watch_tasks(self, old_value: list, new_value: list) -> None:
        """Called automatically when tasks change."""
        # Update task list widget
        task_list = self.query_one("#task-list", TaskListWidget)
        task_list.update_tasks(new_value)

    def watch_loading(self, old_value: bool, new_value: bool) -> None:
        """Called when loading state changes."""
        if new_value:
            self.query_one("#loading-indicator").display = True
        else:
            self.query_one("#loading-indicator").display = False

    def watch_selected_task_index(self, old_value: int, new_value: int) -> None:
        """Called when selection changes."""
        task_list = self.query_one("#task-list", TaskListWidget)
        task_list.highlight_index(new_value)
```

**Reactive Patterns**:
- `reactive(type)`: Standard reactive attribute
- `reactive(type, init=False)`: Don't set initial value in __init__
- `watch_{attribute_name}()`: Called when attribute changes
- `compute_{attribute_name}()`: Compute derived values

---

## Async Operations with Workers

For background operations (API calls), use Textual's Workers:

```python
from textual import work
from textual.worker import Worker, WorkerState

class TasksApp(App):
    @work(thread=False)  # Async worker for I/O
    async def load_tasks(self) -> None:
        """Load tasks from API (background worker)."""
        try:
            tasks = await self.api.list_tasks(
                self.current_list_id,
                show_completed=False
            )
            self.tasks = tasks  # Triggers watch_tasks()
        except APIError as e:
            self.post_message(ErrorOccurred(str(e)))

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker.name == "load_tasks":
            if event.state == WorkerState.RUNNING:
                self.loading = True
            elif event.state == WorkerState.SUCCESS:
                self.loading = False
            elif event.state == WorkerState.ERROR:
                self.loading = False
                self.notify(f"Error: {event.worker.error}", severity="error")
```

---

## Widget Communication Patterns

### Parent → Child Communication

```python
# Parent widget
class TasksApp(App):
    def update_task_filter(self, show_completed: bool) -> None:
        """Tell child widget to update filter."""
        task_list = self.query_one("#task-list", TaskListWidget)
        task_list.show_completed = show_completed
```

### Child → Parent Communication

```python
# Child widget
class TaskListWidget(Static):
    def on_item_selected(self, item_index: int) -> None:
        """Notify parent of selection."""
        task = self.tasks[item_index]
        self.post_message(TaskSelected(task.id, task.title))

# Parent handles message
class TasksApp(App):
    async def on_task_selected(self, message: TaskSelected) -> None:
        """Handle child's message."""
        self.selected_task_id = message.task_id
```

### Sibling Widget Communication

```python
# Via parent as mediator
class TasksApp(App):
    async def on_task_selected(self, message: TaskSelected) -> None:
        """Update both task list and detail panel."""
        task_list = self.query_one("#task-list")
        detail_panel = self.query_one("#detail-panel")

        task_list.highlight_task(message.task_id)
        detail_panel.show_task(message.task_id)
```

---

## Screen Navigation Events

```python
from textual.screen import Screen

class HelpScreen(Screen):
    """Help screen."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
    ]

    def action_dismiss(self) -> None:
        """Close help screen."""
        self.app.pop_screen()

# Showing the screen
async def action_show_help(self) -> None:
    """Show help screen."""
    await self.push_screen(HelpScreen())
```

---

## Error Handling Events

### Network Error

```python
class NetworkError(Message):
    """Network connectivity lost."""

    def __init__(self) -> None:
        super().__init__()

async def on_network_error(self, message: NetworkError) -> None:
    """Handle network errors."""
    self.loading = False
    self.notify(
        "No network connection. Check your internet.",
        severity="error",
        timeout=10
    )
```

### Authentication Error

```python
class AuthenticationError(Message):
    """Authentication failed or token expired."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__()

async def on_authentication_error(self, message: AuthenticationError) -> None:
    """Handle auth errors."""
    self.notify(
        f"Authentication failed: {message.reason}. Run 'gtasks auth'.",
        severity="error"
    )
    # Optionally: exit TUI and prompt for auth
    self.exit()
```

---

## Complete Event Flow Example

**Scenario**: User presses 'space' to toggle task completion

```python
# 1. User presses space key
class TaskListWidget(Static):
    async def on_key(self, event: Key) -> None:
        if event.key == "space":
            task = self.get_selected_task()
            # 2. Emit custom message
            self.post_message(TaskCompleted(task.id))

# 3. App receives message
class TasksApp(App):
    async def on_task_completed(self, message: TaskCompleted) -> None:
        # 4. Update UI state
        self.loading = True  # Triggers watch_loading()

        try:
            # 5. Call API via worker
            await self.complete_task_worker(message.task_id)
        except APIError as e:
            # 6. Handle error
            self.post_message(ErrorOccurred(str(e)))
        finally:
            # 7. Update UI state
            self.loading = False

    @work
    async def complete_task_worker(self, task_id: str) -> None:
        """Complete task (background)."""
        # API call
        await self.api.complete_task(self.current_list_id, task_id)

        # 8. Refresh task list
        await self.load_tasks()  # Updates self.tasks, triggers watch_tasks()

        # 9. Show success notification
        self.notify("Task completed!", severity="success")
```

---

## Message Catalog

| Message | Emitted By | Handled By | Purpose |
|---------|-----------|------------|---------|
| `TaskSelected` | TaskListWidget | TasksApp | User selected a task |
| `TaskCompleted` | TaskListWidget | TasksApp | Mark task complete |
| `TaskDeleted` | TaskListWidget | TasksApp | Delete a task |
| `TaskCreated` | AddTaskModal | TasksApp | Create new task |
| `TaskUpdated` | EditTaskModal | TasksApp | Update task details |
| `RefreshRequested` | TaskListWidget | TasksApp | Reload from API |
| `ErrorOccurred` | Any | TasksApp | Display error |
| `NetworkError` | APIAdapter | TasksApp | Network failure |
| `AuthenticationError` | APIAdapter | TasksApp | Auth failure |

---

## Keyboard Bindings

```python
from textual.binding import Binding

class TasksApp(App):
    """Main TUI application."""

    BINDINGS = [
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("enter", "select", "Select"),
        Binding("space", "toggle_complete", "Complete"),
        Binding("a", "add_task", "Add"),
        Binding("d", "delete_task", "Delete"),
        Binding("e", "edit_task", "Edit"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def action_move_down(self) -> None:
        """Move selection down."""
        max_index = len(self.tasks) - 1
        self.selected_task_index = min(self.selected_task_index + 1, max_index)

    def action_move_up(self) -> None:
        """Move selection up."""
        self.selected_task_index = max(self.selected_task_index - 1, 0)

    async def action_refresh(self) -> None:
        """Refresh tasks from API."""
        await self.load_tasks()
```

---

## Summary

**Custom Messages**: 9 (TaskSelected, TaskCompleted, TaskDeleted, TaskCreated, TaskUpdated, RefreshRequested, ErrorOccurred, NetworkError, AuthenticationError)

**Reactive Attributes**: 5 (tasks, selected_task_index, loading, current_list_id, current_list_name)

**Keyboard Bindings**: 10 (j, k, enter, space, a, d, e, r, ?, q)

**Communication Patterns**:
- ✅ Message passing for inter-widget communication
- ✅ Reactive attributes for automatic UI updates
- ✅ Workers for async operations
- ✅ Event bubbling for propagation up widget tree
- ✅ Bindings for keyboard shortcuts

**Next**: Create quickstart guide with setup and usage instructions.
