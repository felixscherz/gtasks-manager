"""Unit tests for config module."""

from pathlib import Path

from gtasks_manager.config import get_log_file_path


def test_get_log_file_path(tmp_path):
    """Test that get_log_file_path returns correct log file path."""
    # Mock get_log_dir to return tmp_path
    from unittest.mock import patch

    with patch("gtasks_manager.config.get_log_dir", return_value=tmp_path):
        log_path = get_log_file_path()
        assert tmp_path == Path(log_path).parent
        assert "gtasks.log" in log_path
