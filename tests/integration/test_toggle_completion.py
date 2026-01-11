import pytest
from unittest.mock import Mock, AsyncMock
from gtasks_manager.tui.app import TasksApp
from gtasks_manager.core.models import Task, TaskList, TaskStatus


class TestToggleCompletion:
    """Integration tests for toggle task completion functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock TaskService."""
        service = Mock()
        service.list_task_lists.return_value = [TaskList(id="list1", title="Default", updated=None)]
        task = Task(
            id="task1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            list_id="list1",
            updated=None,
        )
        service.list_tasks.return_value = [task]
        service.update_task.return_value = task
        return service

    @pytest.fixture
    def app(self, mock_service):
        """Create a TasksApp instance for testing."""
        app = TasksApp(service=mock_service)
        return app

    @pytest.mark.asyncio
    async def test_enter_toggles_task_to_completed(self, app, mock_service):
        """Test pressing Enter toggles task from needsAction to completed."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.selected_task_id = "task1"
            await pilot.press("Enter")
            assert mock_service.update_task.called

    @pytest.mark.asyncio
    async def test_enter_toggles_task_to_needs_action(self, app, mock_service):
        """Test pressing Enter toggles task from completed to needsAction."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.selected_task_id = "task1"
            await pilot.press("Enter")
            assert mock_service.update_task.called

    @pytest.mark.asyncio
    async def test_optimistic_ui_update_on_success(self, app, mock_service):
        """Test that UI updates optimistically before API completes."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.selected_task_id = "task1"
            initial_status = app.tasks[0].status
            await pilot.press("Enter")
            assert app.tasks[0].status != initial_status

    @pytest.mark.asyncio
    async def test_ui_reverts_on_api_failure(self, app, mock_service):
        """Test that UI reverts when API call fails."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.selected_task_id = "task1"
            mock_service.update_task.side_effect = Exception("API Error")
            initial_status = app.tasks[0].status
            await pilot.press("Enter")
            assert app.tasks[0].status == initial_status
