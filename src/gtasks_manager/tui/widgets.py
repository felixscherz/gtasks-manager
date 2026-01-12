from textual.widgets import ListView


class TasksListView(ListView):
    """Custom ListView that adds a space binding for task completion."""

    BINDINGS = [
        ("space", "app.toggle_completion", "Toggle task"),
    ]
