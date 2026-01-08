# Google Tasks API Contract

**Feature**: Google Tasks CLI and TUI Manager  
**Branch**: `001-google-tasks-cli-tui`  
**Date**: 2026-01-07

## Purpose

This document defines the contract between the application and the Google Tasks API. It specifies all API operations, request/response formats, error handling, and adapter interface.

---

## API Base Information

**Base URL**: `https://tasks.googleapis.com`  
**API Version**: `v1`  
**Authentication**: OAuth 2.0  
**Required Scope**: `https://www.googleapis.com/auth/tasks`  
**Rate Limit**: 50,000 queries/day (courtesy limit)

---

## Adapter Protocol

The Google Tasks adapter must implement this protocol to abstract API interactions from the core domain.

```python
from typing import Protocol, List, Optional
from datetime import datetime
from core.models import Task, TaskList

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
    
    def list_tasks(
        self,
        list_id: str,
        show_completed: bool = False
    ) -> List[Task]:
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
        self,
        list_id: str,
        title: str,
        notes: Optional[str] = None,
        due: Optional[datetime] = None
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
        status: Optional[str] = None
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
```

---

## API Operations

### 1. List Task Lists

**Endpoint**: `GET /tasks/v1/users/@me/lists`

**Request**:
```http
GET /tasks/v1/users/@me/lists HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "kind": "tasks#taskLists",
  "etag": "\"LTY4NzM0MjM0\"",
  "items": [
    {
      "kind": "tasks#taskList",
      "id": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
      "etag": "\"LTY4NzM0MjM0\"",
      "title": "My Tasks",
      "updated": "2024-01-07T10:30:00.000Z",
      "selfLink": "https://www.googleapis.com/tasks/v1/users/@me/lists/MDcx..."
    }
  ]
}
```

**Error Responses**:
- `401 UNAUTHENTICATED`: Invalid or expired credentials
- `500 INTERNAL`: Server error (retry with backoff)
- `503 UNAVAILABLE`: Service temporarily unavailable (retry with backoff)

---

### 2. List Tasks

**Endpoint**: `GET /tasks/v1/lists/{taskListId}/tasks`

**Request**:
```http
GET /tasks/v1/lists/{taskListId}/tasks?showCompleted=false&showHidden=false&maxResults=100 HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
```

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `showCompleted` | boolean | No | false | Show completed tasks |
| `showHidden` | boolean | No | false | Show hidden tasks |
| `maxResults` | integer | No | 20 | Max tasks per page (1-100) |
| `pageToken` | string | No | - | Token for pagination |
| `dueMin` | RFC 3339 | No | - | Min due date filter |
| `dueMax` | RFC 3339 | No | - | Max due date filter |
| `updatedMin` | RFC 3339 | No | - | Min updated time filter |

**Response** (200 OK):
```json
{
  "kind": "tasks#tasks",
  "etag": "\"LTY4NzM0MjM0\"",
  "nextPageToken": "CjkKPD...",
  "items": [
    {
      "kind": "tasks#task",
      "id": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
      "etag": "\"LTY4NzM0MjM0\"",
      "title": "Buy groceries",
      "updated": "2024-01-07T10:30:00.000Z",
      "selfLink": "https://www.googleapis.com/tasks/v1/lists/@default/tasks/MDcx...",
      "position": "00000000000000000001",
      "status": "needsAction",
      "due": "2024-01-08T00:00:00.000Z",
      "notes": "Milk, bread, eggs"
    }
  ]
}
```

**Error Responses**:
- `401 UNAUTHENTICATED`: Invalid credentials
- `404 NOT_FOUND`: Task list doesn't exist
- `429 RESOURCE_EXHAUSTED`: Rate limit exceeded (retry with exponential backoff)
- `500 INTERNAL`: Server error (retry)

---

### 3. Get Task

**Endpoint**: `GET /tasks/v1/lists/{taskListId}/tasks/{taskId}`

