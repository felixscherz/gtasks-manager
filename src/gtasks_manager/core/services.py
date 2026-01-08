from datetime import datetime
from typing import List, Optional

from .models import Task, TaskList, TaskReference
from .ports import TasksAPIProtocol
from .task_cache import TaskCache


class TaskService:
    """Business logic for task management."""

    def __init__(self, api: TasksAPIProtocol, cache: TaskCache):
        self.api = api
        self.cache = cache

    def list_task_lists(self) -> List[TaskList]:
        """Get all task lists."""
        return self.api.list_task_lists()

    def list_tasks(self, list_id: str, show_completed: bool = False) -> List[Task]:
        """List tasks and update cache."""
        tasks = self.api.list_tasks(list_id, show_completed)
        self.cache.update(tasks, show_completed)
        return tasks

    def get_task(self, list_id: str, reference: TaskReference) -> Task:
        """Get a specific task by ID or index."""
        task_id = self.cache.get_task_id(reference)
        if not task_id:
            # Fallback to assuming it's an ID if not in cache (or if int but not in cache)
            task_id = str(reference)
        return self.api.get_task(list_id, task_id)

    def create_task(
        self, list_id: str, title: str, notes: Optional[str] = None, due: Optional[datetime] = None
    ) -> Task:
        """Create a new task."""
        return self.api.create_task(list_id, title, notes, due)

    def update_task(
        self,
        list_id: str,
        reference: TaskReference,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> Task:
        """Update an existing task."""
        task_id = self.cache.get_task_id(reference)
        if not task_id:
            task_id = str(reference)
        return self.api.update_task(list_id, task_id, title, notes, due, status)

    def delete_task(self, list_id: str, reference: TaskReference) -> None:
        """Delete a task."""
        task_id = self.cache.get_task_id(reference)
        if not task_id:
            task_id = str(reference)
        self.api.delete_task(list_id, task_id)

    def complete_task(self, list_id: str, reference: TaskReference) -> Task:
        """Mark a task as completed."""
        task_id = self.cache.get_task_id(reference)
        if not task_id:
            task_id = str(reference)
        return self.api.complete_task(list_id, task_id)
