# Quickstart: VIM Keybindings for TUI Task List

**Feature**: 003-vim-keybindings
**Date**: 2025-01-11

## Overview

This quickstart guide provides step-by-step instructions for developing, testing, and running the VIM keybindings feature for the gtasks-manager TUI.

## Prerequisites

1. **Python 3.11+** installed
2. **uv** installed (dependency manager)
3. **Git** cloned repository at correct branch: `003-vim-keybindings`

### Verify Environment

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Check uv is installed
uv --version

# Verify current branch
git branch  # Should show * 003-vim-keybindings
```

## Development Workflow

### 1. Initial Setup

```bash
# Install dependencies
uv pip install -e ".[test,dev]"

# Verify installation
uv run gtasks --help
```

### 2. Running Tests

#### Run All TUI Tests

```bash
# Run all integration tests for TUI
uv run pytest tests/integration/test_tui_navigation.py -v

# Run all unit tests for keybindings
uv run pytest tests/unit/test_keybindings.py -v

# Run all TUI-related tests
uv run pytest tests/ -k "tui or keybindings" -v
```

#### Run Specific Test

```bash
# Run a single test
uv run pytest tests/integration/test_tui_navigation.py::test_j_key_moves_selection_down -v

# Run with coverage
uv run pytest tests/integration/test_tui_navigation.py -v --cov=gtasks_manager.tui
```

#### Run Tests with Verbosity

```bash
# Very verbose output
uv run pytest tests/ -k "tui" -vv

# Show print statements
uv run pytest tests/ -k "tui" -s
```

### 3. Code Quality

#### Linting with Ruff

```bash
# Check for issues
uv run ruff check src/gtasks_manager/tui/

# Fix auto-fixable issues
uv run ruff check --fix src/gtasks_manager/tui/

# Format code
uv run ruff format src/gtasks_manager/tui/
```

#### Type Checking (if mypy is configured)

```bash
# Type check TUI module
uv run mypy src/gtasks_manager/tui/
```

### 4. Running the TUI

#### Start TUI

```bash
# Start TUI with VIM bindings enabled (default)
uv run gtasks tui

# Alternative: run directly with Python
uv run python -m gtasks_manager.tui.app
```

#### VIM Keybindings

Once TUI is running:

| Key | Action | Description |
|-----|--------|-------------|
| `j` | Move down | Navigate to next task in list |
| `k` | Move up | Navigate to previous task in list |
| `enter` | Toggle task | Toggle completion of selected task (○ ↔ ✓) |
| `h` | Focus left | Move focus to sidebar pane |
| `l` | Focus right | Move focus to task list pane |
| `q` | Quit | Exit TUI |
| `r` | Refresh | Reload tasks from Google Tasks API |

#### Arrow Keys (Backward Compatible)

| Key | Action |
|-----|--------|
| `↓` (down arrow) | Move down (same as 'j') |
| `↑` (up arrow) | Move up (same as 'k') |

### 5. Testing Keybindings Manually

#### Test Navigation

```bash
# Start TUI
uv run gtasks tui

# Manual test steps:
# 1. Press 'j' - selection should move down
# 2. Press 'j' repeatedly - should navigate through list
# 3. Press 'k' - selection should move up
# 4. Press 'k' repeatedly - should navigate backward
# 5. Test at top of list: 'k' should have no effect
# 6. Test at bottom of list: 'j' should have no effect
# 7. Press 'q' to quit
```

#### Test Toggle

```bash
# Start TUI
uv run gtasks tui

# Manual test steps:
# 1. Navigate to a task with status ○ (not completed)
# 2. Press 'enter' - status should change to ✓ (completed)
# 3. Press 'enter' again - status should change back to ○
# 4. Repeat for multiple tasks
# 5. Press 'q' to quit
```

#### Test Arrow Keys

```bash
# Start TUI
uv run gtasks tui

# Manual test steps:
# 1. Press down arrow repeatedly - should navigate down
# 2. Press up arrow repeatedly - should navigate up
# 3. Alternate between arrow keys and j/k - both should work
# 4. Press 'q' to quit
```

## Development Patterns

### Test-First Development (TDD)

Following the constitution's TDD requirement:

1. **Write failing test first**:
   ```python
   @pytest.mark.asyncio
   async def test_new_feature(app):
       """Test new feature behavior."""
       async with app.run_test() as pilot:
           # Setup
           app.ui_focus = UIFocus(pane=UIFocusPane.TASK_LIST, index=0)

           # Act
           await pilot.press("new_key")

           # Assert
           assert expected_state
   ```

2. **Run test to confirm it fails**:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py::test_new_feature -v
   ```

