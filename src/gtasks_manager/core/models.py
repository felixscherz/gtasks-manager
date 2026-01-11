from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union


class UIFocusPane(str, Enum):
    """Represents the different panes in the TUI."""

    SIDEBAR = "sidebar"
    TASK_LIST = "task_list"
    DETAILS = "details"
    INPUT = "input"


@dataclass
class UIFocus:
    """Represents the current UI focus state."""

    pane: UIFocusPane
    index: Optional[int] = None

    def validate_index(self, max_length: int) -> bool:
        """Validate that the index is within bounds.

        Args:
            max_length: The maximum valid index (exclusive)

        Returns:
            True if index is None or within [0, max_length), False otherwise
        """
        if self.index is None:
            return True
        return 0 <= self.index < max_length


class TaskStatus(str, Enum):
    """Task completion status."""

    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"


@dataclass(frozen=False)
class Task:
    """Represents a single todo item in the system."""

    id: str
    title: str
    status: TaskStatus
    list_id: str
    updated: Optional[datetime] = None
    notes: Optional[str] = None
    due: Optional[datetime] = None
    completed: Optional[datetime] = None

    def mark_complete(self) -> None:
        """Mark task as completed."""
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.COMPLETED
            self.completed = datetime.utcnow()

    def mark_incomplete(self) -> None:
        """Mark task as incomplete."""
        if self.status != TaskStatus.NEEDS_ACTION:
            self.status = TaskStatus.NEEDS_ACTION
            self.completed = None

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due or self.status == TaskStatus.COMPLETED:
            return False
        # Compare date only if that's the intention, but here we use datetime
        return datetime.utcnow() > self.due


@dataclass(frozen=False)
class TaskList:
    """Represents a collection of related tasks."""

    id: str
    title: str
    updated: Optional[datetime] = None


@dataclass
class UserCredentials:
    """Represents OAuth2 authentication state."""

    access_token: str
    scopes: List[str]
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if credentials are valid."""
        if not self.access_token:
            return False
        if self.token_expiry and datetime.utcnow() >= self.token_expiry:
            return False
        return True

    def needs_refresh(self) -> bool:
        """Check if token needs refreshing."""
        if not self.refresh_token:
            return False
        if not self.token_expiry:
            return True
        # Refresh if within 5 minutes of expiry
        buffer = timedelta(minutes=5)
        return datetime.utcnow() + buffer >= self.token_expiry


TaskReference = Union[str, int]
