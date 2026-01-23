from datetime import datetime

import pytest

from gtasks_manager.tui.state import TaskListMetadata, TUIApplicationState, TUISelectionState


class TestTUISelectionState:
    """Tests for TUISelectionState dataclass."""

    def test_selection_state_initialization(self):
        """Test that TUISelectionState initializes with correct default values."""
        state = TUISelectionState(task_id="task123")
        assert state.task_id == "task123"
        assert state.preserved is False
        assert state.timestamp is not None
        assert isinstance(state.timestamp, datetime)

    def test_selection_state_with_preserved_flag(self):
        """Test that TUISelectionState accepts preserved flag."""
        state = TUISelectionState(task_id="task123", preserved=True)
        assert state.task_id == "task123"
        assert state.preserved is True

    def test_selection_state_with_custom_timestamp(self):
        """Test that TUISelectionState accepts custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        state = TUISelectionState(task_id="task123", timestamp=custom_time)
        assert state.timestamp == custom_time

    def test_selection_state_requires_task_id(self):
        """Test that TUISelectionState requires task_id parameter."""
        with pytest.raises(TypeError):
            TUISelectionState()

    def test_selection_state_transitions(self):
        """Test that selection state transitions from not preserved to preserved."""
        state1 = TUISelectionState(task_id="task1")
        assert state1.preserved is False

        state2 = TUISelectionState(task_id="task1", preserved=True)
        assert state2.preserved is True
        assert state2.task_id == state1.task_id


class TestTaskListMetadata:
    """Tests for TaskListMetadata dataclass."""

    def test_task_list_metadata_initialization(self):
        """Test that TaskListMetadata initializes with correct default values."""
        metadata = TaskListMetadata(list_id="list123", name="My Tasks")
        assert metadata.list_id == "list123"
        assert metadata.name == "My Tasks"
        assert metadata.is_cached is False
        assert metadata.fetched_at is not None
        assert isinstance(metadata.fetched_at, datetime)

    def test_task_list_metadata_with_cached_flag(self):
        """Test that TaskListMetadata accepts is_cached flag."""
        metadata = TaskListMetadata(list_id="list123", name="My Tasks", is_cached=True)
        assert metadata.list_id == "list123"
        assert metadata.name == "My Tasks"
        assert metadata.is_cached is True

    def test_task_list_metadata_with_custom_timestamp(self):
        """Test that TaskListMetadata accepts custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        metadata = TaskListMetadata(list_id="list123", name="My Tasks", fetched_at=custom_time)
        assert metadata.fetched_at == custom_time

    def test_task_list_metadata_requires_list_id_and_name(self):
        """Test that TaskListMetadata requires list_id and name parameters."""
        with pytest.raises(TypeError):
            TaskListMetadata(list_id="list123")
        with pytest.raises(TypeError):
            TaskListMetadata(name="My Tasks")


class TestTUIApplicationState:
    """Tests for TUIApplicationState dataclass."""

    def test_application_state_initialization(self):
        """Test that TUIApplicationState initializes with correct default values."""
        state = TUIApplicationState()
        assert state.selection is None
        assert state.current_list is None
        assert state.is_loading is False
        assert state.error_message is None

    def test_application_state_with_selection(self):
        """Test that TUIApplicationState can hold selection state."""
        selection = TUISelectionState(task_id="task123")
        state = TUIApplicationState(selection=selection)
        assert state.selection is selection
        assert state.selection.task_id == "task123"

    def test_application_state_with_current_list(self):
        """Test that TUIApplicationState can hold current list metadata."""
        list_metadata = TaskListMetadata(list_id="list123", name="My Tasks")
        state = TUIApplicationState(current_list=list_metadata)
        assert state.current_list is list_metadata
        assert state.current_list.name == "My Tasks"

    def test_application_state_with_loading(self):
        """Test that TUIApplicationState can track loading state."""
        state = TUIApplicationState(is_loading=True)
        assert state.is_loading is True

    def test_application_state_with_error_message(self):
        """Test that TUIApplicationState can hold error message."""
        state = TUIApplicationState(error_message="API error occurred")
        assert state.error_message == "API error occurred"

    def test_application_state_with_all_fields(self):
        """Test that TUIApplicationState can hold all fields."""
        selection = TUISelectionState(task_id="task123")
        list_metadata = TaskListMetadata(list_id="list123", name="My Tasks")
        state = TUIApplicationState(
            selection=selection,
            current_list=list_metadata,
            is_loading=True,
            error_message="Error message",
        )
        assert state.selection is selection
        assert state.current_list is list_metadata
        assert state.is_loading is True
        assert state.error_message == "Error message"
