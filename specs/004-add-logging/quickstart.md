# Quickstart: Add Application Logging

**Feature**: [spec.md](./spec.md)
**Branch**: `004-add-logging`
**Date**: 2026-01-13

## Overview

This quickstart guide provides the essential information for implementing the logging feature in the gtasks-manager CLI application.

## Architecture

```
cli.py (entry point)
  ↓
logging_config.py (setup_logging function)
  ↓
Python logging module (writes to file)
  ↓
Log file at OS-specific location
```

## Key Files to Create/Modify

### 1. Create: `src/gtasks_manager/logging_config.py`

New module for logging configuration:

```python
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

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
    2: logging.DEBUG
}

def get_log_dir() -> Path:
    """Get the OS-specific log directory."""
    if sys.platform == "win32":
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base_dir = Path.home() / ".config"

    log_dir = base_dir / "gtasks-manager" / "logs"
    return log_dir

def setup_logging(verbosity: int = 0, log_dir: Optional[Path] = None) -> bool:
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

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE_BYTES,
            backupCount=BACKUP_FILE_COUNT
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

        # Add handler
        root_logger.addHandler(file_handler)

        # Log startup message
        logging.info("Logging started - Level: %s", logging.getLevelName(log_level))

        return True

    except (PermissionError, OSError) as e:
        # Print error to stderr since logging may not be available
        print(f"Warning: Could not configure logging: {e}", file=sys.stderr)
        return False
```

### 2. Modify: `src/gtasks_manager/cli.py`

Add -v flag option to Click CLI:

```python
import logging
from .logging_config import setup_logging, get_log_dir

@main.command()
@click.option('-v', '--verbose', count=True, help='Increase verbosity level (use -v or -vv)')
@click.pass_context
def list(ctx, verbose):
    """List tasks from Google Tasks."""
    # Setup logging first
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'list' command")

    try:
        manager = TasksManager()
        # ... existing implementation
    except Exception as e:
        logging.error(f"Error in list command: {e}", exc_info=True)
        click.echo(f"Error: {e}")
```

Add to all commands or make it a global option.

### 3. Modify: `src/gtasks_manager/config.py`

Add log file path constants:

```python
# Add to existing config.py
def get_log_file_path() -> str:
    """Get the log file path for display in help text."""
    from pathlib import Path
    import sys
    import os

    log_dir = get_log_dir()
    log_file = log_dir / DEFAULT_LOG_FILENAME
    return str(log_file)
```

## Implementation Steps

### Step 1: Create logging_config.py
- Create new file at `src/gtasks_manager/logging_config.py`
- Implement `get_log_dir()` function for OS-specific paths
- Implement `setup_logging()` function with RotatingFileHandler
- Handle directory creation and permission errors

### Step 2: Integrate with CLI
- Add -v/--verbose option to Click commands
- Call `setup_logging(verbosity)` early in command execution
- Add logging statements to key operations:
  - Command execution: `logging.info("Running 'list' command")`
  - API calls: `logging.debug("Fetching tasks from API")`
  - Errors: `logging.error(f"Error: {e}", exc_info=True)`

### Step 3: Update help text
- Add log file location to --help output
- Example: "Logs written to: ~/.config/gtasks-manager/logs/gtasks.log"

### Step 4: Write tests
- Unit tests for `get_log_dir()` (mock different platforms)
- Unit tests for `setup_logging()` (verify handler configuration)
- Integration tests for file creation and rotation
- Test concurrent writes (spawn multiple processes)

## Testing

### Unit Tests (`tests/unit/test_logging_config.py`)

