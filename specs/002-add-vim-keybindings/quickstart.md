# Quickstart: VIM Keybindings (TUI)

This quickstart covers using VIM-style keybindings in the gtasks-manager TUI.

Prerequisites:
- Install the project in editable mode: `pip install -e .`
- Development workflow: use `uv` for running dev commands (e.g., `uv run pytest`, `uv run python -m gtasks_manager.tui.app`).
- Launch the TUI: `uv run python -m gtasks_manager.tui.app` (or run `gtasks tui` if CLI entrypoint is installed)

Usage:
- Navigation:
  - `j`: Move selection down
  - `k`: Move selection up
  - `h`: Move focus left (if pane exists)
  - `l`: Move focus right (if pane exists)
- Toggle completion:
  - `Enter`: Toggle selected task between completed and pending

Notes:
- VIM keybindings are enabled by default. To disable, open settings and toggle `KeyBindingManager.enabled` or run `gtasks config set keybindings.vim false` (future CLI config command).
- Keybindings do not trigger when typing into text inputs.
- If persistence fails when toggling, the UI will briefly show an error message and revert the visual change.

Testing:
- Run `pytest tests/unit/test_task_cache.py::test_toggle_completion_optimistic` (future test name example) to validate toggle behavior.

(End of quickstart)