**Request**:
```http
GET /tasks/v1/lists/{taskListId}/tasks/{taskId} HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "kind": "tasks#task",
  "id": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
  "etag": "\"LTY4NzM0MjM0\"",
  "title": "Buy groceries",
  "updated": "2024-01-07T10:30:00.000Z",
  "selfLink": "https://www.googleapis.com/tasks/v1/lists/@default/tasks/MDcx...",
  "position": "00000000000000000001",
  "status": "needsAction",
  "due": "2024-01-08T00:00:00.000Z",
  "notes": "Milk, bread, eggs"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Task or task list doesn't exist

---

### 4. Create Task

**Endpoint**: `POST /tasks/v1/lists/{taskListId}/tasks`

**Request**:
```http
POST /tasks/v1/lists/{taskListId}/tasks HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Buy groceries",
  "notes": "Milk, bread, eggs",
  "due": "2024-01-08T00:00:00Z"
}
```

**Request Body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Task title (1-1024 chars) |
| `notes` | string | No | Task notes (max 8192 chars) |
| `due` | RFC 3339 | No | Due date (time ignored) |
| `status` | string | No | "needsAction" or "completed" |

**Response** (200 OK):
```json
{
  "kind": "tasks#task",
  "id": "MDcxNzMyMzk1MzUzNjM0Nzg0NDY",
  "etag": "\"LTY4NzM0MjM0\"",
  "title": "Buy groceries",
  "updated": "2024-01-07T10:30:00.000Z",
  "selfLink": "https://www.googleapis.com/tasks/v1/lists/@default/tasks/MDcx...",
  "position": "00000000000000000001",
  "status": "needsAction",
  "due": "2024-01-08T00:00:00.000Z",
  "notes": "Milk, bread, eggs"
}
```

**Error Responses**:
- `400 INVALID_ARGUMENT`: Invalid task data (title too long, invalid date, etc.)
- `404 NOT_FOUND`: Task list doesn't exist

---

### 5. Update Task

**Endpoint**: `PATCH /tasks/v1/lists/{taskListId}/tasks/{taskId}`

**Request**:
```http
PATCH /tasks/v1/lists/{taskListId}/tasks/{taskId} HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Buy groceries and supplies",
  "status": "completed",
  "completed": "2024-01-07T12:00:00Z"
}
```

**Request Body**: Same fields as Create Task (all optional, only include fields to update)

**Response** (200 OK): Same as Create Task response

**Error Responses**:
- `400 INVALID_ARGUMENT`: Invalid update data
- `404 NOT_FOUND`: Task or task list doesn't exist

**Note**: Use `PATCH` for partial updates (recommended). `PUT` requires all fields (not recommended).

---

### 6. Delete Task

**Endpoint**: `DELETE /tasks/v1/lists/{taskListId}/tasks/{taskId}`

**Request**:
```http
DELETE /tasks/v1/lists/{taskListId}/tasks/{taskId} HTTP/1.1
Host: tasks.googleapis.com
Authorization: Bearer {access_token}
```

**Response** (204 No Content): Empty response body

**Error Responses**:
- `404 NOT_FOUND`: Task or task list doesn't exist

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": 404,
    "message": "Task not found",
    "status": "NOT_FOUND",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "TASK_NOT_FOUND",
        "domain": "tasks.googleapis.com",
        "metadata": {
          "taskId": "abc123"
        }
      }
    ]
  }
}
```

### Retry Strategy

**Retry on these errors** (with exponential backoff):
- `429 RESOURCE_EXHAUSTED` - Rate limit exceeded
- `500 INTERNAL` - Server error
- `503 UNAVAILABLE` - Service unavailable
- `504 DEADLINE_EXCEEDED` - Gateway timeout

**Do NOT retry on these errors**:
- `400 INVALID_ARGUMENT` - Bad request data
- `401 UNAUTHENTICATED` - Invalid credentials (trigger re-auth instead)
- `403 PERMISSION_DENIED` - Insufficient permissions
- `404 NOT_FOUND` - Resource doesn't exist

**Exponential Backoff Algorithm**:
```python
def calculate_backoff(attempt: int) -> float:
    """Calculate wait time for retry attempt."""
    import random
    base_delay = 1.0  # 1 second
    max_delay = 60.0  # 60 seconds
    
    # Exponential: 1s, 2s, 4s, 8s, 16s, 32s, 60s (capped)
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    # Add jitter (±10%) to avoid thundering herd
    jitter = delay * 0.1 * random.uniform(-1, 1)
    
    return delay + jitter
```

**Max Retries**: 3 attempts (initial + 2 retries)

---

## Custom Exceptions

The adapter must translate API errors to domain exceptions:

```python
class APIError(Exception):
    """Base exception for API errors."""
    pass

class AuthenticationError(APIError):
    """Authentication failed or credentials invalid."""
    pass

class NotFoundError(APIError):
    """Requested resource not found."""
    pass

class ValidationError(APIError):
    """Request data validation failed."""
    pass

class RateLimitError(APIError):
    """API rate limit exceeded."""
    pass

class NetworkError(APIError):
    """Network connectivity issue."""
    pass
```

