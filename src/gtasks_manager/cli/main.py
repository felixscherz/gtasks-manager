import click
from typing import Optional

from gtasks_manager.adapters.google_tasks import GoogleTasksAdapter
from gtasks_manager.core.task_cache import TaskCache
from gtasks_manager.core.services import TaskService
from gtasks_manager.core.exceptions import APIError, AuthenticationError
from gtasks_manager.config import CONFIG_DIR
from gtasks_manager.cli.formatters import CLIFormatter

# Dependency Injection / Bootstrap
_adapter = GoogleTasksAdapter()
_cache = TaskCache.load(CONFIG_DIR / "task_cache.json")
_service = TaskService(_adapter, _cache)


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """Google Tasks Manager CLI."""
    ctx.obj = _service


def handle_exception(e: Exception):
    """Handle domain exceptions and echo user-friendly messages."""
    if isinstance(e, AuthenticationError):
        click.echo(
            CLIFormatter.format_error("Authentication failed. Please run 'gtasks auth'."), err=True
        )
    elif isinstance(e, APIError):
        click.echo(CLIFormatter.format_error(f"API Error: {e}"), err=True)
    else:
        click.echo(CLIFormatter.format_error(str(e)), err=True)


@cli.result_callback()
def process_result(result, **kwargs):
    # Ensure cache is saved after operations
    _cache.save(CONFIG_DIR / "task_cache.json")


# Command imports
from .commands.auth import auth, logout
from .commands.tasks import create, list_tasks, update, delete, complete
from .commands.lists import lists


@click.command()
@click.pass_obj
def gui(service):
    """Launch the TUI."""
    from gtasks_manager.tui.app import TasksApp

    app = TasksApp(service)
    app.run()


cli.add_command(auth)
cli.add_command(logout)
cli.add_command(create)
cli.add_command(list_tasks, name="list")
cli.add_command(update)
cli.add_command(delete)
cli.add_command(complete)
cli.add_command(lists)
cli.add_command(gui)

if __name__ == "__main__":
    cli()
