from textual.app import App
from textual.widgets import Input


def is_focused_on_input(app: App) -> bool:
    """Check if currently focused widget is an Input widget.

    Args:
        app: The Textual app instance

    Returns:
        True if focused widget is an Input, False otherwise
    """
    focused = app.focused
    return isinstance(focused, Input)


def show_transient_notification(app: App, message: str, duration: float = 3.0) -> None:
    """Display a transient notification in app.

    Args:
        app: The Textual app instance
        message: The message to display
        duration: How long to show the notification in seconds
    """
    from textual.widgets import RichLog

    log = app.query_one(RichLog)
    if log:
        log.write(message)


def announce_for_accessibility(app: App, message: str) -> None:
    """Announce a message for accessibility (screen readers).

    Args:
        app: The Textual app instance
        message: The message to announce
    """
    focused = app.focused
    if focused:
        focused.focus()
