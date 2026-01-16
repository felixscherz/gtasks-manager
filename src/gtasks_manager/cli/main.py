import click

from gtasks_manager.adapters.google_tasks import GoogleTasksAdapter
from gtasks_manager.cli.commands.auth import auth, logout
from gtasks_manager.cli.commands.lists import lists
from gtasks_manager.cli.commands.tasks import complete, create, delete, list_tasks, update
from gtasks_manager.config import CONFIG_DIR
from gtasks_manager.core.services import TaskService
from gtasks_manager.core.task_cache import TaskCache
from gtasks_manager.logging_config import setup_logging

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


@cli.result_callback()
def process_result(result, **kwargs):
    # Ensure cache is saved after operations
    _cache.save(CONFIG_DIR / "task_cache.json")


@click.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v or -vv)")
@click.pass_context
def gui(ctx, verbose):
    """Launch TUI."""
    # Setup logging before launching TUI
    if not setup_logging(verbosity=verbose):
        # Logging setup failed, but continue with TUI
        pass

    from gtasks_manager.tui.app import TasksApp

    # Get service from context (passed by cli group)
    service = ctx.obj
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
