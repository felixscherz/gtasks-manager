from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import CLIENT_CONFIG, SCOPES, TOKEN_FILE, ensure_config_dir


def get_credentials(force_reauth=False):
    ensure_config_dir()

    creds = None

    if not force_reauth and TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid or force_reauth:
        if creds and creds.expired and creds.refresh_token and not force_reauth:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def clear_credentials():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    print("Credentials cleared. Run 'gtasks auth' to re-authenticate.")
