from datetime import datetime

from gtasks_manager.cli.formatters import CLIFormatter
from gtasks_manager.core.models import Task, TaskList, TaskStatus


def test_format_tasks_empty():
    assert CLIFormatter.format_tasks([]) == "No tasks found."


def test_format_tasks_list():
    tasks = [
        Task(
            id="1",
            list_id="L1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            updated=datetime.utcnow(),
        ),
        Task(
            id="2",
            list_id="L1",
            title="Task 2",
            status=TaskStatus.COMPLETED,
            updated=datetime.utcnow(),
            due=datetime(2024, 1, 1),
        ),
    ]

    output = CLIFormatter.format_tasks(tasks)
    assert "1. ○ Task 1 (ID: 1)" in output
    assert "2. ✓ Task 2 (ID: 2) (due: 2024-01-01)" in output


def test_format_task_lists_empty():
    assert CLIFormatter.format_task_lists([]) == "No task lists found."


def test_format_task_lists():
    lists = [
        TaskList(id="@default", title="Default List", updated=datetime.utcnow()),
        TaskList(id="other", title="Other List", updated=datetime.utcnow()),
    ]
    output = CLIFormatter.format_task_lists(lists)
    assert "1. * Default List (ID: @default)" in output
    assert "2.   Other List (ID: other)" in output


def test_format_success():
    assert CLIFormatter.format_success("Done") == "✓ Done"


def test_format_error():
    assert CLIFormatter.format_error("Fail") == "✗ Error: Fail"
