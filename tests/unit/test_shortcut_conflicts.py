from gtasks_manager.tui.keybindings import KeyBindingManager


class TestShortcutConflicts:
    """Unit tests ensuring non-VIM shortcuts still work when VIM bindings are enabled."""

    def test_vim_bindings_enabled_by_default(self):
        """Test that VIM bindings are enabled by default."""
        manager = KeyBindingManager()
        assert manager.is_enabled() is True

    def test_disabling_vim_bindings_returns_none_for_vim_keys(self):
        """Test that disabling VIM bindings returns None for VIM keys."""
        manager = KeyBindingManager(enabled=False)
        assert manager.get_action("j") is None
        assert manager.get_action("k") is None
        assert manager.get_action("h") is None
        assert manager.get_action("l") is None

    def test_non_vim_keys_always_return_none(self):
        """Test that non-VIM keys always return None regardless of enabled state."""
        manager = KeyBindingManager(enabled=True)
        assert manager.get_action("c") is None
        assert manager.get_action("d") is None
        assert manager.get_action("a") is None

        manager.set_enabled(False)
        assert manager.get_action("c") is None
        assert manager.get_action("d") is None
        assert manager.get_action("a") is None

    def test_custom_mappings_can_be_added_without_conflict(self):
        """Test that custom mappings can be added without affecting existing ones."""
        manager = KeyBindingManager()
        manager.update_mapping("x", "custom_action")
        assert manager.get_action("x") == "custom_action"
        assert manager.get_action("j") == "move_down"
        assert manager.get_action("k") == "move_up"

    def test_custom_mapping_overwrites_vim_mapping(self):
        """Test that custom mappings can overwrite VIM bindings."""
        manager = KeyBindingManager()
        manager.update_mapping("j", "custom_action")
        assert manager.get_action("j") == "custom_action"
        assert manager.get_action("j") != "move_down"
