import logging
from datetime import datetime

import click

from .auth import clear_credentials
from .logging_config import setup_logging
from .task_cache import TaskCache
from .tasks import TasksManager


def format_task(task, index: int | None = None):
    title = task.get("title", "Untitled")
    status = task.get("status", "needsAction")
    due = task.get("due")
    notes = task.get("notes", "")
    task_id = task.get("id", "")

    status_symbol = "✓" if status == "completed" else "○"

    if index is not None:
        result = f"{index}. {status_symbol} {title} (ID: {task_id})"
    else:
        result = f"{status_symbol} {title} (ID: {task_id})"

    if due:
        try:
            due_date = datetime.fromisoformat(due.replace("Z", "+00:00"))
            result += f" (due: {due_date.strftime('%Y-%m-%d')})"
        except ValueError:
            pass

    if notes:
        result += f"\n   Notes: {notes}"

    return result


def resolve_task_reference(reference: str, show_completed: bool = False) -> str | None:
    cache = TaskCache()
    task_id = cache.get_task_id(reference, show_completed)

    if not task_id:
        click.echo(f"Task not found: {reference}")
        click.echo("Run 'gtasks list' to see available tasks with their numbers and IDs.")
        return None

    return task_id


@click.group()
@click.version_option()
def main():
    """Google Tasks Manager - Manage your Google Tasks from the command line.

    \b
    Logging:
      Logs are written to OS-specific location (e.g., ~/.config/gtasks-manager/logs/gtasks.log)
      Use -v or -vv flag for increased logging verbosity.
    """


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.argument("title")
@click.option("--notes", "-n", help="Task notes/description")
@click.option("--due", "-d", help="Due date (YYYY-MM-DD format)")
def create(verbose: int, title: str, notes: str | None, due: str | None):
    """Create a new task."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'create' command with title: %s", title)

    try:
        manager = TasksManager()

        due_date = None
        if due:
            try:
                parsed_date = datetime.strptime(due, "%Y-%m-%d")
                due_date = parsed_date.isoformat() + "Z"
            except ValueError:
                click.echo("Invalid date format. Use YYYY-MM-DD.")
                return

        task = manager.create_task(title, notes, due_date)
        if task:
            click.echo(f"Task created: {task['title']}")
        else:
            click.echo("Failed to create task.")
    except Exception as e:
        logging.error(f"Error in create command: {e}", exc_info=True)
        click.echo(f"Error: {e}")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.option("--completed", "-c", is_flag=True, help="Show completed tasks")
def list(verbose: int, completed: bool):
    """List all tasks."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'list' command (show_completed=%s)", completed)

    try:
        manager = TasksManager()
        tasks = manager.list_tasks(show_completed=completed)

        if not tasks:
            click.echo("No tasks found.")
            return

        cache = TaskCache()
        cache.store_tasks(tasks, completed)

        for i, task in enumerate(tasks, 1):
            click.echo(format_task(task, index=i))
    except Exception as e:
        logging.error(f"Error in list command: {e}", exc_info=True)
        click.echo(f"Error: {e}")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.argument("task_reference")
def complete(verbose: int, task_reference: str):
    """Mark a task as completed. Use task number (from list) or task ID."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'complete' command with task_reference: %s", task_reference)

    try:
        task_id = resolve_task_reference(task_reference)
        if not task_id:
            return

        manager = TasksManager()
        if manager.complete_task(task_id):
            click.echo("Task marked as completed.")
        else:
            click.echo("Failed to complete task.")
    except Exception as e:
        logging.error(f"Error in complete command: {e}", exc_info=True)
        click.echo(f"Error: {e}")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.argument("task_reference")
def delete(verbose: int, task_reference: str):
    """Delete a task. Use task number (from list) or task ID."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'delete' command with task_reference: %s", task_reference)

    try:
        task_id = resolve_task_reference(task_reference)
        if not task_id:
            return

        manager = TasksManager()
        if manager.delete_task(task_id):
            click.echo("Task deleted.")
        else:
            click.echo("Failed to delete task.")
    except Exception as e:
        logging.error(f"Error in delete command: {e}", exc_info=True)
        click.echo(f"Error: {e}")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
def lists(verbose: int):
    """List all task lists."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'lists' command")

    try:
        manager = TasksManager()
        task_lists = manager.get_task_lists()

        if not task_lists:
            click.echo("No task lists found.")
            return

        for task_list in task_lists:
            click.echo(f"• {task_list['title']} (ID: {task_list['id']})")
    except Exception as e:
        logging.error(f"Error in lists command: {e}", exc_info=True)
        click.echo(f"Error: {e}")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.option("--force", is_flag=True, help="Force re-authentication")
def auth(verbose: int, force):
    """Authenticate with Google Tasks."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'auth' command (force=%s)", force)

    try:
        click.echo("Authenticating with Google...")
        if force:
            click.echo("Forcing re-authentication...")

        TasksManager(force_reauth=force)

        click.echo("✓ Authentication successful!")
        click.echo("You can now use all gtasks commands.")
    except Exception as e:
        logging.error(f"Error in auth command: {e}", exc_info=True)
        click.echo(f"✗ Authentication failed: {e}")
        click.echo("\nTroubleshooting:")
        click.echo("1. Check your internet connection")
        click.echo("2. Try running: gtasks auth --force")


@main.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
def logout(verbose: int):
    """Clear stored credentials and logout."""
    # Setup logging before command execution
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with command
        pass

    # Log command execution
    logging.info("Running 'logout' command")

    clear_credentials()


if __name__ == "__main__":
    main()
