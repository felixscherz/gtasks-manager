import click
from typing import List, Optional
from datetime import datetime
from gtasks_manager.core.models import Task, TaskList, TaskStatus


class CLIFormatter:
    """Formats domain models for CLI output."""

    @staticmethod
    def format_tasks(tasks: List[Task], show_completed: bool = False) -> str:
        """Format a list of tasks."""
        if not tasks:
            return "No tasks found."

        lines = []
        for i, task in enumerate(tasks, start=1):
            status = "✓" if task.status == TaskStatus.COMPLETED else "○"
            due = f" (due: {task.due.date()})" if task.due else ""
            lines.append(f"{i:2d}. {status} {task.title} (ID: {task.id}){due}")

        return "\n".join(lines)

    @staticmethod
    def format_task_lists(task_lists: List[TaskList]) -> str:
        """Format a list of task lists."""
        if not task_lists:
            return "No task lists found."

        lines = []
        for i, tl in enumerate(task_lists, start=1):
            default = "*" if tl.id == "@default" else " "
            lines.append(f"{i:2d}. {default} {tl.title} (ID: {tl.id})")

        return "\n".join(lines)

    @staticmethod
    def format_success(message: str) -> str:
        """Format a success message."""
        return f"✓ {message}"

    @staticmethod
    def format_error(message: str) -> str:
        """Format an error message."""
        return f"✗ Error: {message}"
