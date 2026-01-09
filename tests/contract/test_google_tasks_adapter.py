import pytest
from unittest.mock import MagicMock, patch
from gtasks_manager.adapters.google_tasks import GoogleTasksAdapter
from gtasks_manager.core.exceptions import NotFoundError, AuthenticationError


@pytest.fixture
def adapter():
    with patch("gtasks_manager.adapters.google_tasks.build") as mock_build:
        adapter = GoogleTasksAdapter()
        adapter._service = MagicMock()
        yield adapter


def test_list_task_lists_success(adapter):
    adapter._service.tasklists().list().execute.return_value = {
        "items": [{"id": "L1", "title": "List 1", "updated": "2024-01-01T00:00:00.000Z"}]
    }
    lists = adapter.list_task_lists()
    assert len(lists) == 1
    assert lists[0].id == "L1"


def test_list_tasks_pagination(adapter):
    adapter._service.tasks().list().execute.side_effect = [
        {
            "items": [
                {
                    "id": "T1",
                    "title": "T1",
                    "status": "needsAction",
                    "updated": "2024-01-01T00:00:00.000Z",
                }
            ],
            "nextPageToken": "token",
        },
        {
            "items": [
                {
                    "id": "T2",
                    "title": "T2",
                    "status": "needsAction",
                    "updated": "2024-01-01T00:00:00.000Z",
                }
            ]
        },
    ]
    tasks = adapter.list_tasks("L1")
    assert len(tasks) == 2
    assert adapter._service.tasks().list.call_count == 2


def test_get_task_not_found(adapter):
    from googleapiclient.errors import HttpError

    mock_resp = MagicMock()
    mock_resp.status = 404
    adapter._service.tasks().get().execute.side_effect = HttpError(
        resp=mock_resp, content=b"Not Found"
    )

    with pytest.raises(NotFoundError):
        adapter.get_task("L1", "T1")
