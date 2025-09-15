from pathlib import Path

HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".config" / "gtasks-manager"
TOKEN_FILE = CONFIG_DIR / "token.json"
TASK_CACHE_FILE = CONFIG_DIR / "task_cache.json"

SCOPES = ['https://www.googleapis.com/auth/tasks']

CLIENT_CONFIG = {
    "installed": {
        "client_id": "281058803066-2d5m6fpqome4311cs4692sb9kotj2s47.apps.googleusercontent.com",
        "project_id": "gtasks-manager",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost"],
        # not treated as an actual secret here,
        # see: https://developers.google.com/identity/protocols/oauth2#installed
        "client_secret": "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"
    }
}

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
