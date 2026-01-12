import json

from .config import TASK_CACHE_FILE, ensure_config_dir


class TaskCache:
    def __init__(self):
        ensure_config_dir()
        self.cache = {}

    def store_tasks(self, tasks: list[dict], show_completed: bool = False):
        cache_key = "completed" if show_completed else "active"
        task_map = {}

        for i, task in enumerate(tasks, 1):
            task_map[str(i)] = {
                "id": task["id"],
                "title": task.get("title", "Untitled"),
                "status": task.get("status", "needsAction"),
            }

        self.cache[cache_key] = task_map

        try:
            with open(TASK_CACHE_FILE, "w") as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def get_task_id(self, reference: str, show_completed: bool = False) -> str | None:
        cache_key = "completed" if show_completed else "active"

        try:
            with open(TASK_CACHE_FILE) as f:
                self.cache = json.load(f)
        except Exception:
            return None

        task_map = self.cache.get(cache_key, {})

        if reference in task_map:
            return task_map[reference]["id"]

        for task_info in task_map.values():
            if task_info["id"] == reference:
                return reference

        return None

    def clear(self):
        try:
            if TASK_CACHE_FILE.exists():
                TASK_CACHE_FILE.unlink()
        except Exception:
            pass
