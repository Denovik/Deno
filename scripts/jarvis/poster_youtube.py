import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import YOUTUBE_CLIENT_SECRET_PATH, BASE_DIR

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = os.path.join(BASE_DIR, "credentials", "youtube_token.pickle")


def _get_youtube_client():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_path = os.path.join(BASE_DIR, YOUTUBE_CLIENT_SECRET_PATH)
            if not os.path.exists(client_secret_path):
                raise FileNotFoundError(
                    f"YouTube Client Secret nicht gefunden: {client_secret_path}\n"
                    "Lade es von console.cloud.google.com herunter und lege es dort ab."
                )
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(video_path: str, title: str, description: str, tags: list) -> str:
    """Lädt Video zu YouTube hoch. Gibt Video-ID zurück."""
    print(f"[poster_youtube] Lade hoch: {title}")
    youtube = _get_youtube_client()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "26",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    video_id = response["id"]
    print(f"[poster_youtube] Hochgeladen: https://youtube.com/shorts/{video_id}")
    return video_id
