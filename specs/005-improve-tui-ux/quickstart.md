# Quickstart Guide

**Feature**: Improve TUI UX
**Date**: 2026-01-17

## Overview

This guide helps you get started with the TUI UX improvements feature. It covers setup, development workflow, and testing for the new functionality.

## Prerequisites

- Python 3.11+ installed
- `uv` package manager installed
- Google Tasks account
- Existing gtasks-manager repository clone

## Setup Instructions

### 1. Install Dependencies

```bash
# Ensure uv is installed
pip install uv

# Install dependencies in development mode
uv sync
```

### 2. Authentication

If you haven't authenticated the application before:

```bash
# Launch authentication flow
uv run gtasks auth

# This will open a browser window for OAuth2 authentication
```

After authentication, your credentials will be stored in `~/.config/gtasks-manager/token.json`.

### 3. Verify Installation

```bash
# Run with no arguments (new default behavior)
uv run gtasks

# Or use the existing gui command (should be identical)
uv run gtasks gui
```

Both commands should launch the TUI application.

---

## New Features Overview

### 1. Default TUI Launch

**What's New**: Running `gtasks` without any subcommand now launches the TUI by default.

**Before**:
```bash
gtasks              # Error: no such command
gtasks gui          # Only way to launch TUI
```

**After**:
```bash
gtasks              # Launches TUI ✅
gtasks gui          # Still works (backward compatible) ✅
```

**Benefits**:
- Faster access to TUI
- More intuitive for new users
- Single command to get started

---

### 2. Task Selection Preservation

**What's New**: When you toggle a task's completion state, the selection stays on that task instead of jumping to the top.

**Before**:
```text
1. ○ Task A
2. ● Task B      ← Selected
3. ○ Task C

[Toggle Task B to complete]

1. ○ Task A      ← Selection jumps here ❌
2. ✓ Task B
3. ○ Task C
```

**After**:
```text
1. ○ Task A
2. ● Task B      ← Selected
3. ○ Task C

[Toggle Task B to complete]

1. ○ Task A
2. ✓ Task B      ← Selection stays here ✅
3. ○ Task C
```

**Benefits**:
- No need to re-navigate to your position
- Faster workflow when toggling multiple tasks
- Maintains context across operations

---

### 3. List Name Display

**What's New**: The TUI header now displays the name of the current task list.

**Before**:
```text
┌──────────────────────────────┐
│ Google Tasks Manager        │
├──────────────────────────────┤
│ 1. ○ Buy groceries          │
│ 2. ○ Finish project report  │
│ 3. ○ Call dentist           │
```

**After**:
```text
┌──────────────────────────────┐
│ List: Personal Tasks         │  ← List name displayed ✅
├──────────────────────────────┤
│ 1. ○ Buy groceries          │
│ 2. ○ Finish project report  │
│ 3. ○ Call dentist           │
```

**Benefits**:
- Clear context about which list you're editing
- Prevents mistakes when working with multiple lists
- Easier to identify list at a glance

---

## Development Workflow

### Running the Application

```bash
# Launch TUI (new default behavior)
uv run gtasks

# Or use the gui command (backward compatible)
uv run gtasks gui

# Other CLI commands still work
uv run gtasks list
uv run gtasks create "New task"
uv run gtasks complete 1
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only
uv run pytest tests/integration/

# Run specific test file
uv run pytest tests/unit/test_cli.py

# Run with coverage
uv run pytest --cov=gtasks_manager

# Run specific test function
uv run pytest tests/unit/test_cli.py::test_cli_launches_tui_when_no_subcommand
```

### Linting and Formatting

```bash
# Check code with ruff
uv run ruff check .

# Format code with ruff
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking

```bash
# Run mypy for type checking
uv run mypy src/
```

---

## Testing the New Features

### Test 1: Default TUI Launch

```bash
# Should launch TUI
uv run gtasks

# Verify:
# - TUI opens without errors
# - Tasks are displayed
# - List name is shown in header
```

### Test 2: Backward Compatibility

```bash
# Should launch TUI exactly like default command
uv run gtasks gui

# Verify:
# - TUI opens
# - Behavior is identical to `gtasks`
# - No error messages
```

### Test 3: Selection Preservation

```bash
uv run gtasks

# In TUI:
# 1. Navigate to a task in the middle of the list (e.g., task 5 of 10)
# 2. Toggle its completion state (e.g., press 't' or space)
# 3. Verify selection stays on the same task
# 4. Toggle back
# 5. Verify selection still stays
```

### Test 4: List Name Display

```bash
uv run gtasks

