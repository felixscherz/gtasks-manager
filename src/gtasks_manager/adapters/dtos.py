from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from gtasks_manager.core.models import Task, TaskList, TaskStatus


class GoogleTaskDTO(BaseModel):
    """Google Tasks API task representation."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    status: str
    updated: str
    notes: Optional[str] = None
    due: Optional[str] = None
    completed: Optional[str] = None
    parent: Optional[str] = None
    position: Optional[str] = None

    def to_domain(self, list_id: str) -> Task:
        """Convert to domain Task model."""
        return Task(
            id=self.id,
            title=self.title,
            status=TaskStatus(self.status),
            list_id=list_id,
            updated=self._parse_datetime(self.updated),
            notes=self.notes,
            due=self._parse_datetime(self.due) if self.due else None,
            completed=self._parse_datetime(self.completed) if self.completed else None,
        )

    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Parse RFC 3339 datetime string."""
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

    @classmethod
    def from_domain(cls, task: Task) -> dict:
        """Convert domain Task to Google API format."""
        data = {
            "title": task.title,
            "status": task.status.value,
        }
        if task.notes:
            data["notes"] = task.notes
        if task.due:
            data["due"] = task.due.isoformat() + "Z"
        if task.completed:
            data["completed"] = task.completed.isoformat() + "Z"
        return data


class GoogleTaskListDTO(BaseModel):
    """Google Tasks API task list representation."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    updated: str

    def to_domain(self) -> TaskList:
        """Convert to domain TaskList model."""
        return TaskList(
            id=self.id,
            title=self.title,
            updated=datetime.fromisoformat(self.updated.replace("Z", "+00:00")),
        )
