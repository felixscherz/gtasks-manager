import click
from gtasks_manager.cli.formatters import CLIFormatter
from gtasks_manager.cli.main import handle_exception


@click.command()
@click.argument("title")
@click.option("--notes", help="Task notes")
@click.option("--due", help="Due date (YYYY-MM-DD)")
@click.option("--list-id", help="Target task list ID")
@click.pass_obj
def create(service, title, notes, due, list_id):
    """Create a new task."""
    try:
        list_id = list_id or "@default"
        from datetime import datetime

        due_dt = datetime.fromisoformat(due) if due else None
        task = service.create_task(list_id, title, notes, due_dt)
        click.echo(CLIFormatter.format_success(f"Created: {task.title} (ID: {task.id})"))
    except Exception as e:
        handle_exception(e)


@click.command(name="list")
@click.option("--completed", is_flag=True, help="Show completed tasks")
@click.option("--list-id", help="Task list ID")
@click.pass_obj
def list_tasks(service, completed, list_id):
    """List tasks."""
    try:
        list_id = list_id or "@default"
        tasks = service.list_tasks(list_id, show_completed=completed)
        click.echo(CLIFormatter.format_tasks(tasks, show_completed=completed))
    except Exception as e:
        handle_exception(e)


@click.command()
@click.argument("reference")
@click.option("--list-id", help="Task list ID")
@click.pass_obj
def complete(service, reference, list_id):
    """Mark a task as completed."""
    try:
        list_id = list_id or "@default"
        try:
            ref = int(reference)
        except ValueError:
            ref = reference

        task = service.complete_task(list_id, ref)
        click.echo(CLIFormatter.format_success(f"Completed: {task.title}"))
    except Exception as e:
        handle_exception(e)


@click.command()
@click.argument("reference")
@click.option("--title", help="New title")
@click.option("--notes", help="New notes")
@click.option("--due", help="New due date (YYYY-MM-DD)")
@click.option("--list-id", help="Task list ID")
@click.pass_obj
def update(service, reference, title, notes, due, list_id):
    """Update a task."""
    try:
        list_id = list_id or "@default"
        try:
            ref = int(reference)
        except ValueError:
            ref = reference

        from datetime import datetime

        due_dt = datetime.fromisoformat(due) if due else None

        task = service.update_task(list_id, ref, title=title, notes=notes, due=due_dt)
        click.echo(CLIFormatter.format_success(f"Updated: {task.title}"))
    except Exception as e:
        handle_exception(e)


@click.command()
@click.argument("reference")
@click.option("--list-id", help="Task list ID")
@click.pass_obj
def delete(service, reference, list_id):
    """Delete a task."""
    try:
        list_id = list_id or "@default"
        try:
            ref = int(reference)
        except ValueError:
            ref = reference

        service.delete_task(list_id, ref)
        click.echo(CLIFormatter.format_success("Deleted task."))
    except Exception as e:
        handle_exception(e)
