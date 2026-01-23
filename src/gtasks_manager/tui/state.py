from dataclasses import dataclass
from datetime import datetime


@dataclass
class TUISelectionState:
    """Tracks the currently selected task in the TUI and preserves selection across state changes."""

    task_id: str
    preserved: bool = False
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TaskListMetadata:
    """Stores information about the current task list being displayed in the TUI."""

    list_id: str
    name: str
    fetched_at: datetime | None = None
    is_cached: bool = False

    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now()


@dataclass
class TUIApplicationState:
    """Manages overall TUI application state including selection, list metadata, and UI mode."""

    selection: TUISelectionState | None = None
    current_list: TaskListMetadata | None = None
    is_loading: bool = False
    error_message: str | None = None
