# Quickstart Guide

**Feature**: Google Tasks CLI and TUI Manager  
**Version**: 0.1.0  
**Date**: 2026-01-07

## Overview

Google Tasks CLI and TUI Manager provides two ways to manage your Google Tasks from the terminal:

1. **CLI Commands**: Quick task operations (`gtasks create "Buy milk"`)
2. **TUI Interface**: Visual task dashboard in your terminal (`gtasks tui`)

---

## Prerequisites

- **Python**: 3.11 or higher
- **Operating System**: Linux, macOS, or Windows
- **Terminal**: Modern terminal emulator with UTF-8 support
- **Google Account**: With Google Tasks enabled
- **Internet**: Active connection for syncing with Google Tasks

---

## Installation

### Option 1: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/gtasks-manager.git
cd gtasks-manager

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .

# Verify installation
gtasks --version
```

### Option 2: Install from PyPI (When Published)

```bash
# Install package
pip install gtasks-manager

# Verify installation
gtasks --version
```

---

## First-Time Setup

### 1. Authenticate with Google

Before using any commands, authenticate with your Google account:

```bash
gtasks auth
```

This will:
1. Open your default browser
2. Ask you to log in to your Google account
3. Request permission to access Google Tasks
4. Save authentication token to `~/.config/gtasks-manager/token.json`

**Note**: Your credentials are stored locally and never shared.

### 2. Verify Authentication

List your task lists to verify authentication works:

```bash
gtasks lists
```

You should see output like:
```
• My Tasks (ID: MDcxNzMyMzk1MzUzNjM0Nzg0NDY)
• Work Tasks (ID: MDcxNzMyMzk1MzUzNjM0Nzg0NDY)
```

---

## CLI Quick Start

### Create a Task

```bash
# Simple task
gtasks create "Buy groceries"

# Task with notes
gtasks create "Buy groceries" --notes "Milk, bread, eggs"

# Task with due date
gtasks create "Submit report" --due 2024-01-15

# Task with both notes and due date
gtasks create "Team meeting" --notes "Discuss Q1 goals" --due 2024-01-10
```

### List Tasks

```bash
# List active tasks
gtasks list

# List completed tasks
gtasks list --completed
```

Output:
```
1. ○ Buy groceries (ID: MDcxNzMyMz...) (due: 2024-01-08)
   Notes: Milk, bread, eggs
2. ○ Submit report (ID: MDcxNzMyMz...) (due: 2024-01-15)
3. ✓ Team meeting (ID: MDcxNzMyMz...) (completed)
```

### Complete a Task

```bash
# Using task number from list
gtasks complete 1

# Using task ID
gtasks complete MDcxNzMyMzk1MzUzNjM0Nzg0NDY
```

### Delete a Task

```bash
# Using task number
gtasks delete 2

# Using task ID
gtasks delete MDcxNzMyMzk1MzUzNjM0Nzg0NDY
```

### Update a Task

```bash
# Update title
gtasks update 1 --title "Buy groceries and supplies"

# Update notes
gtasks update 1 --notes "Milk, bread, eggs, butter"

# Update due date
gtasks update 1 --due 2024-01-09

# Update multiple fields
gtasks update 1 --title "Shopping" --notes "Weekly shopping" --due 2024-01-09
```

### Manage Task Lists

```bash
# List all task lists
gtasks lists

# Create a new task list
gtasks create-list "Work Tasks"

# Delete a task list
gtasks delete-list "list-id"
```

---

## TUI Quick Start

### Launch the TUI

```bash
gtasks tui
```

This opens a full-screen terminal interface showing your tasks.

### Navigation

**Keyboard Shortcuts**:

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Enter` | Select/view task |
| `Space` | Toggle task completion |
| `a` | Add new task |
| `e` | Edit selected task |
| `d` | Delete selected task |
| `r` | Refresh from Google Tasks |
| `?` | Show help |
| `q` / `Esc` | Quit |

### Basic Workflow

1. **Launch TUI**: `gtasks tui`
2. **Navigate**: Use `j`/`k` or arrow keys
3. **Complete a task**: Select it and press `Space`
4. **Add a task**: Press `a`, enter details, press `Enter`
5. **Refresh**: Press `r` to sync with Google Tasks
6. **Quit**: Press `q`

---

## Configuration

### Configuration Directory

All configuration files are stored in:
- **Linux/macOS**: `~/.config/gtasks-manager/`
- **Windows**: `%APPDATA%\gtasks-manager\`

### Files

| File | Purpose |
|------|---------|
| `token.json` | OAuth2 authentication token |
| `task_cache.json` | Local cache of task IDs for CLI |

### Environment Variables

Override default settings with environment variables:

```bash
# Custom config directory
export GTASKS_CONFIG_DIR="$HOME/.gtasks"

# Default task list ID
export GTASKS_DEFAULT_LIST="your-list-id"

# Enable debug logging
export GTASKS_DEBUG=1
```

---

## Common Tasks

### Daily Workflow

```bash
# Morning: Check tasks
gtasks list

# Add new tasks as they come up
gtasks create "Call dentist"
gtasks create "Review PR #123" --due 2024-01-08

# Complete tasks throughout the day
gtasks complete 1
gtasks complete 3

# Evening: Review completed tasks
gtasks list --completed
```

### Using with Other Tools

```bash
# Export tasks to JSON
gtasks list --format json > tasks.json

