from unittest.mock import Mock

import pytest

from gtasks_manager.core.models import Task, TaskList, TaskStatus, UIFocus, UIFocusPane
from gtasks_manager.tui.app import TasksApp


class TestAccessibilityFocus:
    """Integration tests for accessibility announcements on focus changes."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock TaskService."""
        service = Mock()
        service.list_task_lists.return_value = [TaskList(id="list1", title="Default", updated=None)]
        service.list_tasks.return_value = [
            Task(
                id="task1",
                title="Task 1",
                status=TaskStatus.NEEDS_ACTION,
                list_id="list1",
                updated=None,
            ),
        ]
        return service

    @pytest.fixture
    def app(self, mock_service):
        """Create a TasksApp instance for testing."""
        app = TasksApp(service=mock_service)
        return app

    @pytest.mark.asyncio
    async def test_focus_change_announces_pane_name(self, app, mock_service):
        """Test that focus change announces the new pane name."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
            await pilot.press("h")
            assert app.ui_focus.pane == UIFocusPane.SIDEBAR

    @pytest.mark.asyncio
    async def test_focus_change_updates_selected_task(self, app, mock_service):
        """Test that focus change updates selected task."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.SIDEBAR, index=0)
            await pilot.press("l")
            assert app.ui_focus.pane == UIFocusPane.TASK_LIST
            assert app.selected_task_id is not None