# Verify:
# - Header shows "List: [Your List Name]"
# - If you have multiple lists, name should match the current list
# - Name is readable (not truncated unless very long)
```

### Test 5: Invalid Arguments

```bash
# Should show help/error, not TUI
uv run gtasks --invalid-flag

# Verify:
# - TUI does NOT launch
# - Error message is shown
# - Help text is displayed
```

---

## Key Files to Explore

### Source Code

- **`src/gtasks_manager/cli.py`** - CLI command definitions
  - Modified to detect empty invocation and launch TUI
  - `@main.group(invoke_without_command=True)` decorator
  - `gui` command for backward compatibility

- **`src/gtasks_manager/tui/app.py`** - Main TUI application (NEW)
  - TUI initialization and launch logic
  - Task list display and interaction handling

- **`src/gtasks_manager/tui/widgets.py`** - Custom TUI widgets (NEW)
  - Task list widget with selection tracking
  - Header widget for list name display
  - Selection preservation logic

- **`src/gtasks_manager/tui/state.py`** - TUI state management (NEW)
  - Selection state tracking
  - Task list metadata caching
  - Loading and error states

### Tests

- **`tests/unit/test_cli.py`** - CLI command tests (MODIFIED)
  - Tests for default TUI launch
  - Tests for backward compatibility
  - Tests for invalid argument handling

- **`tests/unit/test_tui.py`** - TUI component tests (NEW)
  - Tests for selection preservation
  - Tests for list name display
  - Tests for state management

- **`tests/unit/test_state.py`** - State management tests (NEW)
  - Tests for selection state transitions
  - Tests for list metadata caching

- **`tests/integration/test_tui_flow.py`** - TUI integration tests (NEW)
  - End-to-end tests for TUI workflows
  - Tests for selection preservation across state changes
  - Tests for error handling

### Documentation

- **`specs/005-improve-tui-ux/spec.md`** - Feature specification
- **`specs/005-improve-tui-ux/plan.md`** - Implementation plan
- **`specs/005-improve-tui-ux/research.md`** - Research and design decisions
- **`specs/005-improve-tui-ux/data-model.md`** - Data structures
- **`specs/005-improve-tui-ux/contracts/`** - Interface contracts

---

## Common Issues and Solutions

### Issue: TUI doesn't launch when running `gtasks`

**Symptom**: Error message instead of TUI opening

**Possible Causes**:
1. Not authenticated
2. Python version too old
3. Dependencies not installed

**Solutions**:
```bash
# Check authentication
uv run gtasks auth

# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
uv sync
```

---

### Issue: Selection jumps to top after toggling task

**Symptom**: After toggling task completion, selection jumps to first task

**Possible Causes**:
1. Old version of code (not updated)
2. Selection state not preserved
3. Bug in selection restoration logic

**Solutions**:
```bash
# Pull latest changes
git pull

# Reinstall
uv sync

# Run tests to verify
uv run pytest tests/unit/test_tui.py::test_restore_selection
```

---

### Issue: List name not displayed in header

**Symptom**: Header is blank or shows "Default List"

**Possible Causes**:
1. API error fetching list metadata
2. No list name available from Google
3. Cached metadata expired

**Solutions**:
```bash
# Check API connectivity
uv run gtasks list

# Clear cache (if implemented)
rm ~/.config/gtasks-manager/*.cache

# Relaunch TUI
uv run gtasks
```

---

## Contributing

When contributing to this feature, follow the project's TDD workflow:

1. **Write failing test first**
   ```bash
   # Create test for new functionality
   # Verify it fails
   uv run pytest tests/unit/test_new_feature.py
   ```

2. **Implement the feature**
   - Make test pass
   - Follow code style guidelines (ruff)
   - Add type hints

3. **Run all tests**
   ```bash
   uv run pytest
   ```

4. **Lint and format**
   ```bash
   uv run ruff check .
   uv run ruff format .
   uv run mypy src/
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "Add [feature description] - [why]"
   ```

---

## Next Steps

After reviewing this quickstart guide:

1. Read the full [specification](./spec.md) for detailed requirements
2. Review the [implementation plan](./plan.md) for architecture decisions
3. Check the [data model](./data-model.md) for data structures
4. Review the [contracts](./contracts/) for interface definitions
5. Start implementing following the [task breakdown](./tasks.md) (Phase 2)

---

## Additional Resources

- [AGENTS.md](../../AGENTS.md) - Project coding guidelines
- [constitution.md](../../.specify/memory/constitution.md) - Development principles
- [Textual Documentation](https://textual.textual.io/) - TUI framework docs
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework docs
- [Google Tasks API](https://developers.google.com/tasks/reference/rest) - API reference
