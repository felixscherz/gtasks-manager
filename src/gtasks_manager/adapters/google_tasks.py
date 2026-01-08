from datetime import datetime
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..core.exceptions import APIError, AuthenticationError, NotFoundError, ValidationError
from ..core.models import Task, TaskList
from ..core.ports import TasksAPIProtocol
from ..config import CLIENT_CONFIG, SCOPES, TOKEN_FILE, ensure_config_dir


class GoogleTasksAdapter(TasksAPIProtocol):
    """Adapter for Google Tasks API."""

    def __init__(self):
        self._creds: Optional[Credentials] = None
        self._service = None
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
        ensure_config_dir()
        with open(TOKEN_FILE, "w") as f:
            f.write(self._creds.to_json())

    def authenticate(self, force_reauth: bool = False) -> bool:
        """Authenticate with Google Tasks API."""
        if not force_reauth and self._creds and self._creds.valid:
            return True

        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        self._creds = flow.run_local_server(port=0)
        self._save_credentials()
        self._service = build("tasks", "v1", credentials=self._creds)
        return True

    def _ensure_authenticated(self) -> None:
        """Check if authenticated."""
        if not self._service:
            if not self.authenticate():
                raise AuthenticationError("Not authenticated. Run 'gtasks auth'.")

    def list_task_lists(self) -> List[TaskList]:
        """Get all task lists."""
        self._ensure_authenticated()
        try:
            results = self._service.tasklists().list().execute()
            items = results.get("items", [])
            # For now returning simple models, DTOs will come in T014
            return [
                TaskList(
                    id=item["id"],
                    title=item["title"],
                    updated=datetime.fromisoformat(item["updated"].replace("Z", "+00:00")),
                )
                for item in items
            ]
        except HttpError as e:
            raise APIError(f"API Error: {e}")

    def list_tasks(self, list_id: str, show_completed: bool = False) -> List[Task]:
        """Get tasks from a list."""
        self._ensure_authenticated()
        try:
            results = (
                self._service.tasks()
                .list(tasklist=list_id, showCompleted=show_completed, showHidden=show_completed)
                .execute()
            )
            items = results.get("items", [])
            return [
                Task(
                    id=item["id"],
                    title=item["title"],
                    status=item["status"],
                    list_id=list_id,
                    updated=datetime.fromisoformat(item["updated"].replace("Z", "+00:00")),
                    notes=item.get("notes"),
                    due=datetime.fromisoformat(item["due"].replace("Z", "+00:00"))
                    if "due" in item
                    else None,
                    completed=datetime.fromisoformat(item["completed"].replace("Z", "+00:00"))
                    if "completed" in item
                    else None,
                )
                for item in items
            ]
        except HttpError as e:
            if e.resp.status == 404:
                raise NotFoundError(f"Task list {list_id} not found")
            raise APIError(f"API Error: {e}")

    def get_task(self, list_id: str, task_id: str) -> Task:
        """Get a specific task."""
        self._ensure_authenticated()
        try:
            item = self._service.tasks().get(tasklist=list_id, task=task_id).execute()
            return Task(
                id=item["id"],
                title=item["title"],
                status=item["status"],
                list_id=list_id,
                updated=datetime.fromisoformat(item["updated"].replace("Z", "+00:00")),
                notes=item.get("notes"),
                due=datetime.fromisoformat(item["due"].replace("Z", "+00:00"))
                if "due" in item
                else None,
                completed=datetime.fromisoformat(item["completed"].replace("Z", "+00:00"))
                if "completed" in item
                else None,
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise APIError(f"API Error: {e}")

    def create_task(
        self, list_id: str, title: str, notes: Optional[str] = None, due: Optional[datetime] = None
    ) -> Task:
        """Create a new task."""
        self._ensure_authenticated()
        body = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = due.isoformat() + "Z"
        try:
            item = self._service.tasks().insert(tasklist=list_id, body=body).execute()
            return self.get_task(list_id, item["id"])
        except HttpError as e:
            if e.resp.status == 400:
                raise ValidationError(f"Invalid task data: {e}")
            raise APIError(f"API Error: {e}")

    def update_task(
        self,
        list_id: str,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        status: Optional[str] = None,
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

        try:
            self._service.tasks().patch(tasklist=list_id, task=task_id, body=body).execute()
            return self.get_task(list_id, task_id)
        except HttpError as e:
            if e.resp.status == 404:
                raise NotFoundError(f"Task {task_id} not found")
            if e.resp.status == 400:
                raise ValidationError(f"Invalid update data: {e}")
            raise APIError(f"API Error: {e}")

    def delete_task(self, list_id: str, task_id: str) -> None:
        """Delete a task."""
        self._ensure_authenticated()
        try:
            self._service.tasks().delete(tasklist=list_id, task=task_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise APIError(f"API Error: {e}")

    def complete_task(self, list_id: str, task_id: str) -> Task:
        """Mark task as complete."""
        return self.update_task(list_id, task_id, status="completed")
