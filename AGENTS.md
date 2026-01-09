# Agent Guidelines for gtasks-manager

This document provides coding guidelines and context for AI coding agents working on the Google Tasks Manager CLI tool.

## Project Overview

A Python application for managing Google Tasks from the terminal with dual interfaces: CLI for quick commands and TUI for visual task management. Built with Click (CLI), Textual (TUI), and Google Tasks API v1 with OAuth2 authentication.

**Tech Stack:**
- Python 3.11+
- Click 8.0+ (CLI framework)
- Textual 0.47+ (TUI framework)
- Google API Python Client 2.0+
- Google Auth libraries (OAuth2)
- Pydantic 2.0+ (Data validation)
- pytest + pytest-asyncio (Testing)
- Hatchling (build backend)

## Build, Test, and Run Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install from scratch (in new venv)
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -e .
```

### Running the Application
```bash
# Run CLI after installation
gtasks --help
gtasks auth
gtasks list
gtasks create "Task title"

# Run directly from source (if installed in editable mode)
python -m gtasks_manager.cli
```

### Testing
**Note:** This project currently has no test suite. When adding tests:
- Use `pytest` as the test framework
- Place tests in `tests/` directory
- Run single test: `pytest tests/test_file.py::test_function_name`
- Run all tests: `pytest`
- Run with coverage: `pytest --cov=gtasks_manager`

### Linting/Formatting
**Note:** No linters/formatters currently configured. When adding:
- Prefer `ruff` for modern Python linting and formatting
- Alternative: `black` for formatting, `flake8` for linting
- Type checking: Use `mypy` with strict mode

### Build Commands
```bash
# Build package (creates wheel and sdist)
python -m build

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
```

## Project Structure

```
src/gtasks_manager/
├── __init__.py          # Package metadata (__version__)
├── cli.py               # Click CLI commands and entry point
├── auth.py              # OAuth2 authentication logic
├── tasks.py             # TasksManager class (API interactions)
├── config.py            # Configuration constants and paths
└── task_cache.py        # TaskCache class (local task indexing)
```

## Code Style Guidelines

### Import Organization
Follow this order with blank lines between groups:
1. Standard library imports (alphabetical)
2. Third-party imports (alphabetical)
3. Local application imports (relative imports)

```python
# Example from cli.py
import click
from datetime import datetime
from typing import Optional

