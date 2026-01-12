import logging

from textual import work
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Header, ListItem, ListView, Static

from gtasks_manager.core.models import Task, TaskList, TaskStatus, UIFocus, UIFocusPane
from gtasks_manager.core.services import TaskService
from gtasks_manager.tui.keybindings import KeyBindingManager
from gtasks_manager.tui.utils import announce_for_accessibility
from gtasks_manager.tui.widgets import TasksListView

logger = logging.getLogger(__name__)


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
        ("enter", "toggle_completion", "Toggle task"),
        ("j", "move_down", "Move down"),
        ("k", "move_up", "Move up"),
        ("h", "move_left", "Move left"),
        ("l", "move_right", "Move right"),
    ]

    tasks: reactive[list[Task]] = reactive([])
    task_lists: reactive[list[TaskList]] = reactive([])
    current_list_id: reactive[str] = reactive("@default")
    loading_state: reactive[bool] = reactive(False)
    vim_enabled: reactive[bool] = reactive(True)
    ui_focus: reactive[UIFocus] = reactive(UIFocus(pane=UIFocusPane.TASK_LIST, index=None))

    def __init__(self, service: TaskService):
        super().__init__()
        self.service = service
        self.keybinding_manager = KeyBindingManager()
        self.selected_task_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Loading tasks...", id="loading-indicator")
        yield Static("[VIM]" if self.vim_enabled else "", id="vim-status")
        yield TasksListView(id="task-list-view")
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self._update_selected_task)
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

    def watch_tasks(self, tasks: list[Task]) -> None:
        """Called when tasks change."""
        try:
            list_view = self.query_one("#task-list-view", ListView)
            list_view.clear()
            for task in tasks:
                status = "✓" if task.status == TaskStatus.COMPLETED else "○"
                list_view.append(ListItem(Static(f"{status} {task.title}")))
            if len(tasks) > 0:
                list_view.index = 0
                self.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
                self._update_selected_task()
            else:
                self.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=None)
                self._update_selected_task()
        except Exception as e:
            logger.error(f"Error in watch_tasks: {e}")

    def watch_ui_focus(self, old_focus: UIFocus, new_focus: UIFocus) -> None:
        """Called when UI focus changes."""
        if new_focus.pane == UIFocusPane.TASK_LIST and new_focus.index is not None:
            list_view = self.query_one("#task-list-view", ListView)
            if 0 <= new_focus.index < len(self.tasks):
                list_view.index = new_focus.index
                self._update_selected_task()

    def watch_loading_state(self, loading: bool) -> None:
        """Called when loading state changes."""
        indicator = self.query_one("#loading-indicator", Static)
        indicator.display = loading

    def watch_vim_enabled(self, enabled: bool) -> None:
        """Called when VIM bindings enabled state changes."""
        try:
            indicator = self.query_one("#vim-status", Static)
            indicator.update("[VIM]" if enabled else "")
        except Exception:
            pass
        self.keybinding_manager.set_enabled(enabled)

    def action_refresh(self) -> None:
        """Refresh tasks."""
        self.load_data()

    def action_move_down(self) -> None:
        """Move selection down in task list."""
        self.action_cursor_down()

    def action_move_up(self) -> None:
        """Move selection up in task list."""
        self.action_cursor_up()

    def action_move_left(self) -> None:
        """Move focus to left pane."""
        self._move_focus_left()

    def action_move_right(self) -> None:
        """Move focus to right pane."""
        self._move_focus_right()

    def action_toggle_completion(self) -> None:
        """Toggle completion of selected task."""
        self._toggle_completion()

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "enter":
            event.stop()
            self.action_toggle_completion()

    def action_cursor_down(self) -> None:
        """Move cursor down and update selected task."""
        list_view = self.query_one("#task-list-view", ListView)
        if len(self.tasks) > 0:
            current_index = list_view.index or 0
            if current_index < len(self.tasks) - 1:
                list_view.index = current_index + 1
                self.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=list_view.index)
            self._update_selected_task()

    def action_cursor_up(self) -> None:
        """Move cursor up and update selected task."""
        list_view = self.query_one("#task-list-view", ListView)
        if len(self.tasks) > 0:
            current_index = list_view.index or 0
            if current_index > 0:
                list_view.index = current_index - 1
                self.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=list_view.index)
            self._update_selected_task()

    def _move_selection_up(self) -> None:
        """Move selection up in the task list."""
        if not self.tasks:
            return
        if self.ui_focus.index is None:
            self.ui_focus = UIFocus(pane=self.ui_focus.pane, index=0)
        elif self.ui_focus.index > 0:
            new_index = self.ui_focus.index - 1
            self.ui_focus = UIFocus(pane=self.ui_focus.pane, index=new_index)
            self._update_selected_task()

    def _move_focus_left(self) -> None:
        """Move focus to left pane."""
        current = self.ui_focus.pane
        if current == UIFocusPane.TASK_LIST:
            self.ui_focus = UIFocus(pane=UIFocusPane.SIDEBAR, index=0)
            announce_for_accessibility(self, "Focused on sidebar")

    def _move_focus_right(self) -> None:
        """Move focus to right pane."""
        current = self.ui_focus.pane
        if current == UIFocusPane.SIDEBAR:
            self.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
            self._update_selected_task()
            announce_for_accessibility(self, "Focused on task list")

    def _update_selected_task(self) -> None:
        """Update selected_task_id based on current index."""
        try:
            list_view = self.query_one("#task-list-view", ListView)
            current_index = list_view.index
            if current_index is not None and 0 <= current_index < len(self.tasks):
                self.selected_task_id = self.tasks[current_index].id
            else:
                self.selected_task_id = None
        except Exception as e:
            logger.error(f"Error in _update_selected_task: {e}")

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

        updated_tasks = []
        for t in self.tasks:
            if t.id == self.selected_task_id:
                updated_tasks.append(
                    Task(
                        id=t.id,
                        title=t.title,
                        status=new_status,
                        list_id=t.list_id,
                        updated=t.updated,
                        notes=t.notes,
                        due=t.due,
                        completed=t.completed,
                    )
                )
            else:
                updated_tasks.append(
                    Task(
                        id=t.id,
                        title=t.title,
                        status=t.status,
                        list_id=t.list_id,
                        updated=t.updated,
                        notes=t.notes,
                        due=t.due,
                        completed=t.completed,
                    )
                )

        self.tasks = updated_tasks
        self._persist_toggle(task.id, old_status)

    @work
    async def _persist_toggle(self, task_id: str, old_status: TaskStatus) -> None:
        """Persist toggle in background with rollback on failure."""
        try:
            new_status = "completed" if old_status == TaskStatus.NEEDS_ACTION else "needsAction"
            self.service.update_task(
                self.current_list_id, task_id, status=new_status, completed_cache=False
            )
        except Exception as e:
            self._revert_toggle(task_id, old_status)
            logger.error(f"Error toggling task {task_id}: {e}")

    def _revert_toggle(self, task_id: str, old_status: TaskStatus) -> None:
        """Revert toggle on failure."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.status = old_status


if __name__ == "__main__":
    # For testing purposes only
    from gtasks_manager.adapters.google_tasks import GoogleTasksAdapter
    from gtasks_manager.config import CONFIG_DIR
    from gtasks_manager.core.task_cache import TaskCache

    adapter = GoogleTasksAdapter()
    cache = TaskCache.load(CONFIG_DIR / "task_cache.json")
    service = TaskService(adapter, cache)
    app = TasksApp(service)
    app.run()
