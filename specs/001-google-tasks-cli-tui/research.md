# Research & Technical Decisions

**Feature**: Google Tasks CLI and TUI Manager  
**Branch**: `001-google-tasks-cli-tui`  
**Date**: 2026-01-07

## Purpose

This document consolidates research findings from Phase 0 and documents key technical decisions for implementing the Google Tasks CLI and TUI application. All decisions are based on official documentation, best practices, and suitability for this project's requirements.

---

## Decision 1: Textual Framework Patterns

### Context
Need to understand best practices for building production-ready Textual TUI applications, including async handling, state management, and testing strategies.

### Research Findings

**Key Insights**:
1. **Async/Await Integration**: Textual runs on asyncio event loop; handlers can be sync or async
2. **Workers API**: Use `@work` decorator for background operations (thread workers for CPU-intensive, async workers for I/O)
3. **Reactive Attributes**: Built-in `reactive()` system for automatic UI updates when state changes
4. **Testing**: First-class `run_test()` API with Pilot for simulating user interactions
5. **Error Handling**: Worker callbacks for error handling, event bubbling for error propagation

**Recommended Patterns**:

```python
# Reactive state management
class TaskListView(Static):
    tasks = reactive(list)  # Auto-updates UI when modified
    
    def watch_tasks(self, old_value, new_value):
        """Called automatically when tasks change."""
        self.refresh()

# Async event handlers
async def on_button_pressed(self, event: Button.Pressed):
    """Async handler for I/O operations."""
    self.loading = True
    tasks = await self.fetch_tasks()
    self.tasks = tasks  # Triggers watch_tasks()
    self.loading = False

# Workers for background operations
@work(thread=True)
def sync_with_api(self) -> list:
    """Background worker (runs in thread)."""
    return api.fetch_tasks()

def on_worker_state_changed(self, event):
    """Handle worker completion/errors."""
    if event.worker.name == "sync_with_api":
        if event.state == WorkerState.SUCCESS:
            self.tasks = event.worker.result
        elif event.state == WorkerState.ERROR:
            self.show_error(event.worker.error)
```

**Testing Pattern**:

```python
async def test_task_list_navigation():
    app = TasksApp()
    async with app.run_test() as pilot:
        await pilot.press("j")  # Simulate key press
        await pilot.pause()      # Wait for UI update
        assert app.selected_task_index == 1
```

### Decision

**Use Textual's reactive attributes for state management** combined with **async event handlers for API calls** and the **Workers API for background operations**.

**Rationale**:
- Reactive attributes eliminate manual UI update code
- Async handlers simplify I/O-bound operations (Google API calls)
- Workers prevent blocking the UI during sync operations
- Built-in testing support with `run_test()` enables comprehensive TUI tests

**Alternatives Considered**:
- Manual state management: Too error-prone, requires explicit refresh calls
- Sync-only handlers: Would block UI during API calls
- Threading without Workers API: More complex, less integrated with Textual

---

## Decision 2: Google Tasks API Integration

### Context
Need robust patterns for OAuth2 authentication, rate limiting, error handling, and API interaction for a CLI/TUI application.

### Research Findings

**OAuth2 Token Management**:
- Access tokens: ~1 hour lifetime
- Refresh tokens: Up to 6 months of inactivity
- Library auto-handles refresh (no manual expiry checking needed)
- Store tokens in `~/.config/gtasks-manager/token.json` (already implemented correctly)

**Rate Limits**:
- 50,000 queries/day courtesy limit
- HTTP 429 RESOURCE_EXHAUSTED for rate limit exceeded
- Retry with exponential backoff for 429, 500, 503 errors
- Don't retry 4xx errors (except 429)

**API Structure**:
```json
{
  "id": "task123",
  "title": "Buy milk",
  "status": "needsAction",  // or "completed"
  "due": "2024-01-08T00:00:00Z",
  "notes": "Optional notes",
  "updated": "2024-01-07T10:30:00.000Z"
}
```

**No Batch Operations**: Google Tasks API doesn't support batching; make individual API calls

**Required Scope**:
```python
SCOPES = ['https://www.googleapis.com/auth/tasks']  # Full access (recommended)
# Alternative: 'tasks.readonly' for read-only mode
```

### Decision

**Implement exponential backoff retry logic** for transient errors (429, 500, 503) with **centralized error handling** for user-friendly messages.

**Rationale**:
- Improves reliability against transient network/API issues
- Better user experience with clear error messages
- Follows Google API best practices
- Simple to implement (no external retry libraries needed)

**Implementation**:

```python
def execute_with_retry(request, max_retries=3):
    """Execute API request with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return request.execute()
        except HttpError as error:
            status = error.resp.status
            
            # Don't retry client errors (except rate limit)
            if 400 <= status < 500 and status != 429:
                raise
            
            if attempt == max_retries:
                raise
            
            # Exponential backoff: 1s, 2s, 4s...
            wait = (2 ** attempt) + (random.random() * 0.1)
            time.sleep(wait)
```

**Alternatives Considered**:
- No retry logic: Too fragile for production use
- Third-party retry library: Overkill for simple exponential backoff
- Batch operations: Not supported by Google Tasks API

