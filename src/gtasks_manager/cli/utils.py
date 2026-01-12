import click

from gtasks_manager.cli.formatters import CLIFormatter
from gtasks_manager.core.exceptions import APIError, AuthenticationError


def handle_exception(e: Exception):
    """Handle domain exceptions and echo user-friendly messages."""
    if isinstance(e, AuthenticationError):
        click.echo(
            CLIFormatter.format_error("Authentication failed. Please run 'gtasks auth'."),
            err=True,
        )
    elif isinstance(e, APIError):
        click.echo(CLIFormatter.format_error(f"API Error: {e}"), err=True)
    else:
        click.echo(CLIFormatter.format_error(str(e)), err=True)