# Add task from another script
echo "Review code" | xargs gtasks create

# Count pending tasks
gtasks list | grep "○" | wc -l

# Bulk complete tasks (use with caution!)
for i in {1..5}; do gtasks complete $i; done
```

---

## Troubleshooting

### Authentication Issues

**Problem**: "Authentication failed" error

**Solutions**:
```bash
# Force re-authentication
gtasks auth --force

# Clear credentials and re-authenticate
gtasks logout
gtasks auth
```

### Network Issues

**Problem**: "No network connection" error

**Solutions**:
- Check your internet connection
- Try refreshing manually: `gtasks list`
- Check Google API status: https://status.cloud.google.com/

### Task Not Found

**Problem**: "Task not found" when using task number

**Solution**:
```bash
# Refresh the cache
gtasks list

# Then try the command again
gtasks complete 1
```

### TUI Display Issues

**Problem**: TUI looks corrupted or doesn't render correctly

**Solutions**:
- Ensure terminal supports UTF-8: `export LANG=en_US.UTF-8`
- Resize terminal to at least 80x24 characters
- Try a different terminal emulator
- Update Textual: `pip install --upgrade textual`

### Permission Denied

**Problem**: Can't access config directory

**Solution**:
```bash
# Check permissions
ls -la ~/.config/gtasks-manager/

# Fix permissions
chmod 700 ~/.config/gtasks-manager/
chmod 600 ~/.config/gtasks-manager/token.json
```

---

## Getting Help

### Command-Line Help

```bash
# General help
gtasks --help

# Command-specific help
gtasks create --help
gtasks list --help
```

### TUI Help

Press `?` while in the TUI to see all keyboard shortcuts.

### Debugging

Enable debug mode for detailed logging:

```bash
# CLI debugging
gtasks --debug list

# Or via environment variable
export GTASKS_DEBUG=1
gtasks list
```

---

## Advanced Usage

### Custom Task List

```bash
# Specify task list for operations
gtasks create "Work task" --list "work-list-id"
gtasks list --list "work-list-id"
```

### Filtering Tasks

```bash
# Show only overdue tasks
gtasks list --overdue

# Show tasks due this week
gtasks list --due-week

# Show tasks with specific text
gtasks list | grep "meeting"
```

### Automation

Create bash aliases for common operations:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias t='gtasks list'
alias ta='gtasks create'
alias td='gtasks complete'
alias tt='gtasks tui'
```

### Scheduled Syncing

Set up automatic task refresh:

```bash
# Add to crontab (refresh every hour)
0 * * * * /path/to/gtasks list > /dev/null 2>&1
```

---

## Examples

### Project Management

```bash
# Create project tasks
gtasks create "Design mockups" --due 2024-01-10
gtasks create "Implement feature" --due 2024-01-15
gtasks create "Write tests" --due 2024-01-18
gtasks create "Code review" --due 2024-01-20

# Track progress
gtasks list
gtasks complete 1  # Done with mockups
gtasks complete 2  # Done with implementation
```

### Daily Standup

```bash
# Yesterday's completed tasks
gtasks list --completed --since yesterday

# Today's pending tasks
gtasks list
```

### Shopping List

```bash
# Create shopping tasks
gtasks create "Milk" --list "shopping-list-id"
gtasks create "Bread" --list "shopping-list-id"
gtasks create "Eggs" --list "shopping-list-id"

# At the store: use TUI for easy checking
gtasks tui
# Press Space to check off items as you go
```

---

## Performance Tips

1. **Use task numbers**: Faster than typing full task IDs
2. **Cache refresh**: Run `gtasks list` periodically to update cache
3. **TUI for browsing**: Use TUI when reviewing many tasks
4. **CLI for quick operations**: Use CLI for one-off task creation
5. **Offline work**: TUI caches data, works briefly offline

---

## Security Notes

- **Token storage**: OAuth tokens stored locally in `~/.config/gtasks-manager/token.json`
- **File permissions**: Token file has `600` permissions (owner read/write only)
- **No password storage**: Only OAuth tokens, no passwords stored
- **Revoke access**: Visit https://myaccount.google.com/permissions to revoke app access

---

## Next Steps

1. ✅ Complete first-time setup (authentication)
2. ✅ Try basic CLI commands (create, list, complete)
3. ✅ Launch TUI and explore interface
4. ✅ Set up bash aliases for common commands
5. ✅ Integrate with your workflow (scripts, cron jobs, etc.)

---

## Additional Resources

- **API Documentation**: See `contracts/google-tasks-api.md`
- **Data Models**: See `data-model.md`
- **Development**: See `ARCHITECTURE_GUIDE.md`
- **Testing**: See `research.md` for testing strategies

---

**Quick Reference Card**

```
CLI Commands:
  gtasks auth              - Authenticate with Google
  gtasks create "title"    - Create new task
  gtasks list              - List tasks
  gtasks complete <ref>    - Complete task
  gtasks delete <ref>      - Delete task
  gtasks update <ref>      - Update task
  gtasks tui               - Launch TUI

TUI Keys:
  j/k or ↑/↓  - Navigate
  Space       - Complete
  a           - Add task
  d           - Delete task
  r           - Refresh
  q           - Quit
```

---

**Status**: Ready for use  
**Version**: 0.1.0  
**Last Updated**: 2026-01-07
