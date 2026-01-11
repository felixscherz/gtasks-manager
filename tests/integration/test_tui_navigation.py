import pytest
from gtasks_manager.tui.app import TasksApp
from gtasks_manager.core.models import Task, TaskList, TaskStatus, UIFocusPane, UIFocus


class TestTUIViewNavigation:
    """Integration tests for TUI navigation with VIM keys."""

    @pytest.fixture
    def mock_service(self, mocker):
        """Create a mock TaskService."""
        service = mocker.Mock()
        service.list_task_lists.return_value = [TaskList(id="list1", title="Default", updated=None)]
        service.list_tasks.return_value = [
            Task(
                id="task1",
                title="Task 1",
                status=TaskStatus.NEEDS_ACTION,
                list_id="list1",
                updated=None,
            ),
            Task(
                id="task2",
                title="Task 2",
                status=TaskStatus.COMPLETED,
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
    async def test_j_key_moves_selection_down(self, app):
        """Test pressing 'j' moves selection down."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
            await pilot.press("j")
            assert app.ui_focus.index == 1

    @pytest.mark.asyncio
    async def test_k_key_moves_selection_up(self, app):
        """Test pressing 'k' moves selection up."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=1)
            await pilot.press("k")
            assert app.ui_focus.index == 0

    @pytest.mark.asyncio
    async def test_j_key_respects_list_boundaries(self, app):
        """Test that 'j' doesn't move selection past the end."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=1)
            await pilot.press("j")
            assert app.ui_focus.index == 1

    @pytest.mark.asyncio
    async def test_k_key_respects_list_boundaries(self, app):
        """Test that 'k' doesn't move selection past the start."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
            await pilot.press("k")
            assert app.ui_focus.index == 0

    @pytest.mark.asyncio
    async def test_h_key_moves_focus_left(self, app):
        """Test pressing 'h' changes focus to left pane."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)
            await pilot.press("h")
            assert app.ui_focus.pane == UIFocusPane.SIDEBAR

    @pytest.mark.asyncio
    async def test_l_key_moves_focus_right(self, app):
        """Test pressing 'l' changes focus to right pane."""
        async with app.run_test() as pilot:
            await pilot.pause()
            app.ui_focus = UIFocus(pane=UIFocusPane.SIDEBAR, index=0)
            await pilot.press("l")
            assert app.ui_focus.pane == UIFocusPane.TASK_LIST
