from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .models import Task, TaskReference


@dataclass
class TaskCache:
    """Local cache for task index-to-ID mapping."""

    active_tasks: dict[int, str]  # index -> task_id
    completed_tasks: dict[int, str]
    last_updated: datetime

    def get_task_id(self, reference: TaskReference, completed: bool = False) -> str | None:
        """Get task ID from reference (int index or str ID)."""
        if isinstance(reference, str):
            return reference  # Already an ID

        cache = self.completed_tasks if completed else self.active_tasks
        return cache.get(reference)

    def update(self, tasks: list[Task], completed: bool = False) -> None:
        """Update cache with task list."""
        cache = {}
        for idx, task in enumerate(tasks, start=1):
            cache[idx] = task.id

        if completed:
            self.completed_tasks = cache
        else:
            self.active_tasks = cache

        self.last_updated = datetime.utcnow()

    @classmethod
    def load(cls, path: Path | None = None) -> "TaskCache":
        """Load cache from a file or return empty if not found."""
        if not path or not path.exists():
            return cls(active_tasks={}, completed_tasks={}, last_updated=datetime.utcnow())

        import json

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                return cls(
                    active_tasks={int(k): v for k, v in data.get("active_tasks", {}).items()},
                    completed_tasks={int(k): v for k, v in data.get("completed_tasks", {}).items()},
                    last_updated=datetime.fromisoformat(data["last_updated"])
                    if "last_updated" in data
                    else datetime.utcnow(),
                )
        except Exception:
            return cls(active_tasks={}, completed_tasks={}, last_updated=datetime.utcnow())

    def save(self, path: Path) -> None:
        """Save cache to a file."""
        import json

        data = {
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "last_updated": self.last_updated.isoformat(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