3. **Implement feature**:
   - Add key binding to BINDINGS list
   - Implement action method
   - Update UI state as needed

4. **Run test to confirm it passes**:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py::test_new_feature -v
   ```

5. **Run all tests to ensure no regressions**:
   ```bash
   uv run pytest tests/ -k "tui" -v
   ```

### Adding New Keybindings

1. **Add to BINDINGS list** in `TasksApp`:
   ```python
   BINDINGS = [
       ("x", "custom_action", "Custom action"),
       # ... existing bindings
   ]
   ```

2. **Implement action method**:
   ```python
   def action_custom_action(self) -> None:
       """Handle custom action."""
       # Implementation
       pass
   ```

3. **Add test**:
   ```python
   @pytest.mark.asyncio
   async def test_x_key_triggers_custom_action(app):
       async with app.run_test() as pilot:
           await pilot.pause()
           await pilot.press("x")
           # Assert expected behavior
   ```

4. **Test and verify**:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py -v
   ```

## Debugging

### Debug Test Failures

```bash
# Run with verbose output
uv run pytest tests/integration/test_tui_navigation.py::test_failing_test -vv -s

# Run with debugger (if installed)
uv run pytest tests/integration/test_tui_navigation.py::test_failing_test --pdb
```

### Debug TUI Issues

```bash
# Run TUI with verbose logging
export TEXTUAL_DEBUG=1
uv run gtasks tui
```

### Check App State

```python
# In tests, inspect app state directly
async def test_inspect_state(app):
    async with app.run_test() as pilot:
        await pilot.pause()
        print(f"Tasks: {len(app.tasks)}")
        print(f"UI focus: {app.ui_focus}")
        print(f"Selected task ID: {app.selected_task_id}")
```

## Common Issues

### Test: "AttributeError: TasksApp has no attribute 'keybinding_manager'"

**Cause**: KeyBindingManager not initialized in `TasksApp.__init__`

**Fix**: Add initialization:
```python
def __init__(self, service: TaskService):
    super().__init__()
    self.service = service
    self.keybinding_manager = KeyBindingManager()  # Add this line
```

### Test: "list_view.index is None"

**Cause**: ListView not initialized or no tasks loaded

**Fix**: Use default value:
```python
current_index = list_view.index or 0
```

### TUI: Keys not responding

**Cause**: Focus may be on wrong pane (sidebar vs task list)

**Fix**: Use `h`/`l` keys to move focus to task list, or ensure focus is correct

### Test: Async test hangs

**Cause**: Missing `@pytest.mark.asyncio` decorator or not awaiting pilot methods

**Fix**: Ensure proper async test structure:
```python
@pytest.mark.asyncio
async def test_correct(app):
    async with app.run_test() as pilot:
        await pilot.pause()  # Must await
        await pilot.press("j")  # Must await
        assert True
```

## CI/CD Checklist

Before committing:

1. ✅ All tests pass:
   ```bash
   uv run pytest tests/ -k "tui or keybindings" -v
   ```

2. ✅ No linting errors:
   ```bash
   uv run ruff check src/gtasks_manager/tui/
   ```

3. ✅ Code formatted:
   ```bash
   uv run ruff format src/gtasks_manager/tui/
   ```

4. ✅ Manual TUI testing confirms feature works

5. ✅ No regressions in existing functionality:
   ```bash
   uv run pytest tests/integration/test_tui_navigation.py -v
   ```

## Additional Resources

- **Textual Documentation**: https://textual.textualize.io/guide/testing/
- **Textual App API**: https://textual.textualize.io/api/app/
- **Project Constitution**: `.specify/memory/constitution.md`
- **Feature Specification**: `specs/003-vim-keybindings/spec.md`
- **Implementation Plan**: `specs/003-vim-keybindings/plan.md`

## Next Steps

1. Review the test strategy in `plan.md`
2. Run existing tests to understand current behavior
3. Start with test-first approach for new features
4. Follow atomic commit pattern: each discrete task gets its own commit
5. Run full test suite before pushing

---

**Last Updated**: 2025-01-11
