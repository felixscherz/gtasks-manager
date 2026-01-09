import pytest
from datetime import datetime, timedelta
from gtasks_manager.core.models import Task, TaskStatus, TaskList, UserCredentials


def test_task_mark_complete():
    task = Task(
        id="1",
        title="Test Task",
        status=TaskStatus.NEEDS_ACTION,
        list_id="L1",
        updated=datetime.utcnow(),
    )
    task.mark_complete()
    assert task.status == TaskStatus.COMPLETED
    assert task.completed is not None


def test_task_mark_incomplete():
    task = Task(
        id="1",
        title="Test Task",
        status=TaskStatus.COMPLETED,
        list_id="L1",
        updated=datetime.utcnow(),
        completed=datetime.utcnow(),
    )
    task.mark_incomplete()
    assert task.status == TaskStatus.NEEDS_ACTION
    assert task.completed is None


def test_task_is_overdue():
    past_due = datetime(2020, 1, 1)
    future_due = datetime(2099, 1, 1)

    task_overdue = Task(
        id="1",
        title="Overdue",
        status=TaskStatus.NEEDS_ACTION,
        list_id="L1",
        updated=datetime.utcnow(),
        due=past_due,
    )
    task_not_overdue = Task(
        id="2",
        title="Not Overdue",
        status=TaskStatus.NEEDS_ACTION,
        list_id="L1",
        updated=datetime.utcnow(),
        due=future_due,
    )
    task_completed = Task(
        id="3",
        title="Completed",
        status=TaskStatus.COMPLETED,
        list_id="L1",
        updated=datetime.utcnow(),
        due=past_due,
    )

    assert task_overdue.is_overdue() is True
    assert task_not_overdue.is_overdue() is False
    assert task_completed.is_overdue() is False


def test_user_credentials_validity():
    future = datetime.utcnow() + timedelta(days=1)
    past = datetime.utcnow() - timedelta(days=1)

    creds_valid = UserCredentials(access_token="abc", scopes=["scope"], token_expiry=future)
    creds_expired = UserCredentials(access_token="abc", scopes=["scope"], token_expiry=past)

    assert creds_valid.is_valid() is True
    assert creds_expired.is_valid() is False


def test_user_credentials_needs_refresh():
    soon = datetime.utcnow() + timedelta(minutes=2)
    far = datetime.utcnow() + timedelta(hours=1)

    creds_needs_refresh = UserCredentials(
        access_token="abc", scopes=["scope"], refresh_token="ref", token_expiry=soon
    )
    creds_no_refresh = UserCredentials(
        access_token="abc", scopes=["scope"], refresh_token="ref", token_expiry=far
    )

    assert creds_needs_refresh.needs_refresh() is True
    assert creds_no_refresh.needs_refresh() is False
