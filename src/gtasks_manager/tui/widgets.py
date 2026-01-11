from textual.widgets import ListView


class TasksListView(ListView):
    """Custom ListView that adds VIM keybindings for navigation."""

    BINDINGS = ListView.BINDINGS + [
        ("j", "cursor_down", "Move down"),
        ("k", "cursor_up", "Move up"),
    ]
