import json
from pathlib import Path
from typing import Optional

from gtasks_manager.config import ensure_config_dir


class StorageAdapter:
    """Storage adapter for token and cache using filesystem."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        ensure_config_dir()

    def save_json(self, filename: str, data: dict) -> None:
        """Save data to a JSON file."""
        file_path = self.config_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        # Ensure secure permissions for token file
        if filename == "token.json":
            file_path.chmod(0o600)

    def load_json(self, filename: str) -> Optional[dict]:
        """Load data from a JSON file."""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def delete_file(self, filename: str) -> bool:
        """Delete a file from the config directory."""
        file_path = self.config_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
