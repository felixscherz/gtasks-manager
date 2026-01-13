# Data Model: Add Application Logging

**Feature**: [spec.md](./spec.md)
**Date**: 2026-01-13

## Entities

### 1. Log Entry

**Purpose**: Represents a single logged event captured by the logging system

**Fields**:
- `timestamp: datetime` - When the log entry was created (ISO 8601 format with timezone)
- `level: LogLevel` - Severity of the log entry (DEBUG, INFO, WARNING, ERROR)
- `message: str` - The log message content
- `stack_trace: Optional[str]` - Stack trace if available (ERROR level only)

**Validation Rules**:
- Timestamp MUST be in ISO 8601 format with timezone offset (e.g., "2024-01-13T14:30:00-08:00")
- Level MUST be one of: DEBUG, INFO, WARNING, ERROR
- Message MUST not be empty
- Stack trace is optional, only present for ERROR level when exception info available

**State Transitions**: N/A (immutable log entries)

**Relationships**: None (log entries are stored sequentially in log file)

### 2. Log File

**Purpose**: Persistent storage for log entries at OS-specific location

**Fields**:
- `path: Path` - Full path to log file (OS-specific location)
- `name: str` - Base filename (e.g., "gtasks.log")
- `rotation_config: RotationConfig` - Configuration for log rotation

**Validation Rules**:
- Path MUST be valid for the target OS
- Parent directory MUST exist or be automatically created
- File MUST be writable (check permissions on startup)

**State Transitions**:
1. `NOT_CREATED` → `ACTIVE` when first log entry written
2. `ACTIVE` → `ROTATED` when file size reaches 10MB
3. `ROTATED` → `ARCHIVED` as backup file (gtasks.log.1, gtasks.log.2, etc.)

**Relationships**:
- Contains multiple LogEntry instances (chronologically ordered)
- Has one RotationConfig

### 3. Log Level

**Purpose**: Enumerated severity classification for log messages

**Values**:
- `DEBUG` (10) - Detailed information for diagnosing problems
- `INFO` (20) - General informational messages
- `WARNING` (30) - Something unexpected happened, but software is still working
- `ERROR` (40) - Due to a more serious problem, the software has not been able to perform some function
- `CRITICAL` (50) - A serious error, indicating that the program itself may be unable to continue running

**Mapping to CLI Flags**:
- No flag (-v count=0): WARNING and above (WARNING, ERROR, CRITICAL)
- -v flag (count=1): INFO and above (INFO, WARNING, ERROR, CRITICAL)
- -vv flag (count=2+): DEBUG and above (all levels)

**Validation Rules**:
- Only these 5 standard Python logging levels are supported
- Verbosity flag maps to minimum level (anything at or above this level is logged)

**State Transitions**: N/A (immutable enum values)

**Relationships**: None

### 4. Rotation Config

**Purpose**: Configuration for automatic log file rotation

**Fields**:
- `max_bytes: int` - Maximum size of log file before rotation (default: 10,485,760 bytes = 10MB)
- `backup_count: int` - Number of backup files to keep (default: 5)
- `naming_pattern: str` - Pattern for backup files (e.g., "gtasks.log.{n}")

**Validation Rules**:
- max_bytes MUST be positive (>= 1)
- backup_count MUST be non-negative integer (>= 0)
- Backup files are named with integer suffix (.1, .2, .3, etc.)
- When max_bytes exceeded, current file renamed to .1, .1 to .2, etc., up to backup_count
- Oldest backup files beyond backup_count are deleted

**State Transitions**: N/A (immutable configuration)

**Relationships**:
- Belongs to one LogFile

## Data Flow

```
CLI Command with -v flag
    ↓
Determine LogLevel from flag count
    ↓
Setup logging configuration
    ↓
Create LogFile at OS-specific location
    ↓
For each event in application:
    - Create LogEntry with timestamp, level, message
    - Append to LogFile
    - Check file size
    - If >= max_bytes: rotate log file (apply RotationConfig)
```

## Configuration Constants

```python
# Log file locations
DEFAULT_LOG_DIR_POSIX = "~/.config/gtasks-manager/logs/"
DEFAULT_LOG_DIR_WINDOWS = "%APPDATA%\\gtasks-manager\\logs\\"
DEFAULT_LOG_FILENAME = "gtasks.log"

# Rotation settings
MAX_LOG_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_FILE_COUNT = 5

# Log level mappings
VERBOSITY_TO_LOG_LEVEL = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

# Log format
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # ISO 8601 with timezone
```

## Validation Requirements

From FR-002: System MUST create directory structure automatically if not exists
- Validation: Check if directory exists before logging, create if missing

From FR-011: Clear error message when log file cannot be written
- Validation: Try to open log file in append mode on startup, catch permission errors
- Display user-friendly message if write fails

From SC-001: Log file creation within 100ms
- Performance requirement for first write operation
