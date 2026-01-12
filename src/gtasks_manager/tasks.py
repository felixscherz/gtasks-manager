from datetime import datetime
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import get_credentials


class TasksManager:
    def __init__(self, force_reauth=False):
        self.creds = get_credentials(force_reauth)
        self.service = build("tasks", "v1", credentials=self.creds)

    def get_task_lists(self) -> list[dict[str, Any]]:
        try:
            results = self.service.tasklists().list().execute()
            return results.get("items", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_default_task_list_id(self) -> str | None:
        task_lists = self.get_task_lists()
        if task_lists:
            return task_lists[0]["id"]
        return None

    def create_task(
        self,
        title: str,
        notes: str | None = None,
        due_date: str | None = None,
        task_list_id: str | None = None,
    ) -> dict[str, Any] | None:
        if not task_list_id:
            task_list_id = self.get_default_task_list_id()
            if not task_list_id:
                print("No task lists found.")
                return None

        task = {
            "title": title,
        }

        if notes:
            task["notes"] = notes

        if due_date:
            task["due"] = due_date

        try:
            result = self.service.tasks().insert(tasklist=task_list_id, body=task).execute()
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def list_tasks(
        self, task_list_id: str | None = None, show_completed: bool = False
    ) -> list[dict[str, Any]]:
        if not task_list_id:
            task_list_id = self.get_default_task_list_id()
            if not task_list_id:
                print("No task lists found.")
                return []

        try:
            if show_completed:
                results = (
                    self.service.tasks()
                    .list(tasklist=task_list_id, showCompleted=True, showHidden=True)
                    .execute()
                )
            else:
                results = self.service.tasks().list(tasklist=task_list_id).execute()

            return results.get("items", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def complete_task(self, task_id: str, task_list_id: str | None = None) -> bool:
        if not task_list_id:
            task_list_id = self.get_default_task_list_id()
            if not task_list_id:
                print("No task lists found.")
                return False

        try:
            task = self.service.tasks().get(tasklist=task_list_id, task=task_id).execute()

            task["status"] = "completed"
            task["completed"] = datetime.utcnow().isoformat() + "Z"

            self.service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()

            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def delete_task(self, task_id: str, task_list_id: str | None = None) -> bool:
        if not task_list_id:
            task_list_id = self.get_default_task_list_id()
            if not task_list_id:
                print("No task lists found.")
                return False

        try:
            self.service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def toggle_task_completion(self, task_id: str, task_list_id: str | None = None) -> bool:
        if not task_list_id:
            task_list_id = self.get_default_task_list_id()
            if not task_list_id:
                print("No task lists found.")
                return False

        try:
            task = self.service.tasks().get(tasklist=task_list_id, task=task_id).execute()

            current_status = task.get("status", "needsAction")
            if current_status == "completed":
                task["status"] = "needsAction"
                task["completed"] = None
            else:
                task["status"] = "completed"
                task["completed"] = datetime.utcnow().isoformat() + "Z"

            self.service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()

            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
