from gtasks_manager.core.models import Task, TaskStatus


class TestToggleOptimistic:
    """Unit tests for optimistic toggle logic."""

    def test_toggle_from_needs_action_to_completed(self):
        """Test toggling task from needsAction to completed."""
        task = Task(
            id="task1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            list_id="list1",
            updated=None,
        )
        old_status = task.status

        task.mark_complete()

        assert task.status == TaskStatus.COMPLETED
        assert old_status == TaskStatus.NEEDS_ACTION

    def test_toggle_from_completed_to_needs_action(self):
        """Test toggling task from completed to needsAction."""
        task = Task(
            id="task1", title="Task 1", status=TaskStatus.COMPLETED, list_id="list1", updated=None
        )
        task.completed = None
        old_status = task.status

        task.mark_incomplete()

        assert task.status == TaskStatus.NEEDS_ACTION
        assert old_status == TaskStatus.COMPLETED

    def test_toggle_twice_returns_to_original(self):
        """Test toggling twice returns task to original status."""
        task = Task(
            id="task1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            list_id="list1",
            updated=None,
        )
        original_status = task.status

        task.mark_complete()
        task.mark_incomplete()

        assert task.status == original_status

    def test_revert_toggle_on_failure(self):
        """Test reverting toggle on API failure."""
        task = Task(
            id="task1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            list_id="list1",
            updated=None,
        )
        old_status = task.status

        task.mark_complete()
        assert task.status == TaskStatus.COMPLETED

        task.status = old_status
        assert task.status == TaskStatus.NEEDS_ACTION
