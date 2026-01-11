class KeyBindingManager:
    """Manages VIM-style keybindings for the TUI."""

    DEFAULT_MAPPINGS: dict[str, str] = {
        "j": "move_down",
        "k": "move_up",
        "h": "move_left",
        "l": "move_right",
        "enter": "toggle_completion",
    }

    def __init__(self, enabled: bool = True):
        """Initialize KeyBindingManager.

        Args:
            enabled: Whether VIM bindings are enabled (default True)
        """
        self.enabled = enabled
        self.mappings: dict[str, str] = self.DEFAULT_MAPPINGS.copy()

    def get_action(self, key: str) -> str | None:
        """Get the action associated with a key.

        Args:
            key: The key pressed (e.g., 'j', 'k', 'Enter')

        Returns:
            The action name if key is mapped and bindings are enabled, else None
        """
        if not self.enabled:
            return None
        return self.mappings.get(key)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable VIM bindings.

        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled

    def is_enabled(self) -> bool:
        """Check if VIM bindings are currently enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.enabled

    def update_mapping(self, key: str, action: str) -> None:
        """Update or add a key mapping.

        Args:
            key: The key to bind
            action: The action to associate with the key
        """
        self.mappings[key] = action

    def remove_mapping(self, key: str) -> bool:
        """Remove a key mapping.

        Args:
            key: The key to unbind

        Returns:
            True if mapping existed and was removed, False otherwise
        """
        if key in self.mappings:
            del self.mappings[key]
            return True
        return False
