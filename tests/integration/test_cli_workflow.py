from datetime import datetime
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from gtasks_manager.cli.main import cli
from gtasks_manager.core.models import Task, TaskList, TaskStatus


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_service(mocker):
    service = MagicMock()
    mocker.patch("gtasks_manager.cli.main._service", service)
    return service


def test_cli_list_tasks(runner, mock_service):
    mock_service.list_tasks.return_value = [
        Task(
            id="1",
            list_id="@default",
            title="Test Task",
            status=TaskStatus.NEEDS_ACTION,
            updated=datetime.utcnow(),
        )
    ]

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "1. ○ Test Task (ID: 1)" in result.output
    mock_service.list_tasks.assert_called_once_with("@default", show_completed=False)


def test_cli_create_task(runner, mock_service):
    mock_service.create_task.return_value = Task(
        id="new-id",
        list_id="@default",
        title="New Task",
        status=TaskStatus.NEEDS_ACTION,
        updated=datetime.utcnow(),
    )

    result = runner.invoke(cli, ["create", "New Task"])

    assert result.exit_code == 0
    assert "✓ Created: New Task (ID: new-id)" in result.output


def test_cli_complete_task(runner, mock_service):
    mock_service.complete_task.return_value = Task(
        id="1",
        list_id="@default",
        title="Test Task",
        status=TaskStatus.COMPLETED,
        updated=datetime.utcnow(),
    )

    result = runner.invoke(cli, ["complete", "1"])

    assert result.exit_code == 0
    assert "✓ Completed: Test Task" in result.output
    mock_service.complete_task.assert_called_once_with("@default", 1)


def test_cli_lists(runner, mock_service):
    mock_service.list_task_lists.return_value = [
        TaskList(id="@default", title="Default List", updated=datetime.utcnow())
    ]

    result = runner.invoke(cli, ["lists"])

    assert result.exit_code == 0
    assert "1. * Default List (ID: @default)" in result.output