```python
import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from gtasks_manager.logging_config import get_log_dir, setup_logging

def test_get_log_dir_posix(monkeypatch):
    """Test log directory on POSIX systems."""
    monkeypatch.setattr("sys.platform", "linux")
    log_dir = get_log_dir()
    assert str(log_dir).endswith(".config/gtasks-manager/logs")

def test_get_log_dir_windows(monkeypatch):
    """Test log directory on Windows."""
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("APPDATA", "C:\\Users\\test\\AppData\\Roaming")
    log_dir = get_log_dir()
    assert "AppData\\Roaming\\gtasks-manager\\logs" in str(log_dir)

def test_setup_logging_creates_directory(tmp_path):
    """Test that setup_logging creates log directory."""
    setup_logging(log_dir=tmp_path)
    assert tmp_path.exists()
    assert (tmp_path / "gtasks.log").exists()

def test_setup_logging_sets_log_level():
    """Test that verbosity maps to correct log level."""
    setup_logging(verbosity=0)
    assert logging.getLogger().level == logging.WARNING

    setup_logging(verbosity=1)
    assert logging.getLogger().level == logging.INFO

    setup_logging(verbosity=2)
    assert logging.getLogger().level == logging.DEBUG
```

### Integration Tests (`tests/integration/test_logging_integration.py`)

```python
import pytest
import logging
from pathlib import Path
from gtasks_manager.logging_config import setup_logging

def test_log_file_rotation(tmp_path):
    """Test that log file rotates at 10MB."""
    # Setup logging with small max size for testing
    setup_logging(log_dir=tmp_path)

    # Write large message to trigger rotation
    large_message = "x" * (11 * 1024 * 1024)  # 11 MB
    logging.info(large_message)

    # Verify rotation
    log_file = tmp_path / "gtasks.log"
    backup_file = tmp_path / "gtasks.log.1"
    assert log_file.exists()
    assert backup_file.exists()

def test_concurrent_writes(tmp_path):
    """Test that multiple processes can write to log file."""
    import multiprocessing

    def write_log():
        setup_logging(log_dir=tmp_path)
        logging.info("Test message from process")

    processes = [multiprocessing.Process(target=write_log) for _ in range(5)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    log_file = tmp_path / "gtasks.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message from process" in content
```

## Usage Examples

### Default logging (WARNING and ERROR only)

```bash
$ gtasks list
# Only warnings and errors logged
```

### Verbose logging (INFO level)

```bash
$ gtasks -v list
# Info, warnings, and errors logged
```

### Debug logging (DEBUG level)

```bash
$ gtasks -vv list
# All messages logged including debug information
```

### Viewing log file location

```bash
$ gtasks --help
# Help text includes:
# Logs written to: ~/.config/gtasks-manager/logs/gtasks.log
```

## Common Patterns

### Logging command execution

```python
logging.info("Running 'create' command with title: %s", title)
```

### Logging API calls

```python
logging.debug("Fetching tasks from Google Tasks API")
```

### Logging errors with stack trace

```python
try:
    result = api_call()
except Exception as e:
    logging.error(f"API call failed: {e}", exc_info=True)
    raise
```

### Conditional logging for performance

```python
if logging.getLogger().isEnabledFor(logging.DEBUG):
    # Only compute expensive debug info if DEBUG level is enabled
    debug_info = expensive_debug_computation()
    logging.debug("Debug info: %s", debug_info)
```

## Troubleshooting

### Permission errors

If log file cannot be written, user will see:
```
Warning: Could not configure logging: [Errno 13] Permission denied
```

Application continues to run without logging.

### Log rotation not working

Check:
- Log file is writable
- Disk space available
- No external processes holding file handles

### Concurrent writes causing issues

If multiple processes need to write, ensure:
- Each process calls `setup_logging()` independently
- FileHandler's OS file locking handles concurrent access
- Consider `concurrent-log-handler` package if issues persist

## Performance Considerations

- Log file creation: Should complete within 100ms (SC-001)
- Synchronous file I/O: May impact performance if excessive logging
- Consider async logging if performance issues observed
- Log rotation may cause brief pause when rotation occurs

## Next Steps

1. Review [data-model.md](./data-model.md) for detailed entity definitions
2. Run tests: `uv run pytest tests/unit/test_logging_config.py`
3. Run linting: `uv run ruff check src/gtasks_manager/logging_config.py`
4. Check log output after running commands
