import pytest
from gtasks_manager.tui.keybindings import KeyBindingManager


class TestKeyBindingManager:
    """Tests for KeyBindingManager."""

    def test_initial_state_enabled(self):
        """Test that KeyBindingManager starts enabled by default."""
        manager = KeyBindingManager()
        assert manager.is_enabled() is True

    def test_initial_state_disabled(self):
        """Test that KeyBindingManager can start disabled."""
        manager = KeyBindingManager(enabled=False)
        assert manager.is_enabled() is False

    def test_get_action_when_enabled(self):
        """Test getting action when bindings are enabled."""
        manager = KeyBindingManager(enabled=True)
        assert manager.get_action("j") == "move_down"
        assert manager.get_action("k") == "move_up"
        assert manager.get_action("h") == "move_left"
        assert manager.get_action("l") == "move_right"
        assert manager.get_action("Enter") == "toggle_completion"

    def test_get_action_when_disabled(self):
        """Test getting action returns None when bindings are disabled."""
        manager = KeyBindingManager(enabled=False)
        assert manager.get_action("j") is None
        assert manager.get_action("k") is None

    def test_get_action_unmapped_key(self):
        """Test getting action for unmapped key returns None."""
        manager = KeyBindingManager()
        assert manager.get_action("x") is None
        assert manager.get_action("a") is None

    def test_set_enabled_true(self):
        """Test enabling bindings."""
        manager = KeyBindingManager(enabled=False)
        manager.set_enabled(True)
        assert manager.is_enabled() is True

    def test_set_enabled_false(self):
        """Test disabling bindings."""
        manager = KeyBindingManager(enabled=True)
        manager.set_enabled(False)
        assert manager.is_enabled() is False

    def test_update_mapping(self):
        """Test updating a key mapping."""
        manager = KeyBindingManager()
        manager.update_mapping("x", "custom_action")
        assert manager.get_action("x") == "custom_action"

    def test_update_mapping_overwrites_existing(self):
        """Test that updating a mapping overwrites the old one."""
        manager = KeyBindingManager()
        manager.update_mapping("j", "new_action")
        assert manager.get_action("j") == "new_action"
        assert manager.get_action("j") != "move_down"

    def test_remove_mapping_existing_key(self):
        """Test removing an existing mapping."""
        manager = KeyBindingManager()
        assert manager.get_action("j") == "move_down"
        removed = manager.remove_mapping("j")
        assert removed is True
        assert manager.get_action("j") is None

    def test_remove_mapping_nonexistent_key(self):
        """Test removing a non-existent mapping."""
        manager = KeyBindingManager()
        removed = manager.remove_mapping("x")
        assert removed is False
