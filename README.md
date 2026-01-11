# Google Tasks Manager

A command-line tool for managing your Google Tasks from the terminal with dual interfaces: CLI for quick commands and TUI for visual task management.

## Features

- Create new tasks with optional notes and due dates
- List all tasks (with option to show completed tasks)
- Mark tasks as completed
- Delete tasks
- View all task lists
- Built-in OAuth2 authentication with Google
- TUI with VIM-style keybindings (h/j/k/l navigation, Enter to toggle)

## TUI Usage

The TUI provides a visual interface with VIM-style keybindings:

### Navigation
- `j` / `k`: Move selection down/up
- `h` / `l`: Move focus left/right between panes
- `q`: Quit
- `r`: Refresh tasks

### Task Management
- `Enter`: Toggle completion of selected task

### Notes
- VIM keybindings are enabled by default
- Keybindings do not trigger when typing into text inputs
- If persistence fails when toggling, the UI will briefly show an error message and revert

## Installation

### Standard Installation

```bash
pip install -e .
```

### Development Installation with uv

For development, we recommend using `uv` for faster package management:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install in development mode with uv
uv pip install -e .

# Or using uv sync (recommended)
uv sync
```

## Quick Start

1. **Authenticate with Google:**
   ```bash
   gtasks auth
   ```
   This will open your browser to sign in with Google and grant permissions.

2. **Create your first task:**
   ```bash
   gtasks create "Buy groceries"
   ```

3. **List your tasks:**
   ```bash
   gtasks list
   ```

That's it! No additional setup required.

## Development Commands

### Running the Application

```bash
# Run CLI after standard installation
gtasks --help
gtasks auth
gtasks list
gtasks create "Task title"

# Run directly from source
uv run gtasks --help
uv run gtasks auth
uv run gtasks list

# Run TUI with VIM keybindings
gtasks tui
# or
uv run gtasks tui
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/unit/test_task_cache.py::test_function_name

# Run with coverage
uv run pytest --cov=gtasks_manager
```

### Code Quality

```bash
# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking (if mypy is configured)
uv run mypy src/gtasks_manager
```

### Dependency Management

```bash
# Update dependencies and lock file
uv lock --upgrade

# Install dependencies from lock file
uv sync
```

## Commands

### Authentication
```bash
gtasks auth                # Authenticate with Google
gtasks auth --force        # Force re-authentication
gtasks logout              # Clear stored credentials
```

### Task Management
```bash
# Create tasks
gtasks create "Task title"
gtasks create "Meeting" --notes "Discuss project timeline" --due 2024-12-25

# List tasks
gtasks list                # Show active tasks
gtasks list --completed    # Show all tasks including completed

# Manage tasks
```bash
# List tasks (shows numbered index and task ID)
gtasks list                # Show active tasks
gtasks list --completed    # Show all tasks including completed

# Complete/delete tasks using either number or ID
gtasks complete 1          # Complete task #1 from list
gtasks complete abc123def  # Complete by task ID
gtasks delete 2            # Delete task #2 from list  
gtasks delete xyz789uvw    # Delete by task ID

# View task lists
gtasks lists               # Show all your Google task lists
```

## Authentication Details

The tool uses OAuth2 to securely authenticate with Google Tasks API. On first run:

1. `gtasks auth` opens your browser
2. You sign in to Google and grant permissions
3. Credentials are stored locally for future use
4. Tokens are automatically refreshed when needed

No Google Cloud project setup required - the app uses a built-in public OAuth2 client.

## Examples

```bash
# Authenticate first
gtasks auth

# Create a simple task
gtasks create "Call dentist"

# Create a task with notes and due date
gtasks create "Prepare presentation" \
  --notes "Include Q3 sales figures and market analysis" \
  --due 2024-01-15

# List all active tasks
gtasks list

# List all tasks including completed ones
gtasks list --completed

# Complete a task (you'll get the task number from gtasks list)
gtasks complete 1

# Delete a task using task number
gtasks delete 2

# Or use the full task ID if you prefer
gtasks complete abc123def456
gtasks delete xyz789uvw012

# View all your task lists
gtasks lists

# Force re-authentication if needed
gtasks auth --force

# Logout
gtasks logout
```

## Troubleshooting

**Authentication Issues:**
- Run `gtasks auth --force` to re-authenticate
- Check your internet connection
- Ensure you're granting the required permissions

**No tasks showing:**
- Make sure you're authenticated: `gtasks auth`
- Check if you have tasks in Google Tasks web interface
- Try `gtasks lists` to see your available task lists