from .tasks import TasksManager
from .auth import clear_credentials
from .task_cache import TaskCache
```

### Type Hints
- **Always use type hints** for function parameters and return types
- Use `typing` module for complex types: `Optional`, `List`, `Dict`, `Any`
- Format: `def function(param: str, optional: Optional[int] = None) -> bool:`
- Dict type hints: `Dict[str, Any]` for API responses from Google

```python
# Good examples from codebase
def create_task(self, title: str, notes: Optional[str] = None, 
               due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    
def resolve_task_reference(reference: str, show_completed: bool = False) -> Optional[str]:
```

### Naming Conventions
- **Functions/methods:** `snake_case` (e.g., `get_task_lists`, `format_task`)
- **Classes:** `PascalCase` (e.g., `TasksManager`, `TaskCache`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `SCOPES`, `TOKEN_FILE`, `CONFIG_DIR`)
- **Private methods:** Prefix with `_` (not heavily used in this codebase)
- **Module-level variables:** `UPPER_SNAKE_CASE` for config constants

### Formatting
- **Line length:** Keep under 100 characters (prefer 88 for Black compatibility)
- **Indentation:** 4 spaces (never tabs)
- **Blank lines:** 2 between top-level definitions, 1 between methods
- **Strings:** Use single quotes `'` for strings (observed pattern in codebase)
- **Trailing commas:** Not consistently used; add in multi-line arguments

### Error Handling

**Pattern 1: Catch and print (Google API calls)**
```python
try:
    result = self.service.tasks().insert(
        tasklist=task_list_id, body=task
    ).execute()
    return result
except HttpError as error:
    print(f'An error occurred: {error}')
    return None
```

**Pattern 2: Click error messages (CLI level)**
```python
try:
    manager = TasksManager()
    # ... operation
except Exception as e:
    click.echo(f"Error: {e}")
```

**Key principles:**
- Catch `HttpError` specifically for Google API calls
- Return `None`, `False`, or empty list on errors (not exceptions)
- Use `click.echo()` for user-facing messages in CLI commands
- Use `print()` for internal error messages in service classes
- Silent failures for non-critical operations (e.g., cache writes with bare `except`)

### Click CLI Patterns

**Command structure:**
```python
@main.command()
@click.argument('required_arg')
@click.option('--flag', '-f', is_flag=True, help='Description')
@click.option('--value', '-v', help='Description')
def command_name(required_arg: str, flag: bool, value: Optional[str]):
    """Command description for --help."""
    try:
        # Implementation
        click.echo("Success message")
    except Exception as e:
        click.echo(f"Error: {e}")
```

**Conventions:**
- Use `click.echo()` not `print()` in CLI commands
- Provide short flag variants (e.g., `-n`, `-d`, `-c`)
- Include helpful docstrings (shown in `--help`)
- Type hint all parameters

### Class Design
- **Service classes** (`TasksManager`): Initialize with credentials in `__init__`
- **Utility classes** (`TaskCache`): Lightweight, instantiate as needed
- **Methods**: Return meaningful values (`bool` for success/fail, `Optional` for nullable)
- **No class variables**: Use instance variables or module constants

### Configuration and Paths
- Use `pathlib.Path` for all file paths (not string concatenation)
- Store config in `~/.config/gtasks-manager/`
- Config constants in `config.py`: `TOKEN_FILE`, `CONFIG_DIR`, `SCOPES`
- Always call `ensure_config_dir()` before file operations

### API Interaction Patterns
- Build Google service once in `__init__`: `build('tasks', 'v1', credentials=self.creds)`
- Default to first task list if none specified
- Google API datetime format: ISO 8601 with 'Z' suffix (e.g., `"2024-12-25T00:00:00Z"`)
- Check for existence of items with `.get('items', [])` pattern

### Comments and Documentation
- **Docstrings:** Use for CLI commands (shown in help), optional for internal functions
- **Inline comments:** Minimal; code should be self-documenting
- **Special cases:** Comment non-obvious logic (e.g., OAuth secret comment in config.py:18-19)

## Important Patterns and Conventions

### Task ID Resolution
The app supports referencing tasks by:
1. Numeric index from `gtasks list` (e.g., "1", "2")
2. Full task ID from Google API (e.g., "abc123def")

Use `resolve_task_reference()` helper for this translation.

### Caching Strategy
- `TaskCache` stores task index→ID mapping in JSON
- Separate caches for active vs completed tasks
- Silently fail cache operations (don't break app if cache fails)
- Update cache after every `gtasks list` command

### Date Formatting
- **Input:** `YYYY-MM-DD` format for CLI arguments
- **Google API:** ISO 8601 with 'Z' (UTC): `datetime.isoformat() + 'Z'`
- **Display:** `YYYY-MM-DD` format: `strftime('%Y-%m-%d')`

### User Feedback
- ✓ (checkmark) for completed tasks and success
- ○ (circle) for pending tasks
- ✗ (x mark) for failures
- Show task IDs in output for reference
- Provide actionable error messages

## Security Considerations

1. **OAuth Credentials:**
   - Client secret in `CLIENT_CONFIG` is not treated as actual secret (public OAuth client)
   - User tokens stored in `~/.config/gtasks-manager/token.json`
   - Never commit `token.json` or user credentials

2. **Gitignore:**
   - `credentials/` directory
   - `token.json`
   - `credentials.json`
   - Standard Python artifacts (`__pycache__/`, `*.egg-info/`, `.venv/`)

## Common Tasks for Agents

### Adding a New CLI Command
1. Add `@main.command()` decorated function in `cli.py`
2. Add arguments/options with type hints
3. Include docstring for help text
4. Wrap in try/except with `click.echo()` for errors
5. Create corresponding method in `TasksManager` if needed

### Adding a New TasksManager Method
1. Add to `tasks.py` class
2. Use type hints: `-> Optional[Dict[str, Any]]` or `-> bool`
3. Get default task list if not provided: `self.get_default_task_list_id()`
4. Wrap Google API call in `try/except HttpError`
5. Return meaningful value (not exception)

### Working with Google Tasks API
- API Reference: https://developers.google.com/tasks/reference/rest
- Task resource fields: `id`, `title`, `notes`, `status`, `due`, `completed`
- Status values: `"needsAction"`, `"completed"`
- Always use `tasklist` parameter in API calls

### Building Textual TUI Components
1. Use `reactive()` attributes for auto-updating UI state
2. Implement `compose()` method for widget layout
3. Handle events with `on_<event>` methods (e.g., `on_key`, `on_button_pressed`)
4. Use `@work` decorator for async background operations (API calls)
5. Create custom `Message` classes for widget communication
6. Test with `app.run_test()` and Pilot API for simulating user input

**Example Textual Widget**:
```python
from textual.reactive import reactive
from textual.widgets import Static
from textual import work

class TaskListWidget(Static):
    tasks = reactive(list)  # Auto-updates UI
    
    def compose(self):
        yield TaskList(self.tasks)
    
    def watch_tasks(self, old, new):
        """Called when tasks change."""
        self.refresh()
    
    @work
    async def load_tasks(self):
        """Background API call."""
        self.tasks = await api.fetch_tasks()
```

**Key Patterns**:
- Reactive attributes: `tasks = reactive(list)` + `watch_tasks()` method
- Async workers: `@work` decorator for non-blocking operations
- Message passing: `self.post_message(TaskSelected(task_id))`
- Testing: `async with app.run_test() as pilot: await pilot.press("j")`

**Reference**: See `docs/textual-framework-guide.md` for comprehensive patterns

## Dependencies

Core dependencies (see `pyproject.toml`):
- `google-api-python-client>=2.0.0` - Google API client
- `google-auth-oauthlib>=1.0.0` - OAuth2 flow
- `google-auth-httplib2>=0.2.0` - HTTP transport
- `click>=8.0.0` - CLI framework

Python version: `>=3.11`

## Future Improvements to Consider

- Add test suite (pytest)
- Add linting/formatting (ruff or black+flake8)
- Add type checking (mypy)
- Support for multiple task lists (currently uses default/first)
- Task editing functionality
- Recurring tasks support
- Better error messages with troubleshooting

## Active Technologies
- Local filesystem (OAuth tokens in `~/.config/gtasks-manager/token.json`) (001-google-tasks-cli-tui)
- Python 3.11 (project-wide requirement from constitution) + `textual` (TUI), `click` (CLI), `google-api-python-client` (adapters), `pydantic` (dtos/validation), `pytest` + `pytest-asyncio` (testing) (002-add-vim-keybindings)
- N/A (feature operates on in-memory UI state and existing task storage/backends) (002-add-vim-keybindings)

## Recent Changes
- 001-google-tasks-cli-tui: Added Python 3.11+
