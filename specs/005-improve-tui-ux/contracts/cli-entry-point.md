# CLI Entry Point Contract

**Version**: 1.0
**Feature**: Improve TUI UX
**Date**: 2026-01-17

## Purpose

Defines the interface contract for the CLI entry point, including command detection and default TUI launch behavior.

## Interface: CLIMain

### Responsibilities

- Detect when CLI is invoked without subcommand
- Launch TUI as default behavior
- Maintain backward compatibility with existing commands
- Handle authentication requirements

### Command Structure

```
gtasks [OPTIONS] COMMAND [ARGS]...
```

### Commands

#### Default Behavior (No Command)

**Invocation**: `gtasks`

**Behavior**:
- Detects `ctx.invoked_subcommand is None`
- Launches TUI application via `launch_tui()`
- Triggers authentication flow if no credentials found

**Exit Codes**:
- 0: TUI closed normally
- 1: Authentication failed
- 2: API error (non-fatal, user can continue)

**Examples**:
```bash
gtasks                          # Launches TUI
gtasks                          # Prompts for auth if not authenticated
gtasks                          # Shows error if API unavailable
```

---

#### `gui` Command (Existing)

**Invocation**: `gtasks gui`

**Behavior**:
- Launches TUI application via `launch_tui()`
- Identical behavior to default command
- Maintains backward compatibility

**Exit Codes**:
- 0: TUI closed normally
- 1: Authentication failed
- 2: API error (non-fatal, user can continue)

**Examples**:
```bash
gtasks gui                      # Launches TUI (same as gtasks)
gtasks gui                      # Existing users' muscle memory works
```

---

#### Other Commands (Unchanged)

The following commands must continue to work exactly as before:
- `gtasks auth` - Authentication flow
- `gtasks list` - List tasks in CLI
- `gtasks create` - Create new task
- `gtasks complete` - Mark task complete
- `gtasks uncomplete` - Mark task incomplete
- `gtasks delete` - Delete task

**Behavior**: No changes to existing command implementations

---

## Methods

#### `launch_tui() -> None`

**Purpose**: Launch the TUI application

**Parameters**: None

**Returns**: None

**Behavior**:
- Imports TUI application module
- Initializes TUI with default task list
- Blocks until TUI is closed
- Handles authentication if needed

**Dependencies**:
- `gtasks_manager.tui.app.launch_tui()`
- `gtasks_manager.auth.get_credentials()`

**Errors**:
- Authentication required → Launch `gtasks auth` flow
- TUI initialization error → Display error and exit

---

#### `is_authenticated() -> bool`

**Purpose**: Check if user has valid credentials

**Parameters**: None

**Returns**: bool - True if authenticated, False otherwise

**Behavior**:
- Checks for existing token file
- Validates token expiration
- Returns True if token exists and is valid

**Dependencies**:
- `gtasks_manager.auth.get_credentials()`

---

## Click Configuration

### Main Group Definition

```python
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Google Tasks Manager CLI

    Run without arguments to launch the TUI, or use a subcommand.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand provided, launch TUI
        launch_tui()
```

### Subcommand Registration

```python
# Existing commands (unchanged)
main.add_command(auth)
main.add_command(list_tasks)
main.add_command(create_task)
main.add_command(complete_task)
main.add_command(uncomplete_task)
main.add_command(delete_task)

# TUI command (maintains backward compatibility)
@main.command()
def gui():
    """Launch the Textual User Interface"""
    launch_tui()
```

---

## Authentication Flow

### Behavior When Not Authenticated

**Scenario**: User runs `gtasks` without credentials

**Flow**:
1. `is_authenticated()` returns False
2. TUI initialization detects missing credentials
3. Redirect to authentication flow
4. User completes authentication (OAuth2)
5. TUI launches with authenticated user's data

**User Experience**:
- Clear message: "Authentication required. Launching authentication flow..."
- OAuth2 browser window opens
- After authentication, TUI launches automatically

---

## Backward Compatibility Contract

### Guarantee

All existing commands and their behaviors must remain unchanged:

| Command | Behavior | Exit Codes | Notes |
|---------|----------|------------|-------|
| `gtasks auth` | OAuth2 authentication | 0 (success), 1 (fail) | No changes |
| `gtasks list` | List tasks in terminal | 0 (success), 1 (fail) | No changes |
| `gtasks create` | Create new task | 0 (success), 1 (fail) | No changes |
| `gtasks complete` | Mark task complete | 0 (success), 1 (fail) | No changes |
| `gtasks uncomplete` | Mark task incomplete | 0 (success), 1 (fail) | No changes |
| `gtasks delete` | Delete task | 0 (success), 1 (fail) | No changes |
| `gtasks gui` | Launch TUI | 0 (success), 1 (fail) | No changes |

### Validation Tests

For each command, verify:
- Command invocation works exactly as before
- Output format is unchanged
- Exit codes are unchanged
- Help text is available (`gtasks <command> --help`)

---

## Error Handling Contract

### CLI-Level Errors

**Invalid Arguments**:
```bash
gtasks --invalid-flag
```
**Behavior**: Display help/error message, exit with code 2
**Message**: "Error: no such option: --invalid-flag"

**Missing Required Arguments**:
```bash
gtasks create
```
**Behavior**: Display help with required arguments, exit with code 2
**Message**: "Error: Missing argument 'TITLE'"

**Authentication Required**:
```bash
gtasks  # No credentials
```
**Behavior**: Launch authentication flow, then TUI
**Message**: "Authentication required. Launching authentication flow..."

### TUI-Level Errors

Handled by TUI application contract (see `tui-application.md`)

---

## Performance Contract

### Launch Time Targets

- `gtasks` (authenticated): < 500ms to TUI display
- `gtasks gui` (authenticated): < 500ms to TUI display
- `gtasks` (not authenticated): < 200ms to auth flow start

### CLI Command Response Time

All existing commands must maintain current performance:
- `gtasks list`: < 2 seconds for typical task lists
- `gtasks create`: < 1 second
- `gtasks complete/uncomplete`: < 1 second
- `gtasks delete`: < 1 second

---

## Testing Contract

### Unit Tests Required

- `test_cli_launches_tui_when_no_subcommand`
- `test_gui_command_launches_tui`
- `test_existing_commands_unchanged` (for each existing command)
- `test_is_authenticated_returns_true_with_valid_token`
- `test_is_authenticated_returns_false_without_token`

### Integration Tests Required

- `test_gtasks_without_args_launches_tui`
- `test_gtasks_gui_launches_tui_identical_to_default`
- `test_gtasks_without_auth_redirects_to_auth_then_tui`
- `test_invalid_args_show_help_not_tui`

### Backward Compatibility Tests Required

For each existing command:
- `test_<command>_behavior_unchanged`
- `test_<command>_exit_codes_unchanged`
- `test_<command>_output_format_unchanged`

---

## Version History

- 1.0 (2026-01-17): Initial contract for CLI entry point improvements
