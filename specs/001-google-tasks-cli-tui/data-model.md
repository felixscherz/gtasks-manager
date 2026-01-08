# Data Model Specification

**Feature**: Google Tasks CLI and TUI Manager  
**Branch**: `001-google-tasks-cli-tui`  
**Date**: 2026-01-07

## Purpose

This document defines the data structures, entities, and their relationships for the Google Tasks CLI/TUI application. All models are designed to be framework-agnostic and represent the domain concepts independently of Google Tasks API or UI implementation details.

---

## Core Domain Models

### 1. Task

Represents a single todo item in the system.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `str` | Yes | - | Unique identifier from Google Tasks API |
| `title` | `str` | Yes | - | Task title (1-1024 characters) |
| `status` | `TaskStatus` | Yes | `NEEDS_ACTION` | Completion status |
| `notes` | `Optional[str]` | No | `None` | Task notes/description (max 8192 chars) |
| `due` | `Optional[datetime]` | No | `None` | Due date (date portion only, time ignored) |
| `completed` | `Optional[datetime]` | No | `None` | Completion timestamp (set when status=COMPLETED) |
| `updated` | `datetime` | Yes | - | Last modification timestamp |
| `list_id` | `str` | Yes | - | Parent task list ID |

**Validation Rules**:
- `title`: Non-empty, max 1024 characters
- `notes`: Max 8192 characters if present
- `completed`: Must be set if status is COMPLETED, must be None if NEEDS_ACTION
- `due`: Time portion is ignored (date only)

**State Transitions**:
```
NEEDS_ACTION ──> COMPLETED (set completed timestamp)
COMPLETED ──> NEEDS_ACTION (clear completed timestamp)
```

**Example**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"

@dataclass(frozen=False)
class Task:
    id: str
    title: str
    status: TaskStatus
    list_id: str
    updated: datetime
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
        return datetime.now() > self.due
```

---

### 2. TaskList

Represents a collection of related tasks.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `str` | Yes | - | Unique identifier from Google Tasks API |
| `title` | `str` | Yes | - | List name |
| `updated` | `datetime` | Yes | - | Last modification timestamp |

**Example**:
```python
@dataclass(frozen=False)
class TaskList:
    id: str
    title: str
    updated: datetime
```

---

### 3. UserCredentials

Represents OAuth2 authentication state.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `access_token` | `str` | Yes | - | OAuth2 access token |
| `refresh_token` | `Optional[str]` | No | `None` | OAuth2 refresh token |
| `token_expiry` | `Optional[datetime]` | No | `None` | When access token expires |
| `scopes` | `List[str]` | Yes | - | Granted OAuth scopes |

**Methods**:
- `is_valid() -> bool`: Check if credentials are valid (not expired)
- `needs_refresh() -> bool`: Check if token needs refreshing

**Example**:
```python
@dataclass
class UserCredentials:
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
```

---

## Value Objects

### TaskStatus Enum

```python
class TaskStatus(str, Enum):
    """Task completion status."""
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"
```

**Notes**:
- Uses Google Tasks API status values directly
- String enum for easy serialization
- Only two states (no partial completion)

---

### TaskReference

Union type for referencing tasks by ID or index.

```python
from typing import Union

TaskReference = Union[str, int]
```

**Usage**:
- `str`: Task ID from Google API (e.g., "MDcxNzMyMz...")
- `int`: Index number from CLI list output (e.g., 1, 2, 3...)

**Conversion Logic**:
```python
def resolve_task_reference(
    reference: TaskReference,
    cache: TaskCache
) -> Optional[str]:
    """Convert TaskReference to task ID."""
    if isinstance(reference, int):
        return cache.get_task_id_by_index(reference)
    return reference  # Already a task ID
```

---

## Data Transfer Objects (DTOs)

### Google API DTOs (for adapter layer)

These use Pydantic for validation and are used only in the adapter layer to interact with Google Tasks API.

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GoogleTaskDTO(BaseModel):
    """Google Tasks API task representation."""
    id: str
    title: str
    status: str
    updated: str
    notes: Optional[str] = None
    due: Optional[str] = None
    completed: Optional[str] = None
    parent: Optional[str] = None
    position: Optional[str] = None
    links: Optional[List[dict]] = None
    
    class Config:
        # Allow extra fields from API we don't use
        extra = "allow"
    
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
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    @classmethod
    def from_domain(cls, task: Task) -> dict:
        """Convert domain Task to Google API format."""
        data = {
            'title': task.title,
            'status': task.status.value,
        }
        if task.notes:
            data['notes'] = task.notes
        if task.due:
            data['due'] = task.due.isoformat() + 'Z'
        if task.completed:
            data['completed'] = task.completed.isoformat() + 'Z'
        return data


class GoogleTaskListDTO(BaseModel):
    """Google Tasks API task list representation."""
    id: str
    title: str
    updated: str
    
    class Config:
        extra = "allow"
    
    def to_domain(self) -> TaskList:
        """Convert to domain TaskList model."""
        return TaskList(
            id=self.id,
            title=self.title,
            updated=datetime.fromisoformat(self.updated.replace('Z', '+00:00')),
        )
```