---

## Decision 3: Testing Strategy

### Context
Need to achieve 90%+ test coverage for both CLI (Click) and TUI (Textual) interfaces with fast, reliable tests.

### Research Findings

**Click Testing**:
- Use `click.testing.CliRunner` (official testing utility)
- Captures output, exit codes, and exceptions
- Supports isolated filesystem for file operations

**Textual Testing**:
- Use `app.run_test()` for headless testing
- Pilot API simulates user interactions (key presses, clicks)
- pytest-asyncio for async test support
- Snapshot testing available via pytest-textual-snapshot

**Mocking**:
- pytest-mock recommended (thin wrapper around unittest.mock)
- Mock Google API service to avoid real API calls in unit tests
- VCR.py for integration tests (record/replay real API responses)

**Test Data**:
- factory_boy for generating realistic test data
- Faker integration for varied test scenarios

### Decision

**Use pytest with specialized tools for each layer**:

1. **Unit Tests (70%)**: pytest-mock for Google API, factory_boy for test data
2. **Integration Tests (20%)**: VCR.py for recorded API responses
3. **E2E Tests (10%)**: Full CLI/TUI workflows with mocked API

**Testing Pyramid**:
```
        E2E (10%)
    CLI + TUI full flows
        
    Integration (20%)
  VCR recorded responses
      
        Unit (70%)
   Fast, isolated, mocked
```

**Rationale**:
- Fast unit tests enable rapid development
- Integration tests verify API contract compliance
- E2E tests catch workflow issues
- Mocking prevents flaky tests from network issues
- VCR provides realistic API responses without hitting quota

**Implementation**:

```python
# Unit test with mocking
def test_create_task(mocker):
    mock_service = mocker.MagicMock()
    mocker.patch('gtasks_manager.tasks.build', return_value=mock_service)
    
    mock_service.tasks().insert().execute.return_value = {
        'id': 'task123',
        'title': 'Buy milk'
    }
    
    manager = TasksManager()
    result = manager.create_task('Buy milk')
    assert result['id'] == 'task123'

# Integration test with VCR
@pytest.mark.vcr()
def test_real_api_structure():
    manager = TasksManager()
    tasks = manager.list_tasks()  # Recorded on first run, replayed after
    assert 'id' in tasks[0]

# TUI async test
async def test_navigation():
    app = TasksApp()
    async with app.run_test() as pilot:
        await pilot.press("j")
        assert app.selected_index == 1
```

**Coverage Goals**:
- Core modules: 95%+
- Adapters: 90%+
- CLI/TUI: 85%+
- Overall: 90%+

**Alternatives Considered**:
- Manual testing only: Not scalable, error-prone
- Real API tests only: Slow, quota-limited, flaky
- responses library instead of VCR: VCR better for complex request/response patterns

---

## Decision 4: Architecture for Shared CLI/TUI Logic

### Context
Both CLI and TUI need to share business logic for task management while maintaining independence and testability.

### Research Findings

**Hexagonal Architecture (Ports & Adapters)**:
- Core domain logic has no external dependencies
- Adapters translate between external systems (Google API) and domain
- Interfaces (CLI/TUI) depend on core, not vice versa

