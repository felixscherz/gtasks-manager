import click
from datetime import datetime
from typing import Optional

from .tasks import TasksManager
from .auth import clear_credentials


def format_task(task):
    title = task.get('title', 'Untitled')
    status = task.get('status', 'needsAction')
    due = task.get('due')
    notes = task.get('notes', '')
    
    status_symbol = '✓' if status == 'completed' else '○'
    
    result = f"{status_symbol} {title}"
    
    if due:
        try:
            due_date = datetime.fromisoformat(due.replace('Z', '+00:00'))
            result += f" (due: {due_date.strftime('%Y-%m-%d')})"
        except:
            pass
    
    if notes:
        result += f"\n   Notes: {notes}"
    
    return result


@click.group()
@click.version_option()
def main():
    """Google Tasks Manager - Manage your Google Tasks from the command line."""
    pass


@main.command()
@click.argument('title')
@click.option('--notes', '-n', help='Task notes/description')
@click.option('--due', '-d', help='Due date (YYYY-MM-DD format)')
def create(title: str, notes: Optional[str], due: Optional[str]):
    """Create a new task."""
    try:
        manager = TasksManager()
        
        due_date = None
        if due:
            try:
                parsed_date = datetime.strptime(due, '%Y-%m-%d')
                due_date = parsed_date.isoformat() + 'Z'
            except ValueError:
                click.echo("Invalid date format. Use YYYY-MM-DD.")
                return
        
        task = manager.create_task(title, notes, due_date)
        if task:
            click.echo(f"Task created: {task['title']}")
        else:
            click.echo("Failed to create task.")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--completed', '-c', is_flag=True, help='Show completed tasks')
def list(completed: bool):
    """List all tasks."""
    try:
        manager = TasksManager()
        tasks = manager.list_tasks(show_completed=completed)
        
        if not tasks:
            click.echo("No tasks found.")
            return
        
        for task in tasks:
            click.echo(format_task(task))
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
@click.argument('task_id')
def complete(task_id: str):
    """Mark a task as completed."""
    try:
        manager = TasksManager()
        if manager.complete_task(task_id):
            click.echo("Task marked as completed.")
        else:
            click.echo("Failed to complete task.")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
@click.argument('task_id')
def delete(task_id: str):
    """Delete a task."""
    try:
        manager = TasksManager()
        if manager.delete_task(task_id):
            click.echo("Task deleted.")
        else:
            click.echo("Failed to delete task.")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
def lists():
    """List all task lists."""
    try:
        manager = TasksManager()
        task_lists = manager.get_task_lists()
        
        if not task_lists:
            click.echo("No task lists found.")
            return
        
        for task_list in task_lists:
            click.echo(f"• {task_list['title']} (ID: {task_list['id']})")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--force', is_flag=True, help='Force re-authentication')
def auth(force):
    """Authenticate with Google Tasks."""
    try:
        click.echo("Authenticating with Google...")
        if force:
            click.echo("Forcing re-authentication...")
        
        manager = TasksManager(force_reauth=force)
        
        click.echo("✓ Authentication successful!")
        click.echo("You can now use all gtasks commands.")
        
    except Exception as e:
        click.echo(f"✗ Authentication failed: {e}")
        click.echo("\nTroubleshooting:")
        click.echo("1. Check your internet connection")
        click.echo("2. Try running: gtasks auth --force")


@main.command()
def logout():
    """Clear stored credentials and logout."""
    clear_credentials()


if __name__ == '__main__':
    main()