---

## Cache Models

### TaskCache

Local cache for task index-to-ID mapping (for CLI usability).

**Purpose**: Allow users to reference tasks by number (1, 2, 3) instead of long Google IDs

**Structure**:
```json
{
  "active_tasks": {
    "1": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
    "2": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
    "3": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY"
  },
  "completed_tasks": {
    "1": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
    "2": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY"
  },
  "last_updated": "2024-01-07T10:30:00Z"
}
```

**Model**:
```python
@dataclass
class TaskCache:
    active_tasks: Dict[int, str]  # index -> task_id
    completed_tasks: Dict[int, str]
    last_updated: datetime
    
    def get_task_id(self, reference: TaskReference, completed: bool = False) -> Optional[str]:
        """Get task ID from reference (int index or str ID)."""
        if isinstance(reference, str):
            return reference  # Already an ID
        
        cache = self.completed_tasks if completed else self.active_tasks
        return cache.get(reference)
    
    def update(self, tasks: List[Task], completed: bool = False) -> None:
        """Update cache with task list."""
        cache = {}
        for idx, task in enumerate(tasks, start=1):
            cache[idx] = task.id
        
        if completed:
            self.completed_tasks = cache
        else:
            self.active_tasks = cache
        
        self.last_updated = datetime.utcnow()
```

---

## Entity Relationships

```
UserCredentials (1) ─────> (*) TaskList
                                  │
                                  │ contains
                                  ↓
                                (*) Task

TaskCache ─────references────> (*) Task (by ID)
```

**Relationships**:
1. **UserCredentials → TaskList**: One user has many task lists
2. **TaskList → Task**: One task list contains many tasks
3. **TaskCache → Task**: Cache references tasks by ID for index lookup

---

## Data Validation

### Task Validation

```python
class InvalidTaskError(ValueError):
    """Raised when task data is invalid."""
    pass

def validate_task(task: Task) -> None:
    """Validate task data."""
    if not task.title or len(task.title) > 1024:
        raise InvalidTaskError("Title must be 1-1024 characters")
    
    if task.notes and len(task.notes) > 8192:
        raise InvalidTaskError("Notes must be max 8192 characters")
    
    if task.status == TaskStatus.COMPLETED and not task.completed:
        raise InvalidTaskError("Completed task must have completion timestamp")
    
    if task.status == TaskStatus.NEEDS_ACTION and task.completed:
        raise InvalidTaskError("Incomplete task cannot have completion timestamp")
```

---

## Serialization

### To/From JSON

```python
from dataclasses import asdict, fields
import json

def task_to_dict(task: Task) -> dict:
    """Convert task to JSON-serializable dict."""
    data = asdict(task)
    # Convert datetime to ISO format
    data['updated'] = task.updated.isoformat()
    if task.due:
        data['due'] = task.due.isoformat()
    if task.completed:
        data['completed'] = task.completed.isoformat()
    data['status'] = task.status.value
    return data

def task_from_dict(data: dict) -> Task:
    """Create task from dict."""
    return Task(
        id=data['id'],
        title=data['title'],
        status=TaskStatus(data['status']),
        list_id=data['list_id'],
        updated=datetime.fromisoformat(data['updated']),
        notes=data.get('notes'),
        due=datetime.fromisoformat(data['due']) if data.get('due') else None,
        completed=datetime.fromisoformat(data['completed']) if data.get('completed') else None,
    )
```

---

## Storage Formats

### Token Storage (`token.json`)

```json
{
  "token": "ya29.a0AfH6SMBx...",
  "refresh_token": "1//0gZ9...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "281058803066-...",
  "client_secret": "GOCSPX-...",
  "scopes": ["https://www.googleapis.com/auth/tasks"],
  "expiry": "2024-01-07T11:30:00Z"
}
```

### Task Cache Storage (`task_cache.json`)

```json
{
  "active_tasks": {
    "1": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
    "2": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
    "3": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY"
  },
  "completed_tasks": {},
  "last_updated": "2024-01-07T10:30:00Z"
}
```

---

## Summary

**Core Models**: 3 (Task, TaskList, UserCredentials)  
**Value Objects**: 2 (TaskStatus, TaskReference)  
**DTOs**: 2 (GoogleTaskDTO, GoogleTaskListDTO)  
**Cache Models**: 1 (TaskCache)

All models are designed to:
- ✅ Be framework-agnostic (no Click/Textual dependencies)
- ✅ Use Python stdlib types (dataclasses, datetime, enum)
- ✅ Separate domain from API representation (DTOs for conversion)
- ✅ Support validation and state management
- ✅ Enable easy testing with simple constructors

**Next**: Define API interaction contracts in `contracts/` directory.
