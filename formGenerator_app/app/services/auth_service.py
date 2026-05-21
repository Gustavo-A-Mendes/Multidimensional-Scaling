import os
from googleapiclient.discovery import build

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

CREDENTIALS_DIR = os.path.join(
    BASE_DIR,
    "credentials"
)

TOKEN_PATH = os.path.join(
    CREDENTIALS_DIR,
    "token.json"
)

CLIENT_SECRET_PATH = os.path.join(
    CREDENTIALS_DIR,
    "client_secret.json"
)


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]


def authenticate():

    creds = None

    if os.path.exists(TOKEN_PATH):

        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_PATH,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


def try_auto_login():

    if not os.path.exists(TOKEN_PATH):
        return None

    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH,
        SCOPES
    )

    if not creds.valid:

        if creds.expired and creds.refresh_token:

            creds.refresh(Request())

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        else:
            return None

    return creds


def get_user_info(creds):

    service = build(
        "oauth2",
        "v2",
        credentials=creds
    )

    info = service.userinfo().get().execute()

    return {
        "name": info.get("name"),
        "email": info.get("email")
    }

