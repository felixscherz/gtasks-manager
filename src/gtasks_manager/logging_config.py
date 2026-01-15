"""Logging configuration for gtasks-manager CLI application."""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

# Log file configuration
DEFAULT_LOG_FILENAME = "gtasks.log"
MAX_LOG_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_FILE_COUNT = 5

# Log format
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

# Verbosity to log level mapping
VERBOSITY_TO_LOG_LEVEL = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def get_log_dir() -> Path:
    """Get the OS-specific log directory."""
    if sys.platform == "win32":
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base_dir = Path.home() / ".config"

    log_dir = base_dir / "gtasks-manager" / "logs"
    return log_dir


def setup_logging(verbosity: int = 0, log_dir: Path | None = None) -> bool:
    """
    Configure application logging.

    Args:
        verbosity: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
        log_dir: Custom log directory (uses default if None)

    Returns:
        bool: True if logging configured successfully, False otherwise
    """
    try:
        # Get log directory and create if needed
        if log_dir is None:
            log_dir = get_log_dir()

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / DEFAULT_LOG_FILENAME

        # Get log level from verbosity
        log_level = VERBOSITY_TO_LOG_LEVEL.get(verbosity, logging.DEBUG)

        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE_BYTES,
            backupCount=BACKUP_FILE_COUNT,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Add handler
        root_logger.addHandler(file_handler)

        # Log startup message
        logging.info("Logging started - Level: %s", logging.getLevelName(log_level))

        return True

    except (PermissionError, OSError) as e:
        # Print error to stderr since logging may not be available
        print(f"Warning: Could not configure logging: {e}", file=sys.stderr)
        return False