**Error Mapping**:

| HTTP Status | Exception | User Message |
|-------------|-----------|--------------|
| 400 | `ValidationError` | "Invalid data. Check your input." |
| 401 | `AuthenticationError` | "Authentication failed. Run 'gtasks auth'." |
| 403 | `AuthenticationError` | "Permission denied. Check your account." |
| 404 | `NotFoundError` | "Task or list not found." |
| 429 | `RateLimitError` | "Rate limit exceeded. Try again in a moment." |
| 500 | `APIError` | "Server error. Please try again." |
| 503 | `APIError` | "Service unavailable. Please try again later." |
| Network | `NetworkError` | "No network connection. Check your internet." |

---

## Authentication Flow

### Initial Authentication

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def authenticate(force_reauth: bool = False) -> UserCredentials:
    """
    Perform OAuth2 authentication flow.
    
    Steps:
    1. Check for existing token in ~/.config/gtasks-manager/token.json
    2. If valid token exists and not force_reauth, use it
    3. If token expired and refresh_token exists, refresh it
    4. Otherwise, run full OAuth flow
    """
    # 1. Try loading existing credentials
    if not force_reauth and token_file.exists():
        creds = Credentials.from_authorized_user_file(
            token_file,
            SCOPES
        )
        
        # 2. Check validity
        if creds and creds.valid:
            return UserCredentials.from_google_creds(creds)
        
        # 3. Try refresh
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                save_credentials(creds)
                return UserCredentials.from_google_creds(creds)
            except Exception:
                # Refresh failed, need full reauth
                pass
    
    # 4. Full OAuth flow
    flow = InstalledAppFlow.from_client_config(
        CLIENT_CONFIG,
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    save_credentials(creds)
    return UserCredentials.from_google_creds(creds)
```

### Token Refresh

The `google-auth` library handles automatic token refresh. The adapter just needs to check validity before each request:

```python
def _ensure_authenticated(self) -> None:
    """Ensure valid credentials before API call."""
    if not self.credentials:
        raise AuthenticationError("Not authenticated. Run 'gtasks auth'.")
    
    if not self.credentials.is_valid():
        if self.credentials.needs_refresh():
            try:
                self.credentials.refresh()
            except Exception as e:
                raise AuthenticationError(f"Token refresh failed: {e}")
        else:
            raise AuthenticationError("Credentials expired. Run 'gtasks auth'.")
```

---

## Pagination Handling

For large task lists, the API returns paginated results:

```python
def list_all_tasks(
    self,
    list_id: str,
    show_completed: bool = False
) -> List[Task]:
    """Fetch all tasks with automatic pagination."""
    all_tasks = []
    page_token = None
    
    while True:
        # Fetch page
        request = self.service.tasks().list(
            tasklist=list_id,
            showCompleted=show_completed,
            showHidden=show_completed,
            maxResults=100,  # Max per page
            pageToken=page_token
        )
        
        response = self._execute_with_retry(request)
        
        # Extract tasks
        items = response.get('items', [])
        all_tasks.extend([
            GoogleTaskDTO(**item).to_domain(list_id)
            for item in items
        ])
        
        # Check for more pages
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return all_tasks
```

---

## Network Connectivity Check

Before making API requests, check if Google's servers are reachable:

```python
import socket

def check_connectivity() -> bool:
    """Check if we can reach Google API servers."""
    try:
        socket.create_connection(
            ("www.googleapis.com", 443),
            timeout=3
        )
        return True
    except OSError:
        return False
```

---

## Summary

**Operations**: 7 (list lists, list tasks, get task, create, update, delete, complete)  
**Authentication**: OAuth2 with automatic token refresh  
**Error Handling**: Exponential backoff for transient errors  
**Pagination**: Automatic handling for large result sets  
**Rate Limits**: 50,000 queries/day with retry on 429

**Adapter Responsibilities**:
1. ✅ Manage OAuth2 authentication and token refresh
2. ✅ Convert between Google API DTOs and domain models
3. ✅ Implement retry logic with exponential backoff
4. ✅ Translate API errors to domain exceptions
5. ✅ Handle pagination automatically
6. ✅ Check network connectivity before requests
7. ✅ Validate request data before sending to API

**Next**: Define TUI event contracts in `contracts/tui-events.md`.
