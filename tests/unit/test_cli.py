from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gtasks_manager.cli.main import cli


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


class TestCLIDefaultTUILaunch:
    """Tests for CLI default TUI launch behavior (User Story 1)."""

    @patch("gtasks_manager.cli.main.launch_tui")
    def test_cli_launches_tui_when_no_subcommand(self, mock_launch, runner):
        """Test that running gtasks with no subcommand launches TUI."""
        runner.invoke(cli, [], catch_exceptions=False)
        mock_launch.assert_called_once()


class TestCLIGUICommand:
    """Tests for GUI command backward compatibility (User Story 1)."""

    @patch("gtasks_manager.cli.main.launch_tui")
    def test_gui_command_launches_tui(self, mock_launch, runner):
        """Test that gtasks gui command launches TUI."""
        runner.invoke(cli, ["gui"])
        mock_launch.assert_called_once()


class TestCLIExistingCommands:
    """Tests that existing CLI commands remain unchanged (User Story 2)."""

    def test_existing_commands_unchanged_auth(self, runner):
        """Test that auth command still exists and works."""
        result = runner.invoke(cli, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Authenticate with Google Tasks" in result.output or "auth" in result.output

    def test_existing_commands_unchanged_list(self, runner):
        """Test that list command still exists and works."""
        result = runner.invoke(cli, ["list", "--help"])
        assert result.exit_code == 0
        assert "List all tasks" in result.output or "list" in result.output

    def test_existing_commands_unchanged_create(self, runner):
        """Test that create command still exists and works."""
        result = runner.invoke(cli, ["create", "--help"])
        assert result.exit_code == 0
        assert "Create a new task" in result.output or "create" in result.output

    def test_existing_commands_unchanged_complete(self, runner):
        """Test that complete command still exists and works."""
        result = runner.invoke(cli, ["complete", "--help"])
        assert result.exit_code == 0
        assert "Mark a task as completed" in result.output or "complete" in result.output

    def test_existing_commands_unchanged_delete(self, runner):
        """Test that delete command still exists and works."""
        result = runner.invoke(cli, ["delete", "--help"])
        assert result.exit_code == 0
        assert "Delete a task" in result.output or "delete" in result.output
