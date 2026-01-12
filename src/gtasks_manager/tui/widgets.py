from textual.widgets import ListView


class TasksListView(ListView):
    """Custom ListView that adds VIM keybindings for navigation."""

    BINDINGS = [
        ("j", "cursor_down", "Move down"),
        ("k", "cursor_up", "Move up"),
        ("enter", "app.toggle_completion", "Toggle task"),
        ("space", "app.toggle_completion", "Toggle task"),
    ]
