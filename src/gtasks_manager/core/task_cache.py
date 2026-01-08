from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from .models import Task, TaskReference


@dataclass
class TaskCache:
    """Local cache for task index-to-ID mapping."""

    active_tasks: Dict[int, str]  # index -> task_id
    completed_tasks: Dict[int, str]
    last_updated: datetime

    def get_task_id(self, reference: TaskReference, completed: bool = False) -> Optional[str]:
        """Get task ID from reference (int index or str ID)."""
        if isinstance(reference, str):
            return reference  # Already an ID

        cache = self.completed_tasks if completed else self.active_tasks
        return cache.get(reference)

    def update(self, tasks: List[Task], completed: bool = False) -> None:
        """Update cache with task list."""
        cache = {}
        for idx, task in enumerate(tasks, start=1):
            cache[idx] = task.id

        if completed:
            self.completed_tasks = cache
        else:
            self.active_tasks = cache

        self.last_updated = datetime.utcnow()
