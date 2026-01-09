import pytest
from datetime import datetime
from gtasks_manager.core.task_cache import TaskCache
from gtasks_manager.core.models import Task, TaskStatus


@pytest.fixture
def empty_cache():
    return TaskCache(active_tasks={}, completed_tasks={}, last_updated=datetime.utcnow())


def test_cache_update_and_get(empty_cache):
    tasks = [
        Task(
            id="T1",
            title="Task 1",
            status=TaskStatus.NEEDS_ACTION,
            list_id="L1",
            updated=datetime.utcnow(),
        ),
        Task(
            id="T2",
            title="Task 2",
            status=TaskStatus.NEEDS_ACTION,
            list_id="L1",
            updated=datetime.utcnow(),
        ),
    ]
    empty_cache.update(tasks)

    assert empty_cache.get_task_id(1) == "T1"
    assert empty_cache.get_task_id(2) == "T2"
    assert empty_cache.get_task_id("T1") == "T1"


def test_cache_completed_tasks(empty_cache):
    tasks = [
        Task(
            id="T3",
            title="Task 3",
            status=TaskStatus.COMPLETED,
            list_id="L1",
            updated=datetime.utcnow(),
        ),
    ]
    empty_cache.update(tasks, completed=True)

    assert empty_cache.get_task_id(1, completed=True) == "T3"
    assert empty_cache.get_task_id(1, completed=False) is None
