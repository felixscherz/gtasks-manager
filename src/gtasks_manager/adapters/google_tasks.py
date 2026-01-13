from datetime import datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..config import CLIENT_CONFIG, SCOPES, TOKEN_FILE, ensure_config_dir
from ..core.models import Task, TaskList
from ..core.ports import TasksAPIProtocol
from .dtos import GoogleTaskDTO, GoogleTaskListDTO
from .utils import execute_with_retry


class GoogleTasksAdapter(TasksAPIProtocol):
    """Adapter for Google Tasks API using DTOs and retry logic."""

    def __init__(self):
        self._creds: Any | None = None
        self._service: Any = None
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load credentials from token file."""
        if TOKEN_FILE.exists():
            self._creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    self._creds.refresh(Request())
                    self._save_credentials()
                except Exception:
                    self._creds = None

        if self._creds and self._creds.valid:
            self._service = build("tasks", "v1", credentials=self._creds)

    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if not self._creds:
            return
        ensure_config_dir()
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(self._creds.to_json())

    def authenticate(self, force_reauth: bool = False) -> bool:
        """Authenticate with Google Tasks API."""
        if not force_reauth and self._creds and hasattr(self._creds, "valid") and self._creds.valid:
            return True

        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        self._creds = flow.run_local_server(port=0)
        self._save_credentials()
        self._service = build("tasks", "v1", credentials=self._creds)
        return True

    def _ensure_authenticated(self) -> None:
        """Ensure valid service instance."""
        if not self._service:
            self.authenticate()

    def list_task_lists(self) -> list[TaskList]:
        """Get all task lists."""
        self._ensure_authenticated()

        def request():
            return self._service.tasklists().list()

        response = execute_with_retry(request)
        items = response.get("items", [])
        return [GoogleTaskListDTO(**item).to_domain() for item in items]

    def list_tasks(self, list_id: str, show_completed: bool = False) -> list[Task]:
        """Get tasks from a list with pagination."""
        self._ensure_authenticated()
        all_tasks = []
        page_token = None

        while True:
            current_token = page_token

            def request():
                return self._service.tasks().list(
                    tasklist=list_id,
                    showCompleted=show_completed,
                    showHidden=show_completed,
                    pageToken=current_token,
                    maxResults=100,
                )

            response = execute_with_retry(request)
            if response is None:
                break
            items = response.get("items", [])
            all_tasks.extend([GoogleTaskDTO(**item).to_domain(list_id) for item in items])

            if not items:
                break

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return all_tasks

    def get_task(self, list_id: str, task_id: str) -> Task:
        """Get a specific task."""
        self._ensure_authenticated()

        def request():
            return self._service.tasks().get(tasklist=list_id, task=task_id)

        item = execute_with_retry(request)
        return GoogleTaskDTO(**item).to_domain(list_id)

    def create_task(
        self, list_id: str, title: str, notes: str | None = None, due: datetime | None = None
    ) -> Task:
        """Create a new task."""
        self._ensure_authenticated()
        body = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = due.isoformat() + "Z"

        def request():
            return self._service.tasks().insert(tasklist=list_id, body=body)

        item = execute_with_retry(request)
        return GoogleTaskDTO(**item).to_domain(list_id)

    def update_task(
        self,
        list_id: str,
        task_id: str,
        title: str | None = None,
        notes: str | None = None,
        due: datetime | None = None,
        status: str | None = None,
    ) -> Task:
        """Update an existing task."""
        self._ensure_authenticated()
        body = {}
        if title is not None:
            body["title"] = title
        if notes is not None:
            body["notes"] = notes
        if due is not None:
            body["due"] = due.isoformat() + "Z"
        if status is not None:
            body["status"] = status

        def request():
            return self._service.tasks().patch(tasklist=list_id, task=task_id, body=body)

        item = execute_with_retry(request)
        return GoogleTaskDTO(**item).to_domain(list_id)

    def delete_task(self, list_id: str, task_id: str) -> None:
        """Delete a task."""
        self._ensure_authenticated()

        def request():
            return self._service.tasks().delete(tasklist=list_id, task=task_id)

        execute_with_retry(request)

    def complete_task(self, list_id: str, task_id: str) -> Task:
        """Mark task as complete."""
        return self.update_task(list_id, task_id, status="completed")
