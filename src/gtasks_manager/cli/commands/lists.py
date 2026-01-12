import click

from gtasks_manager.cli.formatters import CLIFormatter
from gtasks_manager.cli.main import handle_exception


@click.command()
@click.pass_obj
def lists(service):
    """List all task lists."""
    try:
        task_lists = service.list_task_lists()
        click.echo(CLIFormatter.format_task_lists(task_lists))
    except Exception as e:
        handle_exception(e)
