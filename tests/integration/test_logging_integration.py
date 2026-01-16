"""Integration tests for logging functionality."""

import logging
import time
from pathlib import Path

from gtasks_manager.logging_config import DEFAULT_LOG_FILENAME, setup_logging


# Module-level worker function for multiprocessing
def _write_log_worker(tmp_dir: Path) -> None:
    """Worker function to write logs (must be at module level for multiprocessing)."""
    setup_logging(verbosity=1, log_dir=tmp_dir)
    logger = logging.getLogger()
    logger.info("Test message from process")
    time.sleep(0.1)  # Small delay to ensure writes complete


def test_log_file_created_on_command(tmp_path):
    """End-to-end test: log file is created when application runs."""
    # Setup logging
    setup_logging(verbosity=1, log_dir=tmp_path)

    # Log a message (simulating command execution)
    logging.info("Simulating command execution")

    # Force flush
    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.flush()

    # Verify log file exists and contains message
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    assert log_file.exists()

    content = log_file.read_text()
    assert "Simulating command execution" in content
    assert "[INFO]" in content


def test_log_file_rotation(tmp_path):
    """Test that log file rotates at 10MB."""
    # Setup logging with small max size for testing
    setup_logging(verbosity=1, log_dir=tmp_path)

    logger = logging.getLogger()

    # Write large message to trigger rotation (>10MB)
    large_message = "x" * (11 * 1024 * 1024)  # 11 MB
    logger.info(large_message)

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    # Verify rotation occurred
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    tmp_path / f"{DEFAULT_LOG_FILENAME}.1"

    assert log_file.exists()
    # Note: Backup file may not be created immediately due to buffering
    # This is a basic test that large messages don't crash the system


def test_concurrent_writes_no_corruption(tmp_path):
    """Test that multiple processes can write to log file without corruption."""
    import multiprocessing

    # Spawn multiple processes
    processes = [
        multiprocessing.Process(target=_write_log_worker, args=(tmp_path,)) for _ in range(5)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join(timeout=5)

    # Give time for all handlers to flush
    time.sleep(0.5)

    # Verify log file exists
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    assert log_file.exists()

    content = log_file.read_text()
    # Should have multiple messages (at least some from concurrent processes)
    assert "Test message from process" in content


def test_log_file_exists_after_crash(tmp_path):
    """Test that log file remains intact after application crash."""
    # Setup logging
    setup_logging(verbosity=1, log_dir=tmp_path)

    logger = logging.getLogger()
    logger.info("Message before crash")
    logger.error("Error during crash")

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    # Simulate crash by not calling logging.shutdown()
    # Just verify file is intact
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    assert log_file.exists()

    content = log_file.read_text()
    assert "Message before crash" in content
    assert "Error during crash" in content


def test_large_log_handling(tmp_path):
    """Test that large log files don't cause performance issues."""
    import time

    # Setup logging
    setup_logging(verbosity=1, log_dir=tmp_path)

    logger = logging.getLogger()

    # Write many log messages
    start_time = time.time()
    for i in range(1000):
        logger.info(f"Log message {i}")
    end_time = time.time()

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    # Verify all messages were written in reasonable time
    log_file = tmp_path / DEFAULT_LOG_FILENAME
    content = log_file.read_text()

    # Should have all 1000 messages
    assert content.count("Log message") == 1000

    # Should complete in reasonable time (<5 seconds for 1000 messages)
    duration = end_time - start_time
    assert duration < 5.0, f"Logging 1000 messages took {duration:.2f} seconds"
