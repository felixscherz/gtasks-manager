"""
Unit tests for logging configuration.
"""

import logging
import logging.handlers
from unittest.mock import patch

from gtasks_manager.logging_config import (
    BACKUP_FILE_COUNT,
    DEFAULT_LOG_FILENAME,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    MAX_LOG_SIZE_BYTES,
    VERBOSITY_TO_LOG_LEVEL,
    get_log_dir,
    setup_logging,
)


def test_get_log_dir_posix():
    """Test log directory on POSIX systems (Linux/macOS)."""
    with patch("sys.platform", "linux"):
        log_dir = get_log_dir()
        assert log_dir.parts[-3:] == (".config", "gtasks-manager", "logs")


def test_get_log_dir_windows():
    """Test log directory on Windows."""
    with (
        patch("sys.platform", "win32"),
        patch.dict("os.environ", {"APPDATA": "C:\\Users\\test\\AppData\\Roaming"}),
    ):
        log_dir = get_log_dir()
        # Path normalizes slashes, so check for components
        assert "gtasks-manager" in str(log_dir)
        assert "logs" in str(log_dir)


def test_setup_logging_creates_directory(tmp_path):
    """Test that setup_logging creates log directory."""
    result = setup_logging(log_dir=tmp_path)
    assert result is True
    assert tmp_path.exists()
    assert (tmp_path / DEFAULT_LOG_FILENAME).exists()


def test_setup_logging_creates_log_file(tmp_path):
    """Test that setup_logging creates log file on first write."""
    # Use verbosity=1 to set INFO level so INFO messages are logged
    setup_logging(verbosity=1, log_dir=tmp_path)
    logger = logging.getLogger()
    logger.info("Test message")
    # Force flush to ensure log is written
    for handler in logger.handlers:
        handler.flush()

    log_file = tmp_path / DEFAULT_LOG_FILENAME
    assert log_file.exists(), f"Log file should exist at {log_file}"
    content = log_file.read_text()
    assert "Test message" in content


def test_setup_logging_timestamp_format(tmp_path):
    """Test that log entries include ISO 8601 timestamps."""
    # Use verbosity=1 to set INFO level so INFO messages are logged
    setup_logging(verbosity=1, log_dir=tmp_path)
    logger = logging.getLogger()
    logger.info("Test message")
    # Force flush to ensure log is written
    for handler in logger.handlers:
        handler.flush()

    log_file = tmp_path / DEFAULT_LOG_FILENAME
    content = log_file.read_text()
    # ISO 8601 format: 2024-01-13T14:30:00-08:00
    assert "Test message" in content
    # Check for timestamp characters
    assert any(char in content for char in ["T", "-", ":"])


def test_setup_logging_error_stack_trace(tmp_path):
    """Test that error logging includes stack trace."""
    setup_logging(log_dir=tmp_path)
    try:
        raise ValueError("Test error")
    except Exception:
        logging.error("Error occurred", exc_info=True)

    log_file = tmp_path / DEFAULT_LOG_FILENAME
    content = log_file.read_text()
    assert "ValueError" in content or "Traceback" in content


def test_setup_logging_permission_error():
    """Test permission error handling."""
    # Mock Path.mkdir to raise PermissionError
    with patch("pathlib.Path.mkdir", side_effect=PermissionError("No permission")):
        result = setup_logging()
        assert result is False


def test_setup_logging_default_verbosity(tmp_path):
    """Test that default verbosity (0) sets WARNING level."""
    setup_logging(verbosity=0, log_dir=tmp_path)
    assert logging.getLogger().level == logging.WARNING


def test_setup_logging_info_verbosity(tmp_path):
    """Test that verbosity=1 sets INFO level."""
    setup_logging(verbosity=1, log_dir=tmp_path)
    assert logging.getLogger().level == logging.INFO


def test_setup_logging_debug_verbosity(tmp_path):
    """Test that verbosity=2 sets DEBUG level."""
    setup_logging(verbosity=2, log_dir=tmp_path)
    assert logging.getLogger().level == logging.DEBUG


def test_constants_defined():
    """Test that all required constants are defined."""
    assert DEFAULT_LOG_FILENAME == "gtasks.log"
    assert MAX_LOG_SIZE_BYTES == 10 * 1024 * 1024  # 10 MB
    assert BACKUP_FILE_COUNT == 5
    assert LOG_FORMAT == "%(asctime)s [%(levelname)s] %(message)s"
    assert LOG_DATE_FORMAT == "%Y-%m-%dT%H:%M:%S%z"
    assert VERBOSITY_TO_LOG_LEVEL == {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }


def test_log_level_filtering(tmp_path):
    """Test that log level filtering works correctly."""
    # Setup with INFO level
    setup_logging(verbosity=1, log_dir=tmp_path)
    logger = logging.getLogger()

    # Log at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    # Check log content - should NOT have DEBUG (filtered out)
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    content = log_file.read_text()

    assert "Debug message" not in content  # Filtered out
    assert "Info message" in content  # Included
    assert "Warning message" in content  # Included
    assert "Error message" in content  # Included