**Service Layer Patterns**:
- Function-based services simpler than class-based for stateless operations
- Protocol-based abstractions (Python's structural typing) for flexibility
- No dependency injection framework needed (manual wiring via bootstrap module)

**Data Modeling**:
- **dataclasses**: Lightweight, stdlib, perfect for domain models
- **Pydantic**: For API boundaries (validation, serialization)
- Conversion functions between Google API format and domain models

**Cache Invalidation**:
- File-based event system (simplest, sufficient for single-user)
- SQLite for more robust shared state (if needed later)
- Message bus pattern (overkill for this project)

**Error Handling**:
- Custom exception hierarchy (domain exceptions vs adapter exceptions)
- Adapters translate external errors to domain exceptions
- Interfaces catch and display user-friendly messages

### Decision

**Use Hexagonal Architecture with**:
- **Domain models**: dataclasses (lightweight, stdlib)
- **API boundary**: Pydantic for Google API validation
- **Service layer**: Function-based services
- **State sharing**: File-based event notifications
- **Dependencies**: Manual composition root (bootstrap module)

**Rationale**:
- Clear separation of concerns (domain, adapters, interfaces)
- Core testable without Google API or UI frameworks
- Both CLI and TUI use same service functions
- Easy to add new interfaces later (web, mobile)
- No heavyweight frameworks needed

**Project Structure**:

```
src/gtasks_manager/
├── core/                   # Domain layer (no external deps)
│   ├── models.py          # dataclass models
│   ├── services.py        # Business logic functions
│   └── exceptions.py      # Domain exceptions
│
├── adapters/              # External integrations
│   ├── google_tasks.py   # Google Tasks API adapter
│   └── storage.py        # File system storage
│
├── cli/                   # Click interface
│   └── commands/         # CLI commands
│
├── tui/                   # Textual interface
│   ├── app.py           # Main TUI app
│   └── widgets/         # TUI widgets
│
└── config.py             # Configuration (reuse existing)
```

**Implementation**:

```python
# core/models.py (domain, no external deps)
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: str
    title: str
    status: str
    notes: Optional[str] = None
    due: Optional[datetime] = None
    updated: datetime = None

# adapters/google_tasks.py (translate API to domain)
from pydantic import BaseModel

class GoogleTask(BaseModel):
    """Pydantic model for Google API validation."""
    id: str
    title: str
    status: str
    notes: Optional[str] = None
    due: Optional[str] = None
    
    def to_domain(self) -> Task:
        """Convert to domain model."""
        return Task(
            id=self.id,
            title=self.title,
            status=self.status,
            notes=self.notes,
            due=datetime.fromisoformat(self.due) if self.due else None
        )

# core/services.py (business logic)
def create_task(
    title: str,
    api_adapter: TasksAPIProtocol,
    notes: Optional[str] = None,
    due: Optional[datetime] = None
) -> Task:
    """Create a new task (framework-agnostic)."""
    # Business validation
    if not title or len(title) > 1024:
        raise InvalidTaskError("Title must be 1-1024 characters")
    
    # Delegate to adapter
    task_data = api_adapter.create_task(title, notes, due)
    return task_data

# cli/commands/tasks.py (Click interface)
@click.command()
@click.argument('title')
def create(title: str):
    """Create a new task."""
    from gtasks_manager.bootstrap import get_api_adapter
    
    adapter = get_api_adapter()
    task = create_task(title, adapter)
    click.echo(f"Created: {task.title}")

# tui/app.py (Textual interface)
class TasksApp(App):
    async def on_button_pressed(self, event):
        """Handle create button."""
        from gtasks_manager.bootstrap import get_api_adapter
        
        adapter = get_api_adapter()
        task = create_task(self.input_text, adapter)
        self.tasks.append(task)
```

**Alternatives Considered**:
- Monolithic CLI/TUI: Code duplication, hard to test
- Framework-heavy DI: Overkill for this size project
- attrs instead of dataclasses: More features but unnecessary complexity
- Result types instead of exceptions: Less Pythonic, harder to read

---

## Technology Stack Summary

### Core Dependencies

```toml
[project.dependencies]
# CLI framework
click = ">=8.0.0"

# TUI framework  
textual = ">=0.47.0"

# Google API
google-api-python-client = ">=2.0.0"
google-auth-oauthlib = ">=1.0.0"
google-auth-httplib2 = ">=0.2.0"

# Data validation (API boundary)
pydantic = ">=2.0.0"
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.11.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.0",
    
    # Test data
    "factory-boy>=3.3.0",
    "faker>=19.0.0",
    
    # Integration testing
    "vcrpy>=5.1.0",
    "pytest-recording>=0.13.0",
    
    # TUI testing
    "pytest-textual-snapshot>=0.4.0",
    
    # Development
    "pytest-watch>=4.2.0",
    "pytest-sugar>=0.9.7",
]
```

---

## Implementation Priorities

### Phase 0: Foundation ✅ (This Document)
- Research complete
- Architectural decisions made
- Technology stack selected

### Phase 1: Core + Google API (Next)
- Implement domain models (dataclasses)
- Build Google Tasks adapter with retry logic
- Create service layer functions
- Unit tests for core (95%+ coverage)

### Phase 2: CLI Interface
- Implement Click commands using service layer
- Output formatters
- Error handling
- CLI integration tests

### Phase 3: TUI Interface
- Basic Textual app structure
- Task list view with reactive attributes
- Async loading with Workers API
- Keyboard navigation
- TUI tests with Pilot

### Phase 4: Testing & Documentation
- Achieve 90%+ overall coverage
- Integration tests with VCR
- E2E test scenarios
- Quickstart guide
- API documentation

---

## Risk Mitigation

### Risk 1: Textual Framework Learning Curve
**Mitigation**: 
- Comprehensive guide created (`docs/textual-framework-guide.md`)
- Start with simple widgets, iterate to complex
- Use official examples as reference

### Risk 2: Google API Rate Limits
**Mitigation**:
- Implement exponential backoff retry
- Use VCR for integration tests (no API calls)
- Cache task data locally
- User feedback on rate limit errors

### Risk 3: OAuth Token Expiration
**Mitigation**:
- Auto-refresh handled by library
- Clear error messages on revoked tokens
- Easy re-authentication flow

### Risk 4: Test Coverage Goals
**Mitigation**:
- Test-first approach (write tests before implementation)
- factory_boy reduces test data boilerplate
- Mocking prevents slow/flaky tests
- Coverage tracked in CI/CD

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research and decisions documented
2. **Phase 1**: Create `data-model.md` with detailed entity specifications
3. **Phase 1**: Create `contracts/` directory with API interaction contracts
4. **Phase 1**: Generate `quickstart.md` with setup instructions
5. **Phase 1**: Update `AGENTS.md` with Textual framework context
6. **Phase 2**: Generate `tasks.md` with implementation tasks (via `/speckit.tasks`)

---

**Research Status**: ✅ Complete  
**Decisions**: 4/4 made  
**Ready for**: Phase 1 (Design & Contracts)
