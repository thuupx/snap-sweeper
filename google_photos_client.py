from os.path import join, dirname
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]


def get_google_photos_client():
    creds = None
    token_path = join(dirname(__file__), "google-token.json")

    # The file google-token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print(f"Credential file found, expired?: {creds.expired}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credential expired, refreshing...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                return None
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                join(dirname(__file__), "client_id.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            print(f"Credential saved to {token_path}")

    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)


google_photos = get_google_photos_client()
