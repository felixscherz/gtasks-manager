from typing import List, Optional
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, ListItem, ListView
from textual import work

from gtasks_manager.core.models import Task, TaskList
from gtasks_manager.core.services import TaskService


class TasksApp(App):
    """A Textual app for managing Google Tasks."""

    CSS = """
    Screen {
        background: #121212;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    tasks: reactive[List[Task]] = reactive([])
    task_lists: reactive[List[TaskList]] = reactive([])
    current_list_id: reactive[str] = reactive("@default")
    loading_state: reactive[bool] = reactive(False)

    def __init__(self, service: TaskService):
        super().__init__()
        self.service = service

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Loading tasks...", id="loading-indicator")
        yield ListView(id="task-list-view")
        yield Footer()

    def on_mount(self) -> None:
        self.load_data()

    @work
    async def load_data(self) -> None:
        """Load task lists and tasks."""
        self.loading_state = True
        try:
            self.task_lists = self.service.list_task_lists()
            self.tasks = self.service.list_tasks(self.current_list_id)
        finally:
            self.loading_state = False

    def watch_tasks(self, tasks: List[Task]) -> None:
        """Called when tasks change."""
        list_view = self.query_one("#task-list-view", ListView)
        list_view.clear()
        for task in tasks:
            status = "✓" if task.status == "completed" else "○"
            list_view.append(ListItem(Static(f"{status} {task.title}")))

    def watch_loading_state(self, loading: bool) -> None:
        """Called when loading state changes."""
        indicator = self.query_one("#loading-indicator", Static)
        indicator.display = loading

    def action_refresh(self) -> None:
        """Refresh tasks."""
        self.load_data()


if __name__ == "__main__":
    # For testing purposes only
    from gtasks_manager.adapters.google_tasks import GoogleTasksAdapter
    from gtasks_manager.core.task_cache import TaskCache
    from gtasks_manager.config import CONFIG_DIR

    adapter = GoogleTasksAdapter()
    cache = TaskCache.load(CONFIG_DIR / "task_cache.json")
    service = TaskService(adapter, cache)
    app = TasksApp(service)
    app.run()
