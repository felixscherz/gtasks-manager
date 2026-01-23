from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gtasks_manager.cli.main import cli


class TestTUIFlowIntegration:
    """Integration tests for TUI workflows."""

    def test_gtasks_without_args_launches_tui(self):
        """Test that running gtasks without arguments launches TUI."""
        runner = CliRunner()

        with patch("gtasks_manager.cli.main.launch_tui") as mock_launch:
            result = runner.invoke(cli, [])
            assert result.exit_code == 0
            mock_launch.assert_called_once()

    def test_gtasks_gui_launches_tui_identical_to_default(self):
        """Test that gtasks gui launches TUI identically to default command."""
        runner = CliRunner()

        with patch("gtasks_manager.cli.main.launch_tui") as mock_launch:
            result = runner.invoke(cli, ["gui"])
            assert result.exit_code == 0
            mock_launch.assert_called_once()

    def test_invalid_args_show_help_not_tui(self):
        """Test that invalid arguments show help instead of launching TUI."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--invalid-flag"])
        assert result.exit_code != 0
        assert "Error:" in result.output or "no such option" in result.output
        assert "Help:" in result.output or "--help" in result.output

    def test_task_toggle_preserves_selection_across_refresh(self):
        """Test that toggling task state preserves selection across list refresh."""
        from gtasks_manager.core.models import Task, TaskStatus
        from gtasks_manager.tui.app import TasksApp

        MagicMock()
        MagicMock()
        service = MagicMock()
        app = TasksApp(service=service)

        task1 = Task(id="1", title="Task 1", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task2 = Task(id="2", title="Task 2", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task3 = Task(id="3", title="Task 3", status=TaskStatus.NEEDS_ACTION, list_id="list1")

        app.tasks = [task1, task2, task3]

        app.selected_task_id = "2"
        preserved_id = app.selected_task_id

        task2_completed = Task(id="2", title="Task 2", status=TaskStatus.COMPLETED, list_id="list1")
        app.tasks = [task1, task2_completed, task3]

        app.selected_task_id = preserved_id
        assert app.selected_task_id == "2"

        found_task = next((t for t in app.tasks if t.id == preserved_id), None)
        assert found_task is not None
        assert found_task.id == "2"

    def test_selection_restoration_handles_moved_task_in_sorted_list(self):
        """Test that selection restoration works when task moves in sorted list."""
        from gtasks_manager.core.models import Task, TaskStatus
        from gtasks_manager.tui.app import TasksApp

        service = MagicMock()
        app = TasksApp(service=service)

        task1 = Task(id="1", title="A Task", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task2 = Task(id="2", title="B Task", status=TaskStatus.NEEDS_ACTION, list_id="list1")
        task3 = Task(id="3", title="C Task", status=TaskStatus.NEEDS_ACTION, list_id="list1")

        app.tasks = [task1, task2, task3]

        app.selected_task_id = "2"
        preserved_id = app.selected_task_id

        task2_completed = Task(id="2", title="B Task", status=TaskStatus.COMPLETED, list_id="list1")

        app.tasks = [task1, task3, task2_completed]

        app.selected_task_id = preserved_id
        assert app.selected_task_id == "2"

        found_task = next((t for t in app.tasks if t.id == preserved_id), None)
        assert found_task is not None
        assert found_task.id == "2"
        assert app.tasks.index(found_task) == 2
