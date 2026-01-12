# Architecture Guide: Python CLI/TUI with Shared Business Logic

This guide provides architecture patterns for building a Python application with multiple interfaces (CLI and TUI) sharing business logic, specifically for the gtasks-manager project.

## Table of Contents

1. [Architectural Pattern: Hexagonal Architecture](#1-architectural-pattern-hexagonal-architecture)
2. [Service Layer Patterns](#2-service-layer-patterns)
3. [Data Model Serialization](#3-data-model-serialization)
4. [Cache Invalidation & State Management](#4-cache-invalidation--state-management)
5. [Configuration Sharing](#5-configuration-sharing)
6. [Error Propagation](#6-error-propagation)
7. [Dependency Management](#7-dependency-management)
8. [Project Structure](#8-project-structure)
9. [Testing Strategy](#9-testing-strategy)

---

## 1. Architectural Pattern: Hexagonal Architecture

### Core Concepts

**Hexagonal Architecture** (aka Ports & Adapters, Clean Architecture, Onion Architecture) organizes code into layers with dependencies flowing **inward** toward the domain.

```
┌─────────────────────────────────────────┐
│      Entrypoints (CLI, TUI, API)        │ ← Adapters (Primary/Driving)
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         Service Layer                    │ ← Orchestration
│  (Use Cases / Application Services)      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         Domain Model                     │ ← Business Logic (Core)
│  (Entities, Value Objects, Domain Svc)   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│    Adapters (Secondary/Driven)           │ ← Infrastructure
│  (Repository, Email, Cache, Google API)  │
└──────────────────────────────────────────┘
```

### Key Principles

1. **Dependencies point inward**: Domain has NO dependencies on infrastructure
2. **Abstractions at boundaries**: Use ABCs/Protocols for ports
3. **Dependency Inversion**: High-level modules don't depend on low-level modules

### Example Structure

```python
# Domain Layer - NO external dependencies
# src/gtasks_manager/domain/model.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Pure domain entity - no Google API knowledge"""
    id: Optional[str]
    title: str
    notes: Optional[str]
    due_date: Optional[datetime]
    status: str = 'needsAction'

    def mark_complete(self) -> None:
        """Domain logic lives here"""
        self.status = 'completed'

    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        return self.due_date < datetime.now()

# Domain Service - complex business logic
# src/gtasks_manager/domain/services.py
from typing import List

def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    """Domain service: pure business logic"""
    overdue = [t for t in tasks if t.is_overdue()]
    today = [t for t in tasks if not t.is_overdue() and t.due_date]
    no_date = [t for t in tasks if not t.due_date]
    return overdue + today + no_date
```

---

## 2. Service Layer Patterns

### Pattern: Use Case Functions with Explicit Dependencies

The service layer orchestrates domain logic and coordinates with infrastructure.

```python
# src/gtasks_manager/service_layer/services.py
from typing import Protocol
from ..domain.model import Task
from ..domain import services as domain_services

# Define ports (abstractions)
class TaskRepository(Protocol):
    """Port: defines what we need, not how it's done"""
    def get(self, task_id: str) -> Task: ...
    def list(self) -> list[Task]: ...
    def add(self, task: Task) -> None: ...
    def update(self, task: Task) -> None: ...

class UnitOfWork(Protocol):
    """Port: transaction boundary"""
    tasks: TaskRepository

    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, *args): ...

# Service layer functions
def list_tasks(
    uow: UnitOfWork,
    show_completed: bool = False
) -> list[Task]:
    """Use case: List tasks with optional filtering"""
    with uow:
        tasks = uow.tasks.list()

        if not show_completed:
            tasks = [t for t in tasks if t.status != 'completed']

        # Use domain service for sorting
        tasks = domain_services.prioritize_tasks(tasks)

        return tasks

def create_task(
    title: str,
    notes: str | None,
    due_date: datetime | None,
    uow: UnitOfWork
) -> Task:
    """Use case: Create a new task"""
    task = Task(
        id=None,
        title=title,
        notes=notes,
        due_date=due_date
    )

    with uow:
        uow.tasks.add(task)
        uow.commit()

    return task

def complete_task(
    task_id: str,
    uow: UnitOfWork
) -> None:
    """Use case: Mark task as complete"""
    with uow:
        task = uow.tasks.get(task_id)
        task.mark_complete()  # Domain logic
        uow.tasks.update(task)
        uow.commit()
```

### Alternative Pattern: Service Classes

If you prefer classes over functions:

```python
# src/gtasks_manager/service_layer/services.py
from typing import Protocol

class TaskService:
    """Application service as a class"""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_tasks(self, show_completed: bool = False) -> list[Task]:
        with self.uow:
            tasks = self.uow.tasks.list()

            if not show_completed:
                tasks = [t for t in tasks if t.status != 'completed']

            return domain_services.prioritize_tasks(tasks)

    def create_task(
        self,
        title: str,
        notes: str | None = None,
        due_date: datetime | None = None
    ) -> Task:
        task = Task(id=None, title=title, notes=notes, due_date=due_date)

        with self.uow:
            self.uow.tasks.add(task)
            self.uow.commit()

        return task
```

**Recommendation**: Use **functions** for stateless use cases (simpler, easier to test). Use **classes** only if you need to share state across operations.

---

## 3. Data Model Serialization

### Comparison: dataclasses vs Pydantic vs attrs

| Feature | dataclasses | Pydantic | attrs |
|---------|-------------|----------|-------|
| **Validation** | No | Yes (runtime) | No (unless custom) |
| **Type coercion** | No | Yes | No |
| **JSON serialization** | Manual | Built-in | Manual |
| **Performance** | Fast | Slower | Fast |
| **Complexity** | Low | Medium | Low-Medium |
| **Stdlib** | Yes (3.7+) | No | No |
| **Best for** | Internal models | API boundaries | Internal models |

### Recommendation: Use Both

Use **dataclasses** for domain models, **Pydantic** for API boundaries.

```python
# Domain Model - Simple dataclass
# src/gtasks_manager/domain/model.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Pure domain entity"""
    id: Optional[str]
    title: str
    notes: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = 'needsAction'
    completed_date: Optional[datetime] = None

    def mark_complete(self) -> None:
        self.status = 'completed'
        self.completed_date = datetime.now()

# Google API Response Model - Pydantic for validation
# src/gtasks_manager/adapters/google_api_schema.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class GoogleTaskSchema(BaseModel):
    """Validates Google API responses"""
    id: str
    title: str
    notes: Optional[str] = None
    due: Optional[str] = None  # RFC 3339 format
    status: str
    completed: Optional[str] = None

    @field_validator('due', 'completed', mode='before')
    @classmethod
    def parse_rfc3339(cls, v: str | None) -> datetime | None:
        if not v:
            return None
        return datetime.fromisoformat(v.replace('Z', '+00:00'))

    class Config:
        # Don't allow extra fields from Google
        extra = 'forbid'

# Adapter: Convert between representations
# src/gtasks_manager/adapters/google_tasks.py
from ..domain.model import Task

class GoogleTasksAdapter:
    """Converts between domain and Google API models"""

    @staticmethod
    def to_domain(google_task: GoogleTaskSchema) -> Task:
        """Google API → Domain Model"""
        return Task(
            id=google_task.id,
            title=google_task.title,
            notes=google_task.notes,
            due_date=google_task.due,
            status=google_task.status,
            completed_date=google_task.completed
        )

    @staticmethod
    def from_domain(task: Task) -> dict:
        """Domain Model → Google API dict"""
        result = {
            'title': task.title,
            'status': task.status,
        }

        if task.notes:
            result['notes'] = task.notes

        if task.due_date:
            result['due'] = task.due_date.isoformat() + 'Z'

        return result
```

### Why This Approach?

1. **Domain stays pure**: No validation library pollution
2. **Type safety at boundaries**: Pydantic catches API changes
3. **Performance**: Dataclasses are fast; validation only where needed
4. **Explicit conversion**: Adapter pattern makes transformations clear

---

## 4. Cache Invalidation & State Management

### Problem

CLI modifies tasks → TUI needs to know → How to synchronize?

### Solution Options

#### Option 1: File-Based Event Bus (Simplest)

```python
# src/gtasks_manager/adapters/file_event_bus.py
from pathlib import Path
from datetime import datetime
import json
from typing import Callable

class FileEventBus:
    """Simple file-based events for process communication"""

    def __init__(self, event_dir: Path):
        self.event_dir = event_dir
        self.event_dir.mkdir(parents=True, exist_ok=True)

    def publish(self, event_type: str, data: dict) -> None:
        """Write event to file"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        event_file = self.event_dir / f"{event_type}_{datetime.now().timestamp()}.json"
        event_file.write_text(json.dumps(event))

    def poll_events(self, since: datetime) -> list[dict]:
        """Read events since timestamp"""
        events = []

        for event_file in self.event_dir.glob('*.json'):
            # Parse timestamp from filename
            timestamp = float(event_file.stem.split('_')[-1])

            if datetime.fromtimestamp(timestamp) > since:
                events.append(json.loads(event_file.read_text()))

        return sorted(events, key=lambda e: e['timestamp'])

    def clear_old_events(self, before: datetime) -> None:
        """Cleanup old event files"""
        for event_file in self.event_dir.glob('*.json'):
            timestamp = float(event_file.stem.split('_')[-1])
            if datetime.fromtimestamp(timestamp) < before:
                event_file.unlink()

# Usage in CLI
def create_task_cli(title: str, event_bus: FileEventBus):
    task = create_task(title=title, uow=real_uow)
    event_bus.publish('task_created', {'task_id': task.id})

# Usage in TUI
class TaskTUI:
    def __init__(self, event_bus: FileEventBus):
        self.event_bus = event_bus
        self.last_check = datetime.now()
        self.cached_tasks = []

    def refresh_if_needed(self):
        events = self.event_bus.poll_events(since=self.last_check)

        if any(e['type'] in ['task_created', 'task_updated', 'task_deleted']
               for e in events):
            self.cached_tasks = list_tasks(uow=real_uow)
            self.last_check = datetime.now()
```

#### Option 2: SQLite for Shared State (More Robust)

```python
# src/gtasks_manager/adapters/cache.py
import sqlite3
from pathlib import Path
from datetime import datetime
from ..domain.model import Task
import json

class SQLiteCache:
    """SQLite-backed cache with change tracking"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

    def set_tasks(self, tasks: list[Task]) -> None:
        """Update cache with new task list"""
        with sqlite3.connect(self.db_path) as conn:
            # Clear old tasks
            conn.execute('DELETE FROM tasks')

            # Insert new tasks
            for task in tasks:
                conn.execute(
                    'INSERT INTO tasks (id, data) VALUES (?, ?)',
                    (task.id, json.dumps(task.__dict__))
                )

            # Update timestamp
            conn.execute(
                'REPLACE INTO cache_metadata (key, value) VALUES (?, ?)',
                ('last_sync', datetime.now().isoformat())
            )

    def get_tasks(self) -> list[Task]:
        """Retrieve cached tasks"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('SELECT data FROM tasks').fetchall()
            return [Task(**json.loads(row[0])) for row in rows]

    def get_last_sync(self) -> datetime | None:
        """When was cache last updated?"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                'SELECT value FROM cache_metadata WHERE key = ?',
                ('last_sync',)
            ).fetchone()

            if row:
                return datetime.fromisoformat(row[0])
            return None

    def invalidate(self) -> None:
        """Mark cache as stale"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache_metadata WHERE key = ?', ('last_sync',))

# Service layer integration
def list_tasks_cached(
    uow: UnitOfWork,
    cache: SQLiteCache,
    max_age_seconds: int = 60
) -> list[Task]:
    """List tasks with caching"""
    last_sync = cache.get_last_sync()

    # Use cache if fresh enough
    if last_sync and (datetime.now() - last_sync).seconds < max_age_seconds:
        return cache.get_tasks()

    # Otherwise refresh
    tasks = list_tasks(uow=uow)
    cache.set_tasks(tasks)
    return tasks
```

#### Option 3: Message Bus Pattern (Most Sophisticated)

For complex scenarios with many event types:

```python
# src/gtasks_manager/service_layer/message_bus.py
from typing import Callable, Dict, Type
from dataclasses import dataclass

@dataclass
class Event:
    """Base event"""
    pass

@dataclass
class TaskCreated(Event):
    task_id: str
    title: str

@dataclass
class TaskCompleted(Event):
    task_id: str

class MessageBus:
    """In-process event bus"""

    def __init__(self):
        self.handlers: Dict[Type[Event], list[Callable]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def publish(self, event: Event):
        for handler in self.handlers.get(type(event), []):
            handler(event)

# Usage
bus = MessageBus()

def invalidate_cache(event: TaskCreated | TaskCompleted):
    cache.invalidate()

bus.subscribe(TaskCreated, invalidate_cache)
bus.subscribe(TaskCompleted, invalidate_cache)

# In service layer
def create_task_with_events(title: str, uow: UnitOfWork, bus: MessageBus) -> Task:
    task = create_task(title, uow)
    bus.publish(TaskCreated(task_id=task.id, title=task.title))
    return task
```

### Recommendation

- **Simple app**: Option 1 (File-based)
- **Growing app**: Option 2 (SQLite cache)
- **Complex app**: Option 3 (Message bus) + Option 2

---

## 5. Configuration Sharing

### Pattern: Centralized Config with Environment Override

```python
# src/gtasks_manager/config.py
from pathlib import Path
from dataclasses import dataclass
import os

@dataclass
class Config:
    """Application configuration"""
    # Paths
    config_dir: Path
    cache_dir: Path
    token_file: Path

    # Google API
    google_client_id: str
    google_client_secret: str
    google_scopes: list[str]

    # Cache settings
    cache_max_age_seconds: int

    @classmethod
    def from_env(cls) -> 'Config':
        """Build config from environment variables"""
        config_dir = Path(
            os.getenv('GTASKS_CONFIG_DIR', Path.home() / '.config' / 'gtasks-manager')
        )
        config_dir.mkdir(parents=True, exist_ok=True)

        cache_dir = Path(
            os.getenv('GTASKS_CACHE_DIR', Path.home() / '.cache' / 'gtasks-manager')
        )
        cache_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            config_dir=config_dir,
            cache_dir=cache_dir,
            token_file=config_dir / 'token.json',
            google_client_id=os.getenv(
                'GOOGLE_CLIENT_ID',
                '1234-default.apps.googleusercontent.com'
            ),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'default-secret'),
            google_scopes=['https://www.googleapis.com/auth/tasks'],
            cache_max_age_seconds=int(os.getenv('GTASKS_CACHE_TTL', '60'))
        )

# Default instance
default_config = Config.from_env()

# Usage in adapters
def get_google_service(config: Config = default_config):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(
        str(config.token_file),
        config.google_scopes
    )

    return build('tasks', 'v1', credentials=creds)
```

### Testing Override

```python
# tests/conftest.py
import pytest
from pathlib import Path
from gtasks_manager.config import Config

@pytest.fixture
def test_config(tmp_path: Path) -> Config:
    """Test config with temp directories"""
    return Config(
        config_dir=tmp_path / 'config',
        cache_dir=tmp_path / 'cache',
        token_file=tmp_path / 'config' / 'token.json',
        google_client_id='test-client',
        google_client_secret='test-secret',
        google_scopes=['test-scope'],
        cache_max_age_seconds=0  # No caching in tests
    )
```

---

## 6. Error Propagation

### Pattern: Custom Exception Hierarchy + Result Type

```python
# src/gtasks_manager/domain/exceptions.py
class DomainException(Exception):
    """Base for domain errors"""
    pass

class TaskNotFoundError(DomainException):
    """Task doesn't exist"""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")

class InvalidTaskError(DomainException):
    """Task data is invalid"""
    pass

# src/gtasks_manager/adapters/exceptions.py
class AdapterException(Exception):
    """Base for infrastructure errors"""
    pass

class GoogleAPIError(AdapterException):
    """Google API communication failed"""
    pass

class CacheError(AdapterException):
    """Cache operation failed"""
    pass

# Service layer - Translate exceptions
# src/gtasks_manager/service_layer/services.py
from ..domain.exceptions import TaskNotFoundError
from ..adapters.exceptions import GoogleAPIError

def get_task(task_id: str, uow: UnitOfWork) -> Task:
    """Get task by ID"""
    try:
        with uow:
            task = uow.tasks.get(task_id)

            if not task:
                raise TaskNotFoundError(task_id)

            return task

    except GoogleAPIError as e:
        # Log infrastructure error
        logger.error(f"Google API error: {e}")
        # Re-raise as domain error
        raise TaskNotFoundError(task_id) from e

# CLI - Handle errors gracefully
# src/gtasks_manager/entrypoints/cli.py
import click
from ..domain.exceptions import TaskNotFoundError, DomainException
from ..adapters.exceptions import AdapterException

@click.command()
@click.argument('task_id')
def get_task_command(task_id: str):
    """Get task by ID"""
    try:
        task = get_task(task_id, uow=real_uow)
        click.echo(f"{task.title}")

    except TaskNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    except DomainException as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    except AdapterException as e:
        click.echo(f"System error: {e}", err=True)
        click.echo("Please try again later", err=True)
        raise click.Abort()
```

### Alternative: Result Type Pattern

For Railway-Oriented Programming fans:

```python
# src/gtasks_manager/common/result.py
from typing import Generic, TypeVar, Callable
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

@dataclass
class Err(Generic[E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

Result = Ok[T] | Err[E]

# Usage in service layer
def get_task(task_id: str, uow: UnitOfWork) -> Result[Task, str]:
    """Get task, returning Result type"""
    try:
        with uow:
            task = uow.tasks.get(task_id)

            if not task:
                return Err(f"Task not found: {task_id}")

            return Ok(task)

    except Exception as e:
        return Err(f"Failed to get task: {e}")

# Usage in CLI
@click.command()
@click.argument('task_id')
def get_task_command(task_id: str):
    result = get_task(task_id, uow=real_uow)

    if result.is_ok():
        click.echo(result.value.title)
    else:
        click.echo(f"Error: {result.error}", err=True)
```

**Recommendation**: Use **exception hierarchy** for most cases. Use **Result types** if your team prefers functional programming style.

---

## 7. Dependency Management

### Pattern: Bootstrap Module (Composition Root)

```python
# src/gtasks_manager/bootstrap.py
"""
Dependency injection bootstrap.
This is the ONLY place that knows about concrete implementations.
"""
from pathlib import Path
from .config import Config
from .service_layer.services import TaskService
from .adapters.google_tasks import GoogleTasksRepository
from .adapters.cache import SQLiteCache
from .adapters.unit_of_work import SqlAlchemyUnitOfWork

def bootstrap_production(config: Config | None = None) -> TaskService:
    """Wire up real dependencies for production"""
    if config is None:
        config = Config.from_env()

    # Infrastructure
    cache = SQLiteCache(config.cache_dir / 'tasks.db')
    repository = GoogleTasksRepository(config)
    uow = SqlAlchemyUnitOfWork(repository)

    # Service
    return TaskService(uow=uow, cache=cache)

def bootstrap_test(tmp_path: Path) -> TaskService:
    """Wire up test doubles for testing"""
    from .testing.fakes import FakeTaskRepository, FakeUnitOfWork, FakeCache

    repository = FakeTaskRepository()
    uow = FakeUnitOfWork(repository)
    cache = FakeCache()

    return TaskService(uow=uow, cache=cache)

# CLI entrypoint
# src/gtasks_manager/entrypoints/cli.py
import click
from ..bootstrap import bootstrap_production

@click.group()
@click.pass_context
def cli(ctx):
    """Google Tasks Manager CLI"""
    ctx.obj = bootstrap_production()

@cli.command()
@click.pass_obj
def list_tasks(service: TaskService):
    """List all tasks"""
    tasks = service.list_tasks()
    for task in tasks:
        click.echo(f"- {task.title}")

# TUI entrypoint
# src/gtasks_manager/entrypoints/tui.py
from textual.app import App
from ..bootstrap import bootstrap_production

class TaskTUI(App):
    def __init__(self):
        super().__init__()
        self.service = bootstrap_production()

    def on_mount(self):
        tasks = self.service.list_tasks()
        # ... render tasks
```

### Avoiding Circular Dependencies

**Rule**: Dependencies flow inward only:

```
Entrypoints → Bootstrap → Service Layer → Domain ← Adapters
                ↑                                      ↑
                └──────────────────────────────────────┘
                    Bootstrap wires them together
```

**Example of BAD (circular)**:
```python
# domain/model.py
from adapters.google_tasks import GoogleTasksAdapter  # ❌ Domain depends on adapter

# adapters/google_tasks.py
from domain.model import Task  # ❌ Adapter depends on domain
```

**Example of GOOD (no cycle)**:
```python
# domain/model.py
# No imports from adapters! ✅

# adapters/google_tasks.py
from domain.model import Task  # ✅ Adapter depends on domain (inward)

# bootstrap.py
from domain.model import Task
from adapters.google_tasks import GoogleTasksAdapter  # ✅ Bootstrap knows both
```

---

## 8. Project Structure

### Recommended Directory Layout

```
gtasks-manager/
├── src/
│   └── gtasks_manager/
│       ├── __init__.py
│       │
│       ├── domain/                    # Core business logic
│       │   ├── __init__.py
│       │   ├── model.py               # Entities, Value Objects
│       │   ├── services.py            # Domain services
│       │   └── exceptions.py          # Domain exceptions
│       │
│       ├── service_layer/             # Use cases / Application services
│       │   ├── __init__.py
│       │   ├── services.py            # Service functions/classes
│       │   ├── unit_of_work.py        # UoW abstraction
│       │   └── message_bus.py         # Event bus (optional)
│       │
│       ├── adapters/                  # Infrastructure / Secondary adapters
│       │   ├── __init__.py
│       │   ├── google_tasks.py        # Google Tasks API adapter
│       │   ├── cache.py               # Cache implementation
│       │   ├── repository.py          # Repository implementations
│       │   └── exceptions.py          # Adapter exceptions
│       │
│       ├── entrypoints/               # Primary adapters
│       │   ├── __init__.py
│       │   ├── cli.py                 # Click CLI
│       │   └── tui.py                 # Textual TUI
│       │
│       ├── common/                    # Shared utilities
│       │   ├── __init__.py
│       │   ├── result.py              # Result type (optional)
│       │   └── types.py               # Common type aliases
│       │
│       ├── config.py                  # Configuration
│       └── bootstrap.py               # Dependency injection
│
├── tests/
│   ├── unit/                          # Fast, isolated tests
│   │   ├── domain/
│   │   └── service_layer/
│   │
│   ├── integration/                   # Test with real dependencies
│   │   └── adapters/
│   │
│   ├── e2e/                           # End-to-end tests
│   │   ├── test_cli.py
│   │   └── test_tui.py
│   │
│   ├── fakes.py                       # Test doubles
│   └── conftest.py                    # Pytest fixtures
│
├── pyproject.toml
└── README.md
```

---

## 9. Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E Tests (few, slow, high confidence)
      /────\
     /      \  Integration Tests (some, medium speed)
    /────────\
   /          \ Unit Tests (many, fast, focused)
  /────────────\
```

### Unit Tests - Fast, Isolated

```python
# tests/unit/domain/test_model.py
from gtasks_manager.domain.model import Task
from datetime import datetime, timedelta

def test_task_is_overdue():
    """Test domain logic in isolation"""
    yesterday = datetime.now() - timedelta(days=1)
    task = Task(
        id='1',
        title='Test',
        due_date=yesterday
    )

    assert task.is_overdue()

def test_mark_complete():
    """Test domain behavior"""
    task = Task(id='1', title='Test')
    task.mark_complete()

    assert task.status == 'completed'
    assert task.completed_date is not None

# tests/unit/service_layer/test_services.py
from gtasks_manager.service_layer.services import list_tasks
from gtasks_manager.testing.fakes import FakeUnitOfWork, FakeTaskRepository
from gtasks_manager.domain.model import Task

def test_list_tasks_filters_completed():
    """Test service layer with fakes"""
    # Arrange
    repo = FakeTaskRepository()
    repo.add(Task(id='1', title='Active', status='needsAction'))
    repo.add(Task(id='2', title='Done', status='completed'))

    uow = FakeUnitOfWork(repo)

    # Act
    tasks = list_tasks(uow=uow, show_completed=False)

    # Assert
    assert len(tasks) == 1
    assert tasks[0].title == 'Active'
```

### Integration Tests - Real Infrastructure

```python
# tests/integration/adapters/test_google_tasks.py
import pytest
from gtasks_manager.adapters.google_tasks import GoogleTasksRepository
from gtasks_manager.domain.model import Task

@pytest.mark.integration
def test_repository_roundtrip(test_config):
    """Test with real Google API (or test instance)"""
    repo = GoogleTasksRepository(test_config)

    # Create
    task = Task(id=None, title='Integration Test Task')
    repo.add(task)

    # Read
    retrieved = repo.get(task.id)
    assert retrieved.title == 'Integration Test Task'

    # Cleanup
    repo.delete(task.id)
```

### E2E Tests - Full System

```python
# tests/e2e/test_cli.py
from click.testing import CliRunner
from gtasks_manager.entrypoints.cli import cli

def test_create_and_list_task(test_config):
    """Test full CLI workflow"""
    runner = CliRunner()

    # Create task
    result = runner.invoke(cli, ['create', 'Test Task'])
    assert result.exit_code == 0
    assert 'Created' in result.output

    # List tasks
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Test Task' in result.output
```

### Test Doubles (Fakes)

```python
# tests/fakes.py
from gtasks_manager.domain.model import Task
from gtasks_manager.service_layer.unit_of_work import UnitOfWork

class FakeTaskRepository:
    """In-memory repository for testing"""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._next_id = 1

    def add(self, task: Task) -> None:
        if task.id is None:
            task.id = str(self._next_id)
            self._next_id += 1
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def update(self, task: Task) -> None:
        self._tasks[task.id] = task

    def delete(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)

class FakeUnitOfWork:
    """Fake UoW for testing"""

    def __init__(self, repository: FakeTaskRepository | None = None):
        self.tasks = repository or FakeTaskRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
```

---

## Summary: Key Decisions

1. **Architecture**: Hexagonal/Clean with service layer
2. **Service Layer**: Functions (not classes) for stateless use cases
3. **Data Models**:
   - Dataclasses for domain
   - Pydantic for API boundaries
4. **Cache/State**:
   - Start with file-based events
   - Graduate to SQLite when needed
5. **Configuration**: Single `Config` dataclass with env overrides
6. **Errors**: Custom exception hierarchy (not Result types initially)
7. **DI**: Bootstrap module, manual injection (no framework)
8. **Structure**: Clear layer separation (domain/service/adapters/entrypoints)
9. **Testing**: Lots of fast unit tests, some integration tests, few E2E tests

## Next Steps

1. Start with domain model (pure Python, no dependencies)
2. Add service layer with Protocol-based abstractions
3. Implement one adapter (Google Tasks)
4. Add first entrypoint (CLI)
5. Add second entrypoint (TUI) - will reuse service layer
6. Add caching when performance becomes issue
7. Add events when you need cross-process communication

## References

- [Architecture Patterns with Python (cosmicpython.com)](https://www.cosmicpython.com/)
- [Composition Over Inheritance](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [attrs Documentation](https://www.attrs.org/)
