# Textual Framework Comprehensive Guide

**Version:** Textual 0.47+
**Date:** January 2026
**Purpose:** Practical reference for building Textual TUI applications

---

## Table of Contents

1. [Application Lifecycle & Async Event Handling](#1-application-lifecycle--async-event-handling)
2. [Screen and Widget Composition Patterns](#2-screen-and-widget-composition-patterns)
3. [State Management (Reactive Attributes)](#3-state-management-reactive-attributes)
4. [Testing Strategies](#4-testing-strategies)
5. [Error Handling and Recovery](#5-error-handling-and-recovery)

---

## 1. Application Lifecycle & Async Event Handling

### Overview

Textual applications are built on Python's `asyncio` and use a **message-driven architecture**. All events (key presses, mouse clicks, timers) are converted to messages and processed through an event loop.

### Core Concepts

#### The App Class

```python
from textual.app import App

class MyApp(App):
    """Main application class."""

    def on_mount(self) -> None:
        """Called when app is mounted and ready."""
        self.title = "My Application"
        self.sub_title = "A Textual App"

    async def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "q":
            await self.exit()

if __name__ == "__main__":
    app = MyApp()
    app.run()  # Blocks until app exits
```

#### Lifecycle Events (in order)

1. `compose()` - Return widgets to be mounted
2. `on_mount()` - Called after app/widget is mounted
3. Event loop runs - Processes messages
4. `on_unmount()` - Called before cleanup
5. App exits

### Async Event Handling

All event handlers can be either sync or async:

```python
# Synchronous handler
def on_button_pressed(self, event: Button.Pressed) -> None:
    self.query_one("#output").update("Button clicked!")

# Asynchronous handler (preferred for I/O or long operations)
async def on_button_pressed(self, event: Button.Pressed) -> None:
    result = await self.fetch_data()  # Non-blocking
    self.query_one("#output").update(result)
```

**Best Practice:** Use async handlers when:
- Making network requests
- Reading/writing files
- Performing database queries
- Running any operation that might block

### Workers: Background Tasks

Workers allow you to run background tasks without blocking the UI.

#### The @work Decorator

```python
from textual.worker import work

class MyApp(App):

    @work(exclusive=True)  # Cancel previous workers
    async def fetch_data(self) -> str:
        """Background task using async."""
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            return response.json()

    @work(thread=True)  # Run in separate thread
    def process_file(self, filepath: str) -> dict:
        """CPU-bound task in thread (can use blocking I/O)."""
        with open(filepath) as f:
            return json.load(f)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Start worker and get Worker object
        worker = self.fetch_data()
        # Can wait for result, cancel, or ignore
```

#### Worker Parameters

- `exclusive=True` - Cancel any previous workers from this method
- `thread=True` - Run in thread pool (for blocking/CPU-bound code)
- `exit_on_error=True` - Exit app if worker raises exception (default: True)
- `group="name"` - Group workers together for batch operations
- `name="worker_name"` - Custom name for identification

#### Accessing Worker Results

```python
class MyApp(App):

    @work
    async def fetch_data(self) -> dict:
        # ... fetch data
        return {"key": "value"}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        worker = self.fetch_data()
        worker.result_callback = self.handle_result

    def handle_result(self, result: dict) -> None:
        """Called when worker completes successfully."""
        self.query_one("#output").update(str(result))
```

#### Thread Workers and UI Updates

**IMPORTANT:** Cannot call UI methods directly from thread workers!

```python
# WRONG - Will raise error
@work(thread=True)
def blocking_task(self) -> None:
    data = blocking_io_call()
    self.query_one("#output").update(data)  # ERROR!

# CORRECT - Use call_from_thread
@work(thread=True)
def blocking_task(self) -> None:
    data = blocking_io_call()
    self.call_from_thread(self.update_ui, data)

def update_ui(self, data: str) -> None:
    """Runs in main thread."""
    self.query_one("#output").update(data)
```

### Message Handling

Textual uses message passing for all events:

```python
from textual.message import Message

class MyWidget(Widget):

    class DataLoaded(Message):
        """Custom message when data is loaded."""
        def __init__(self, data: dict) -> None:
            super().__init__()
            self.data = data

    async def load_data(self) -> None:
        data = await fetch_data()
        # Post message to parent
        self.post_message(self.DataLoaded(data))

class MyApp(App):

    def on_my_widget_data_loaded(self, event: MyWidget.DataLoaded) -> None:
        """Handle custom message (auto-discovered by naming convention)."""
        self.log(f"Loaded: {event.data}")
```

### Event Handler Discovery

Handler methods are auto-discovered by naming:

- `on_<event_name>` - Handles any event of that type
- `on_<widget_class>_<event_name>` - Handles events from specific widget class
- `@on(EventClass, "selector")` - Handles events matching CSS selector

```python
from textual.on import on

class MyApp(App):

    # Handle all key presses
    def on_key(self, event: events.Key) -> None:
        pass

    # Handle button presses from any Button
    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    # Handle only buttons matching selector
    @on(Button.Pressed, "#submit-button")
    def handle_submit(self, event: Button.Pressed) -> None:
        pass
```

### Best Practices

1. **Prefer async handlers** for any I/O operations
2. **Use workers** for long-running tasks to keep UI responsive
3. **Use `exclusive=True`** for workers that should cancel previous runs (e.g., search)
4. **Use thread workers** only for blocking I/O or CPU-bound code
5. **Never call UI methods** directly from thread workers - use `call_from_thread()`
6. **Handle worker errors** with `exit_on_error=False` and result callbacks
7. **Use custom messages** for complex component communication

---

## 2. Screen and Widget Composition Patterns

### Overview

Textual uses a **declarative composition model** where you define what widgets to display, and Textual handles rendering and layout.

### The compose() Method

The primary way to add widgets:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container, Vertical, Horizontal

class MyApp(App):

    def compose(self) -> ComposeResult:
        """Called once during mount to get initial widgets."""
        yield Header()
        yield Container(
            Static("Welcome!", id="welcome"),
            Horizontal(
                Button("OK", id="ok"),
                Button("Cancel", id="cancel"),
            ),
            id="dialog",
        )
        yield Footer()
```

**Key Points:**
- Called once when app/widget is mounted
- Must `yield` widgets (not `return`)
- Can yield individual widgets or containers with nested widgets
- Widgets are mounted in the order yielded

### Dynamic Mounting with mount()

For adding widgets after initial composition:

```python
class MyApp(App):

    def compose(self) -> ComposeResult:
        yield Container(id="task-list")

    async def on_mount(self) -> None:
        """Add tasks dynamically."""
        container = self.query_one("#task-list")
        for i in range(10):
            # mount() returns awaitable
            await container.mount(Static(f"Task {i}"))

    async def add_task(self, title: str) -> None:
        """Add task at runtime."""
        container = self.query_one("#task-list")
        # If you need immediate access to the widget:
        widget = Static(title)
        await container.mount(widget)
        widget.scroll_visible()  # Now safe to use
```

**Important:** If you need to interact with a mounted widget immediately, you must `await` the `mount()` call.

### Removing Widgets

```python
# Remove single widget
widget = self.query_one("#my-widget")
await widget.remove()

# Remove multiple widgets
widgets = self.query(".task-item")
for widget in widgets:
    await widget.remove()

# Remove children of a container
container = self.query_one("#container")
await container.remove_children()
```

### Screen Management

Screens are full-screen views that can be pushed/popped like a stack.

#### Defining Screens

```python
from textual.screen import Screen

class MainScreen(Screen):
    """Main application screen."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Main Screen")
        yield Button("Open Settings", id="settings-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings-btn":
            self.app.push_screen(SettingsScreen())

class SettingsScreen(Screen):
    """Settings screen."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Settings")
        yield Button("Back", id="back-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()
```

#### Screen Stack Operations

```python
class MyApp(App):

    def on_mount(self) -> None:
        # Push screen onto stack (current screen remains underneath)
        self.push_screen(MainScreen())

        # Push and get result when screen exits
        self.push_screen(DialogScreen(), callback=self.handle_dialog_result)

        # Pop current screen (go back)
        self.pop_screen()

        # Switch screen (replace current)
        self.switch_screen(MainScreen())

        # Install screen without showing it
        self.install_screen(SettingsScreen(), name="settings")
        # Later: show by name
        self.push_screen("settings")
```

#### Modal Screens

Screens that dim the background and focus attention:

```python
from textual.screen import ModalScreen

class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog that returns bool."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Are you sure?"),
            Horizontal(
                Button("Yes", id="yes", variant="success"),
                Button("No", id="no", variant="error"),
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)  # Return True
        else:
            self.dismiss(False)  # Return False

# Usage
class MyApp(App):

    async def confirm_action(self) -> None:
        result = await self.push_screen_wait(ConfirmDialog())
        if result:
            self.log("User confirmed")
        else:
            self.log("User cancelled")
```

**Key Methods:**
- `dismiss(result)` - Close modal and return result
- `push_screen_wait(screen)` - Async method that waits for screen result

#### Modes: Multiple Screen Stacks

Modes allow switching between different screen stacks (like tabs):

```python
class MyApp(App):

    MODES = {
        "tasks": MainScreen,
        "settings": SettingsScreen,
        "help": HelpScreen,
    }

    def on_mount(self) -> None:
        # Start in tasks mode
        self.switch_mode("tasks")

    def on_key(self, event: events.Key) -> None:
        if event.key == "f1":
            self.switch_mode("help")
        elif event.key == "f2":
            self.switch_mode("settings")
        elif event.key == "f3":
            self.switch_mode("tasks")
```

Each mode maintains its own screen stack independently.

### Widget Querying

Find widgets in the DOM:

```python
# Get single widget (raises if not found or multiple)
widget = self.query_one("#my-id")
widget = self.query_one(".my-class", Button)  # Type-safe

# Get multiple widgets
widgets = self.query(".task-item")
for widget in widgets:
    widget.add_class("selected")

# Check existence
if self.query("#optional-widget"):
    # Widget exists
    pass

# Query from specific widget
container = self.query_one("#container")
buttons = container.query(Button)
```

### Layout Containers

```python
from textual.containers import (
    Container,      # Generic container
    Vertical,       # Stack children vertically
    Horizontal,     # Stack children horizontally
    Grid,           # CSS grid layout
    VerticalScroll, # Vertical with scrolling
    HorizontalScroll, # Horizontal with scrolling
)

def compose(self) -> ComposeResult:
    yield Vertical(
        Static("Header"),
        Horizontal(
            Button("Left"),
            Button("Right"),
        ),
        Grid(
            Static("1"), Static("2"),
            Static("3"), Static("4"),
        ),
    )
```

### Best Practices

1. **Use `compose()` for static structure** - Define initial layout
2. **Use `mount()` for dynamic content** - Add/remove widgets at runtime
3. **Await `mount()` if needed immediately** - Ensures widget is ready
4. **Use screens for major views** - Push/pop for navigation
5. **Use modal screens for dialogs** - Focus user attention
6. **Use modes for tab-like behavior** - Separate screen stacks
7. **Install screens by name** - Reuse screens efficiently
8. **Use CSS for layout** - Prefer CSS over nested containers when possible

---

## 3. State Management (Reactive Attributes)

### Overview

Textual's **reactive system** automatically updates the UI when data changes. This eliminates manual refresh logic.

### Basic Reactive Attributes

```python
from textual.reactive import reactive
from textual.app import App
from textual.widgets import Static

class Counter(Static):
    """Widget that displays a count."""

    count = reactive(0)  # Reactive attribute with default value

    def render(self) -> str:
        """Called automatically when count changes."""
        return f"Count: {self.count}"

    def increment(self) -> None:
        self.count += 1  # Triggers refresh automatically
```

**How it works:**
1. Define class attribute with `reactive(default_value)`
2. Textual intercepts assignments to the attribute
3. When value changes, widget is marked for refresh
4. `render()` is called on next update cycle

### Watch Methods

React to changes with custom logic:

```python
class TaskList(Static):

    tasks = reactive(list)  # Use factory for mutable defaults
    selected_index = reactive(0)

    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """Called when selected_index changes."""
        self.log(f"Selection changed from {old_value} to {new_value}")
        self.scroll_to_index(new_value)

    def watch_tasks(self, old_tasks: list, new_tasks: list) -> None:
        """Called when tasks list changes."""
        self.log(f"Tasks updated: {len(old_tasks)} -> {len(new_tasks)}")
```

**Naming convention:** `watch_<attribute_name>(old_value, new_value)`

**When called:**
- Only when value actually changes (using `!=` comparison)
- After attribute is updated but before refresh
- Receives both old and new values

### Validation Methods

Validate and transform values before assignment:

```python
class ProgressBar(Static):

    progress = reactive(0)

    def validate_progress(self, value: int) -> int:
        """Ensure progress is between 0 and 100."""
        if value < 0:
            return 0
        if value > 100:
            return 100
        return value

    def set_progress(self, value: int) -> None:
        self.progress = value  # Will be clamped by validator
```

**Naming convention:** `validate_<attribute_name>(value) -> value`

**When called:**
- Before value is assigned
- Return value becomes the actual value stored
- Can raise `ValueError` to reject the change

### Compute Methods

Derive values from other reactive attributes:

```python
class TaskWidget(Static):

    title = reactive("")
    completed = reactive(False)

    def compute_display_text(self) -> str:
        """Computed from title and completed."""
        prefix = "[X]" if self.completed else "[ ]"
        return f"{prefix} {self.title}"

    def render(self) -> str:
        return self.display_text  # Auto-computed
```

**Naming convention:** `compute_<attribute_name>() -> value`

**How to access:** Just use `self.attribute_name` (no reactive declaration needed)

**When computed:**
- Automatically when any reactive dependency changes
- Textual tracks which reactives are accessed in the method
- Result is cached until dependencies change

### Reactive Parameters

Control reactive behavior:

```python
from textual.reactive import reactive

class MyWidget(Static):

    # Trigger layout recalculation when changed
    width_percent = reactive(50, layout=True)

    # Don't trigger any refresh (for internal state)
    internal_flag = reactive(False, recompose=False)

    # Trigger full recompose (re-call compose())
    mode = reactive("view", recompose=True)

    # Initialize with different value
    count = reactive(0, init=False)  # Don't set during __init__
```

**Parameters:**
- `layout=True` - Recalculate layout when changed (for size/position)
- `recompose=True` - Re-call `compose()` when changed (rebuild structure)
- `init=False` - Don't initialize during `__init__` (set manually later)

### var() for Non-Refreshing Reactives

When you need reactive behavior without automatic refresh:

```python
from textual.reactive import var

class MyWidget(Static):

    # Regular reactive - triggers refresh
    count = reactive(0)

    # var - can watch/validate but no refresh
    internal_state = var("idle")

    def watch_internal_state(self, old: str, new: str) -> None:
        """Still get watch callbacks."""
        self.log(f"State: {old} -> {new}")
```

**Use cases:**
- Internal state that doesn't affect display
- Want watch/validate methods without refresh overhead
- Coordinating between widgets via messages

### Mutating Reactive Collections

**IMPORTANT:** Direct mutation doesn't trigger reactivity!

```python
# WRONG - Won't trigger update
self.tasks.append(new_task)

# CORRECT - Use mutate_reactive
def add_task(self, task: str) -> None:
    self.mutate_reactive(TaskWidget.tasks)  # Mark as dirty
    self.tasks.append(task)
    # Alternatively: reassign
    # self.tasks = self.tasks + [task]
```

**When to use:**
- Modifying lists, dicts, sets
- Any in-place mutation of reactive mutable objects

### Data Binding

Bind reactive attributes between widgets:

```python
from textual.reactive import reactive

class Slider(Widget):
    value = reactive(50)

class Display(Widget):
    value = reactive(0)

    def render(self) -> str:
        return f"Value: {self.value}"

class MyApp(App):

    def compose(self) -> ComposeResult:
        slider = Slider()
        display = Display()

        # Bind slider.value to display.value
        display.data_bind(Slider.value, "value")

        yield slider
        yield display
```

Now changing `slider.value` automatically updates `display.value`.

### State Management Patterns

#### Local Component State

```python
class TaskItem(Static):
    """Self-contained task with own state."""

    title = reactive("")
    completed = reactive(False)

    def toggle(self) -> None:
        self.completed = not self.completed
```

#### Shared State via App

```python
class MyApp(App):
    """App holds shared state."""

    tasks = reactive(list, layout=True)
    selected_task_id = reactive(None)

    def add_task(self, title: str) -> None:
        self.tasks = self.tasks + [{"id": uuid4(), "title": title}]

    def watch_tasks(self, old_tasks: list, new_tasks: list) -> None:
        """Update all task widgets when tasks change."""
        container = self.query_one("#task-list")
        # Rebuild task list...
```

#### Message-Based State Updates

```python
class TaskList(Widget):

    class TaskCompleted(Message):
        def __init__(self, task_id: str) -> None:
            super().__init__()
            self.task_id = task_id

    tasks = reactive(list)

    def mark_complete(self, task_id: str) -> None:
        # Update local state
        self.tasks = [
            {**t, "completed": True} if t["id"] == task_id else t
            for t in self.tasks
        ]
        # Notify parent
        self.post_message(self.TaskCompleted(task_id))

class MyApp(App):

    def on_task_list_task_completed(self, event: TaskList.TaskCompleted) -> None:
        """Handle completion in app state."""
        self.save_task_completion(event.task_id)
```

### Best Practices

1. **Use reactive for displayable state** - Anything that affects the UI
2. **Use var for internal state** - State that needs watch but not refresh
3. **Use watch methods sparingly** - Only for side effects, not display logic
4. **Use compute for derived values** - Better than manual updates
5. **Use validation for constraints** - Keep state valid
6. **Always mutate_reactive for collections** - Don't forget this!
7. **Use data_bind for synchronized values** - Avoid manual copying
8. **Keep state close to usage** - Widget state in widget, shared state in app
9. **Prefer immutable updates** - `self.list = self.list + [item]` is clear
10. **Use layout=True for layout-affecting changes** - Size, position, visibility

---

## 4. Testing Strategies

### Overview

Textual provides `run_test()` for headless testing and a `Pilot` API for simulating user interactions.

### Basic Test Structure

```python
import pytest
from textual.app import App
from textual.widgets import Button, Static

class MyApp(App):

    def compose(self) -> ComposeResult:
        yield Static("Click the button", id="message")
        yield Button("Click Me", id="click-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one("#message", Static).update("Button clicked!")

# Test using pytest
@pytest.mark.asyncio
async def test_button_click():
    """Test that clicking button updates message."""
    app = MyApp()

    async with app.run_test() as pilot:
        # App is now running in test mode

        # Check initial state
        message = app.query_one("#message", Static)
        assert message.renderable == "Click the button"

        # Simulate button click
        await pilot.click("#click-btn")

        # Check updated state
        assert message.renderable == "Button clicked!"
```

**Key points:**
- Use `async with app.run_test()` for headless testing
- Returns a `Pilot` object for simulating input
- Must `await` pilot methods
- App runs until context exits

### The Pilot API

The `Pilot` simulates user interactions:

```python
async def test_keyboard_navigation():
    app = MyApp()

    async with app.run_test() as pilot:
        # Press keys
        await pilot.press("tab")  # Single key
        await pilot.press("enter")
        await pilot.press("ctrl+c")  # Key combinations

        # Type text (series of key presses)
        await pilot.type("Hello, world!")

        # Click widgets
        await pilot.click("#my-button")  # By selector
        await pilot.click(Button, "#submit")  # Type + selector

        # Mouse hover
        await pilot.hover("#my-widget")

        # Pause to let async operations complete
        await pilot.pause()
        await pilot.pause(0.5)  # Pause for 0.5 seconds

        # Wait for specific widget
        await pilot.wait_for_scheduled_animations()
```

### Testing Async Widgets

When testing widgets with workers or async operations:

```python
class DataApp(App):

    @work
    async def load_data(self) -> None:
        # Simulate async data loading
        await asyncio.sleep(0.1)
        self.query_one("#status", Static).update("Data loaded")

    def on_mount(self) -> None:
        self.load_data()

async def test_async_data_loading():
    app = DataApp()

    async with app.run_test() as pilot:
        # Initial state
        status = app.query_one("#status", Static)
        assert status.renderable != "Data loaded"

        # Wait for async operation
        await pilot.pause(0.2)  # Wait longer than sleep

        # Check loaded state
        assert status.renderable == "Data loaded"
```

**Strategies:**
- Use `await pilot.pause()` to let workers complete
- Use `await pilot.wait_for_scheduled_animations()` for animations
- Consider making delays configurable for faster tests

### Snapshot Testing

Textual supports visual regression testing with snapshots:

```python
# Install: pip install pytest-textual-snapshot

def test_app_appearance(snap_compare):
    """Test that app looks correct."""
    app = MyApp()

    # Compare against stored SVG snapshot
    assert snap_compare(app)
```

**How it works:**
1. First run: generates SVG snapshot of app
2. Subsequent runs: compares current render to snapshot
3. Fails if appearance changes
4. Update with `pytest --snapshot-update`

**Use cases:**
- Catch unintended visual changes
- Document expected appearance
- Test different screen sizes

### Testing State Changes

```python
async def test_reactive_state():
    """Test reactive attribute updates."""
    app = CounterApp()

    async with app.run_test() as pilot:
        counter = app.query_one(Counter)

        # Check initial state
        assert counter.count == 0

        # Trigger increment
        await pilot.click("#increment-btn")

        # Check state updated
        assert counter.count == 1

        # Check UI reflects state
        assert "Count: 1" in counter.render()
```

### Testing Navigation

```python
async def test_screen_navigation():
    """Test pushing and popping screens."""
    app = MyApp()

    async with app.run_test() as pilot:
        # Check initial screen
        assert isinstance(app.screen, MainScreen)

        # Navigate to settings
        await pilot.click("#settings-btn")
        await pilot.pause()  # Let screen push complete

        # Check settings screen active
        assert isinstance(app.screen, SettingsScreen)

        # Navigate back
        await pilot.press("escape")  # Or click back button
        await pilot.pause()

        # Check back on main screen
        assert isinstance(app.screen, MainScreen)
```

### Testing Modal Dialogs

```python
async def test_modal_dialog():
    """Test modal dialog interaction."""
    app = MyApp()

    async with app.run_test() as pilot:
        # Trigger dialog
        await pilot.click("#delete-btn")
        await pilot.pause()

        # Check modal is showing
        assert isinstance(app.screen, ConfirmDialog)

        # Click yes
        await pilot.click("#yes-btn")
        await pilot.pause()

        # Check dialog dismissed
        assert not isinstance(app.screen, ConfirmDialog)

        # Check action was performed
        assert len(app.tasks) == 0
```

### Testing Error Handling

```python
async def test_error_handling():
    """Test app handles errors gracefully."""
    app = MyApp()

    async with app.run_test() as pilot:
        # Trigger error condition
        await pilot.click("#load-invalid-data")
        await pilot.pause()

        # Check error message shown
        error_msg = app.query_one("#error-message")
        assert error_msg.has_class("error")
        assert "Invalid data" in error_msg.renderable

        # Check app still responsive
        await pilot.press("escape")
        assert error_msg not in app.query("*")
```

### Mocking in Tests

```python
from unittest.mock import AsyncMock, patch

async def test_with_mocked_api():
    """Test with mocked external API."""
    app = MyApp()

    # Mock the API call
    with patch.object(app, 'fetch_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"tasks": [{"title": "Test"}]}

        async with app.run_test() as pilot:
            await pilot.click("#refresh-btn")
            await pilot.pause()

            # Check mock was called
            mock_fetch.assert_called_once()

            # Check data displayed
            task_list = app.query_one("#task-list")
            assert "Test" in str(task_list.renderable)
```

### Pytest Fixtures

```python
import pytest
from textual.pilot import Pilot

@pytest.fixture
async def app_pilot():
    """Fixture providing app and pilot."""
    app = MyApp()
    async with app.run_test() as pilot:
        yield app, pilot

@pytest.mark.asyncio
async def test_with_fixture(app_pilot):
    """Test using fixture."""
    app, pilot = app_pilot

    await pilot.click("#my-button")
    assert app.query_one("#status").renderable == "Clicked"
```

### Best Practices

1. **Use `run_test()` for all tests** - Provides headless environment
2. **Always await pilot methods** - They're async operations
3. **Use `pilot.pause()` for async operations** - Let workers complete
4. **Test behavior, not implementation** - Use selectors, not internals
5. **Use snapshot tests for visual regression** - Catch unintended changes
6. **Mock external dependencies** - Network, file I/O, databases
7. **Test error paths** - Don't just test happy path
8. **Use fixtures for common setup** - Reduce duplication
9. **Test screen navigation** - Push, pop, modal dialogs
10. **Test keyboard and mouse** - Both interaction methods

---

## 5. Error Handling and Recovery

### Overview

Textual applications need robust error handling because they run continuously and interact with external systems (APIs, files, user input).

### Worker Error Handling

Workers have built-in error handling:

```python
from textual.worker import work

class MyApp(App):

    @work(exit_on_error=False)  # Don't crash app on error
    async def risky_operation(self) -> dict:
        """Worker that might fail."""
        try:
            result = await external_api_call()
            return result
        except APIError as e:
            self.log.error(f"API error: {e}")
            return {"error": str(e)}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        worker = self.risky_operation()
        worker.result_callback = self.handle_result
        worker.error_callback = self.handle_error

    def handle_result(self, result: dict) -> None:
        """Called on success."""
        if "error" in result:
            self.show_error(result["error"])
        else:
            self.show_data(result)

    def handle_error(self, error: Exception) -> None:
        """Called if worker raises unhandled exception."""
        self.log.error(f"Worker failed: {error}")
        self.show_error(f"Operation failed: {error}")
```

**Worker error parameters:**
- `exit_on_error=False` - Don't exit app on error (default is True!)
- Set `worker.error_callback` to handle errors
- Set `worker.result_callback` to handle success

### Event Handler Error Handling

Wrap event handlers in try/except:

```python
class MyApp(App):

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press with error handling."""
        try:
            result = await self.perform_action()
            self.show_success(result)
        except ValidationError as e:
            # User error - show friendly message
            self.show_error(f"Invalid input: {e}")
        except NetworkError as e:
            # Network error - suggest retry
            self.show_error(f"Network error: {e}. Please try again.")
        except Exception as e:
            # Unexpected error - log and show generic message
            self.log.exception("Unexpected error in button handler")
            self.show_error("An unexpected error occurred")
```

**Best practices:**
- Catch specific exceptions first
- Log unexpected exceptions with `self.log.exception()`
- Show user-friendly messages
- Don't let handlers crash silently

### Message Handling Patterns

Use messages to communicate errors:

```python
from textual.message import Message

class TaskWidget(Widget):

    class LoadFailed(Message):
        """Posted when task loading fails."""
        def __init__(self, error: str) -> None:
            super().__init__()
            self.error = error

    async def load_task(self, task_id: str) -> None:
        try:
            task = await fetch_task(task_id)
            self.update_display(task)
        except Exception as e:
            self.log.exception(f"Failed to load task {task_id}")
            self.post_message(self.LoadFailed(str(e)))

class MyApp(App):

    def on_task_widget_load_failed(self, event: TaskWidget.LoadFailed) -> None:
        """Handle task loading errors."""
        self.query_one("#error-display").update(
            f"Failed to load task: {event.error}"
        )
```

### Event Bubbling and Stopping

Control event propagation:

```python
class CustomButton(Button):

    def on_click(self, event: events.Click) -> None:
        """Handle click locally."""
        if not self.disabled:
            self.toggle_class("active")
        else:
            # Stop event from bubbling to parent
            event.stop()

class Container(Widget):

    def on_click(self, event: events.Click) -> None:
        """Only called if child didn't stop propagation."""
        self.log("Container clicked")
```

**Methods:**
- `event.stop()` - Stop bubbling to parent widgets
- `event.prevent_default()` - Prevent default behavior (if any)

### Validation Error Handling

Reactive validation can raise errors:

```python
class TaskInput(Widget):

    task_title = reactive("")

    def validate_task_title(self, value: str) -> str:
        """Validate task title."""
        if not value.strip():
            raise ValueError("Task title cannot be empty")
        if len(value) > 100:
            raise ValueError("Task title too long (max 100 chars)")
        return value.strip()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        try:
            self.task_title = event.value  # May raise ValueError
            await self.save_task()
        except ValueError as e:
            # Show validation error to user
            self.query_one("#error-label").update(str(e))
            self.query_one("#error-label").add_class("error")
```

### Global Error Handling

Handle uncaught exceptions in the app:

```python
class MyApp(App):

    def on_mount(self) -> None:
        """Set up global error handler."""
        # Python's exception hook doesn't work in Textual
        # Instead, use try/except in key methods
        pass

    async def action_quit(self) -> None:
        """Quit action with cleanup."""
        try:
            await self.cleanup()
        except Exception as e:
            self.log.exception("Error during cleanup")
        finally:
            self.exit()
```

**Note:** Textual runs in async context, so `sys.excepthook` won't catch errors. Use try/except in critical paths.

### Displaying Errors to Users

Common patterns for showing errors:

```python
# Pattern 1: Dedicated error widget
class MyApp(App):

    def compose(self) -> ComposeResult:
        yield Static("", id="error-display", classes="error hidden")
        # ... other widgets

    def show_error(self, message: str) -> None:
        """Display error message."""
        error_widget = self.query_one("#error-display")
        error_widget.update(f"Error: {message}")
        error_widget.remove_class("hidden")

        # Auto-hide after 5 seconds
        self.set_timer(5.0, lambda: error_widget.add_class("hidden"))

# Pattern 2: Modal error dialog
class ErrorDialog(ModalScreen):

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Error: {self.message}", id="error-msg"),
            Button("OK", id="ok"),
            id="error-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class MyApp(App):

    def show_error(self, message: str) -> None:
        """Show error in modal dialog."""
        self.push_screen(ErrorDialog(message))

# Pattern 3: Toast notification
class MyApp(App):

    def show_error(self, message: str) -> None:
        """Show error notification."""
        self.notify(message, severity="error", timeout=5)
```

### Retry Logic

Implement retry for transient failures:

```python
class MyApp(App):

    async def fetch_with_retry(
        self,
        max_retries: int = 3,
        delay: float = 1.0
    ) -> dict:
        """Fetch data with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await self.fetch_data()
            except NetworkError as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    raise
                # Wait before retry (exponential backoff)
                wait_time = delay * (2 ** attempt)
                self.log(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                await asyncio.sleep(wait_time)
```

### Graceful Degradation

Continue functioning with reduced features:

```python
class MyApp(App):

    cache_available = reactive(True)
    network_available = reactive(True)

    async def on_mount(self) -> None:
        """Initialize with feature detection."""
        try:
            await self.init_cache()
        except Exception as e:
            self.log.error(f"Cache unavailable: {e}")
            self.cache_available = False

        try:
            await self.check_network()
        except Exception as e:
            self.log.error(f"Network unavailable: {e}")
            self.network_available = False

    async def save_task(self, task: dict) -> None:
        """Save task with fallbacks."""
        # Try network first
        if self.network_available:
            try:
                await self.save_to_server(task)
                if self.cache_available:
                    await self.save_to_cache(task)
                return
            except NetworkError:
                self.network_available = False
                self.show_error("Network unavailable, saving locally")

        # Fall back to cache
        if self.cache_available:
            try:
                await self.save_to_cache(task)
                return
            except CacheError:
                self.cache_available = False

        # No storage available
        self.show_error("Cannot save task: no storage available")
```

### Logging Best Practices

Use Textual's built-in logging:

```python
class MyApp(App):

    async def on_mount(self) -> None:
        """Demonstrate logging levels."""
        self.log.debug("Debug info for development")
        self.log.info("General information")
        self.log.warning("Warning about potential issue")
        self.log.error("Error that was handled")
        self.log.exception("Error with full traceback")

    async def critical_operation(self) -> None:
        """Log errors with context."""
        try:
            await dangerous_operation()
        except Exception as e:
            self.log.exception(
                "Critical operation failed",
                extra={"user_id": self.user_id, "context": "startup"}
            )
            raise
```

**View logs:** Run app with `textual run --dev app.py` to see logs.

### Best Practices

1. **Set `exit_on_error=False` for workers** - Prevent crashes
2. **Catch specific exceptions first** - Handle known errors appropriately
3. **Log unexpected exceptions** - Use `log.exception()` for tracebacks
4. **Show user-friendly messages** - Don't expose technical details
5. **Use messages for error propagation** - Decouple error handling
6. **Implement retry logic** - Handle transient failures
7. **Gracefully degrade** - Provide fallbacks when features fail
8. **Always clean up resources** - Use try/finally or context managers
9. **Test error paths** - Don't just test happy path
10. **Monitor and log errors** - Use logging for debugging production issues

---

## Summary

This guide covers the five essential aspects of building Textual applications:

1. **Lifecycle & Async** - Understanding asyncio integration, workers, and message handling
2. **Composition** - Building UIs with compose(), screens, and dynamic mounting
3. **State Management** - Using reactive attributes for automatic UI updates
4. **Testing** - Writing reliable tests with Pilot and snapshots
5. **Error Handling** - Building robust apps that handle failures gracefully

**Next Steps:**
- Review the official Textual documentation for latest updates
- Study example apps in the Textual repository
- Build a small project to practice these patterns
- Explore Textual's rich widget library and CSS styling

**Resources:**
- Official docs: https://textual.textualize.io/
- GitHub: https://github.com/Textualize/textual
- Discord: https://discord.gg/Enf6Z3qhVr

---

*Document generated: January 2026*
*Textual version: 0.47+*
