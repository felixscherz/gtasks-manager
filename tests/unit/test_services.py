from unittest.mock import MagicMock

import pytest

from gtasks_manager.core.services import TaskService


@pytest.fixture
def mock_api():
    return MagicMock()


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.get_task_id.side_effect = (
        lambda ref, comp=False: f"ID_{ref}" if isinstance(ref, int) else ref
    )
    return cache


@pytest.fixture
def service(mock_api, mock_cache):
    return TaskService(mock_api, mock_cache)


def test_list_tasks_updates_cache(service, mock_api, mock_cache):
    mock_api.list_tasks.return_value = []
    service.list_tasks("L1", show_completed=True)

    mock_api.list_tasks.assert_called_once_with("L1", True)
    mock_cache.update.assert_called_once_with([], True)


def test_create_task_delegation(service, mock_api):
    service.create_task("L1", "Title", "Notes")
    mock_api.create_task.assert_called_once_with("L1", "Title", "Notes", None)


def test_complete_task_resolves_reference(service, mock_api, mock_cache):
    service.complete_task("L1", 1)
    mock_api.complete_task.assert_called_once_with("L1", "ID_1")
