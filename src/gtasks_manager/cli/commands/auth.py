import click

from gtasks_manager.cli.formatters import CLIFormatter
from gtasks_manager.cli.main import handle_exception


@click.command()
@click.option("--force", is_flag=True, help="Force re-authentication")
@click.pass_obj
def auth(service, force):
    """Authenticate with Google Tasks."""
    try:
        service.api.authenticate(force_reauth=force)
        click.echo(CLIFormatter.format_success("Successfully authenticated."))
    except Exception as e:
        handle_exception(e)


@click.command()
@click.pass_obj
def logout(service):
    """Log out and clear credentials."""
    from gtasks_manager.config import TOKEN_FILE

    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        click.echo(CLIFormatter.format_success("Logged out."))
    else:
        click.echo("Already logged out.")
