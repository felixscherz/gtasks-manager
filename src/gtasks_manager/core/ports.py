from datetime import datetime
from typing import List, Optional, Protocol

from .models import Task, TaskList


class TasksAPIProtocol(Protocol):
    """Protocol defining the Google Tasks API adapter interface."""

    def authenticate(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with Google Tasks API.

        Args:
            force_reauth: Force re-authentication even if valid token exists

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        ...

    def list_task_lists(self) -> List[TaskList]:
        """
        Get all task lists for the authenticated user.

        Returns:
            List of TaskList objects

        Raises:
            APIError: If API request fails
            AuthenticationError: If not authenticated
        """
        ...

    def list_tasks(self, list_id: str, show_completed: bool = False) -> List[Task]:
        """
        Get tasks from a specific task list.

        Args:
            list_id: Task list identifier
            show_completed: Include completed tasks

        Returns:
            List of Task objects

        Raises:
            APIError: If API request fails
            NotFoundError: If task list doesn't exist
        """
        ...

    def get_task(self, list_id: str, task_id: str) -> Task:
        """
        Get a specific task.

        Args:
            list_id: Task list identifier
            task_id: Task identifier

        Returns:
            Task object

        Raises:
            APIError: If API request fails
            NotFoundError: If task doesn't exist
        """
        ...

    def create_task(
        self, list_id: str, title: str, notes: Optional[str] = None, due: Optional[datetime] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            list_id: Task list identifier
            title: Task title (1-1024 chars)
            notes: Optional task notes (max 8192 chars)
            due: Optional due date

        Returns:
            Created Task object

        Raises:
            APIError: If API request fails
            ValidationError: If task data is invalid
        """
        ...

    def update_task(
        self,
        list_id: str,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> Task:
        """
        Update an existing task.

        Args:
            list_id: Task list identifier
            task_id: Task identifier
            title: New title (if updating)
            notes: New notes (if updating)
            due: New due date (if updating)
            status: New status (if updating)

        Returns:
            Updated Task object

        Raises:
            APIError: If API request fails
            NotFoundError: If task doesn't exist
            ValidationError: If update data is invalid
        """
        ...

    def delete_task(self, list_id: str, task_id: str) -> None:
        """
        Delete a task.

        Args:
            list_id: Task list identifier
            task_id: Task identifier

        Raises:
            APIError: If API request fails
            NotFoundError: If task doesn't exist
        """
        ...

    def complete_task(self, list_id: str, task_id: str) -> Task:
        """
        Mark a task as completed.

        Args:
            list_id: Task list identifier
            task_id: Task identifier

        Returns:
            Updated Task object with completed status

        Raises:
            APIError: If API request fails
            NotFoundError: If task doesn't exist
        """
        ...
