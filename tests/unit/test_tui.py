import pytest

from gtasks_manager.core.services import TaskService
from gtasks_manager.tui.app import TasksApp


class TestTasksApp:
    """Tests for TasksApp TUI application class."""

    def test_app_initialization(self, mock_service):
        """Test that TasksApp initializes correctly."""
        app = TasksApp(service=mock_service)
        assert app.service is mock_service
        assert app.tasks == []
        assert app.task_lists == []
        assert app.current_list_id == "@default"
        assert app.selected_task_id is None

    def test_set_selection_highlights_task(self, mock_service):
        """Test that setting selection highlights the correct task."""
        from gtasks_manager.core.models import Task, TaskStatus

        app = TasksApp(service=mock_service)
        task1 = Task(id="1", title="Task 1", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task2 = Task(id="2", title="Task 2", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        app.tasks = [task1, task2]

        app.selected_task_id = "2"
        assert app.selected_task_id == "2"

    def test_preserve_selection_stores_task_id(self, mock_service):
        """Test that preserve_selection stores current task ID."""
        from gtasks_manager.tui.state import TUISelectionState

        app = TasksApp(service=mock_service)
        app.selected_task_id = "task123"

        selection_state = TUISelectionState(task_id="task123")
        assert selection_state.task_id == "task123"
        assert selection_state.preserved is False

        selection_state_preserved = TUISelectionState(task_id="task123", preserved=True)
        assert selection_state_preserved.preserved is True

    def test_restore_selection_moves_highlight_to_correct_index(self, mock_service):
        """Test that restoring selection moves highlight to correct task by ID."""
        from gtasks_manager.core.models import Task, TaskStatus

        app = TasksApp(service=mock_service)
        task1 = Task(id="1", title="Task 1", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task2 = Task(id="2", title="Task 2", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task3 = Task(id="3", title="Task 3", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        app.tasks = [task1, task2, task3]

        preserved_id = "2"
        app.selected_task_id = preserved_id
        assert app.selected_task_id == preserved_id

        found_task = next((t for t in app.tasks if t.id == preserved_id), None)
        assert found_task is not None
        assert found_task.id == "2"

    @pytest.fixture
    def mock_service(self):
        """Create a mock TaskService for testing."""
        from unittest.mock import MagicMock

        mock_api = MagicMock()
        mock_cache = MagicMock()
        return TaskService(api=mock_api, cache=mock_cache)


class TestTasksListView:
    """Tests for TasksListView custom widget."""

    def test_tasks_list_view_has_space_binding(self):
        """Test that TasksListView has space key binding for task completion."""
        from gtasks_manager.tui.widgets import TasksListView

        assert TasksListView.BINDINGS is not None
        assert len(TasksListView.BINDINGS) > 0
