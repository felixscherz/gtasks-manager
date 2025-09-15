# Google Tasks Manager

A command-line tool for managing your Google Tasks from the terminal.

## Features

- Create new tasks with optional notes and due dates
- List all tasks (with option to show completed tasks)
- Mark tasks as completed
- Delete tasks
- View all task lists
- Built-in OAuth2 authentication with Google

## Installation

```bash
pip install -e .
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
gtasks complete <task_id>  # Mark task as completed
gtasks delete <task_id>    # Delete a task

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

# Complete a task (you'll get the task ID from gtasks list)
gtasks complete abc123def456

# Delete a task
gtasks delete abc123def456

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