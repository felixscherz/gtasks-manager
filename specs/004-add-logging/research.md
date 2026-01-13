# Research: Add Application Logging

**Feature**: [spec.md](./spec.md)
**Date**: 2026-01-13

## Research Topics

### Topic 1: Python Logging Module Best Practices for CLI Applications

**Decision**: Use Python's built-in `logging` module with `FileHandler`, configured early in application startup

**Rationale**:
- Python's logging module is battle-tested, thread-safe, and widely adopted
- Provides built-in support for log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Supports multiple handlers (file + console) without extra dependencies
- Includes automatic timestamp formatting
- Handles concurrent writes safely via locking mechanism

**Alternatives Considered**:
- loguru: More user-friendly API but adds external dependency, not needed for simple file logging
- structlog: Better for structured logging but overkill for this use case

**Key Findings**:
- Configure logging once at application startup (in cli.py or dedicated logging module)
- Use `logging.config.dictConfig` or `logging.basicConfig` for setup
- Set formatter to include timestamp, level name, and message
- Use `RotatingFileHandler` or `TimedRotatingFileHandler` for log rotation
- FileHandler uses OS-level file locking, safe for concurrent writes from multiple processes

### Topic 2: Cross-Platform Log File Location Handling

**Decision**: Use `pathlib.Path` with platform detection for log file paths

**Rationale**:
- Python's `pathlib.Path` provides cross-platform path handling
- Can detect OS and use appropriate base directory:
  - macOS/Linux: `~/.config/gtasks-manager/logs/`
  - Windows: `%APPDATA%\gtasks-manager\logs\`
- Existing codebase already uses pathlib (from config.py inspection)
- Automatic directory creation with `Path.mkdir(parents=True, exist_ok=True)`

**Alternatives Considered**:
- `os.path` module: Lower-level API, more verbose
- `appdirs` library: Would add external dependency, not needed for simple config directory
- Hardcoded paths: Would fail on different platforms

**Key Findings**:
```python
import sys
from pathlib import Path

if sys.platform == "win32":
    base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
else:
    base_dir = Path.home() / ".config"

log_dir = base_dir / "gtasks-manager" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
```

### Topic 3: Log Rotation Strategies

**Decision**: Use `RotatingFileHandler` with maxBytes=10MB and backupCount=5

**Rationale**:
- Built-in to Python logging module (no extra dependencies)
- Automatic rotation when file size limit reached
- Keeps backup files (gtasks.log.1, gtasks.log.2, etc.)
- Meets requirement SC-006: "Log file size does not exceed 10 MB"

**Alternatives Considered**:
- `TimedRotatingFileHandler`: Rotates based on time (daily, hourly), but size-based is more predictable for disk usage
- `WatchedFileHandler`: Only useful for external log rotation tools
- Manual rotation in code: More complex, error-prone

**Key Findings**:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

### Topic 4: Concurrent Write Handling in Python Logging

**Decision**: Rely on Python logging's built-in thread/process safety with FileHandler

**Rationale**:
- Python's logging module has built-in locking mechanism
- FileHandler uses `threading.Lock` for thread safety
- For process-safe concurrent writes, use `ConcurrentLogHandler` or rely on OS file locking
- Existing codebase doesn't mention multiprocessing, assuming single-process CLI
- If multiple CLI instances run simultaneously, OS file locking in FileHandler handles it

**Alternatives Considered**:
- `ConcurrentLogHandler` from `concurrent-log-handler` package: External dependency, may be overkill
- Named pipes or sockets: Too complex for simple file logging
- Separate log files per PID: Would make log collection difficult

**Key Findings**:
- Standard FileHandler is sufficient for most CLI use cases
- FileHandler uses OS-level file locking which prevents corruption
- If multiprocessing is introduced, consider `ConcurrentLogHandler` or process-safe queues

### Topic 5: Click CLI -v Flag Implementation Patterns

**Decision**: Add global -v/--verbose option with count=True to support multiple levels

**Rationale**:
- Click's `@click.option` with `count=True` allows -v, -vv, -vvv
- Existing codebase uses Click extensively (from cli.py inspection)
- Can set log level based on verbosity count:
  - 0 (default): WARNING
  - 1 (-v): INFO
  - 2+ (-vv, -vvv): DEBUG
- Global option means it works for all subcommands

**Alternatives Considered**:
- Multiple separate flags (--verbose, --debug): More verbose to use
- Environment variable: Less discoverable for CLI users
- Config file setting: Not ideal for temporary debugging sessions

**Key Findings**:
```python
@click.command()
@click.option('-v', '--verbose', count=True, help='Increase verbosity level')
def cli(verbose):
    # Map count to log level
    log_levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    log_level = log_levels.get(verbose, logging.DEBUG)
    setup_logging(log_level)
```

## Decisions Summary

1. **Logging Framework**: Python built-in `logging` module
2. **Log File Handler**: `RotatingFileHandler` with 10MB max size, 5 backup files
3. **Log File Location**: OS-specific using `pathlib.Path` (`~/.config/gtasks-manager/logs/` or `%APPDATA%\gtasks-manager\logs\`)
4. **Concurrency**: Rely on FileHandler's OS file locking
5. **CLI Integration**: Click `count=True` option for -v/-vv flags
6. **Log Levels**: WARNING (default), INFO (-v), DEBUG (-vv)
7. **Log Format**: Timestamp with timezone, level name, message (+ stack trace for errors)
8. **Testing**: pytest for unit tests, integration tests for file operations

## Implementation Notes

- Configure logging in a new `logging_config.py` module
- Call `setup_logging()` early in cli.py before command execution
- Use try/except around log file operations with clear error messages (FR-011)
- Document log file location in `--help` output (FR-012)
- Add log configuration to existing config.py constants
- Write unit tests for:
  - Log file creation at correct location
  - Log level filtering based on -v flag
  - Log rotation at 10MB
  - Error messages for permission issues
- Write integration tests for:
  - Concurrent writes from multiple processes
  - Cross-platform path handling
