"""
Daten: YouTube-Sammler

Holt Channel-Statistiken und Video-Performance vom Mindwave-Kanal.
Nutzt den bestehenden OAuth-Token aus credentials/youtube_daten_token.pickle.

Erzeugte Tabellen: youtube_daily, youtube_videos
"""

import pickle
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TOKEN_PATH = BASE_DIR / "credentials" / "youtube_daten_token.pickle"
CLIENT_SECRET_PATH = BASE_DIR / "credentials" / "youtube_client_secret.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _get_youtube_client():
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    if not creds or not creds.valid:
        return None, "YouTube-Token fehlt oder abgelaufen — bitte erneuern"

    return build("youtube", "v3", credentials=creds), None


def collect():
    if not TOKEN_PATH.exists():
        return {
            "source": "youtube", "status": "skipped",
            "reason": "youtube_daten_token.pickle fehlt"
        }

    try:
        youtube, err = _get_youtube_client()
        if err:
            return {"source": "youtube", "status": "skipped", "reason": err}

        # Channel-Statistiken
        channel_resp = youtube.channels().list(
            part="statistics,snippet", mine=True
        ).execute()

        if not channel_resp.get("items"):
            return {"source": "youtube", "status": "error", "reason": "Channel nicht gefunden"}

        stats = channel_resp["items"][0]["statistics"]
        snippet = channel_resp["items"][0]["snippet"]

        channel_data = {
            "channel_name": snippet.get("title", ""),
            "channel_id": channel_resp["items"][0]["id"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "total_videos": int(stats.get("videoCount", 0)),
        }

        # Letzte Videos (30 Tage)
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        search_resp = youtube.search().list(
            part="id", channelId=channel_data["channel_id"], type="video",
            publishedAfter=thirty_days_ago, order="date", maxResults=50
        ).execute()

        video_ids = [
            item["id"]["videoId"]
            for item in search_resp.get("items", [])
            if "videoId" in item.get("id", {})
        ]

        videos = []
        total_views_30d = 0

        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            vid_resp = youtube.videos().list(
                part="statistics,snippet,contentDetails",
                id=",".join(batch)
            ).execute()

            for item in vid_resp.get("items", []):
                vid_stats = item.get("statistics", {})
                views = int(vid_stats.get("viewCount", 0))
                total_views_30d += views
                videos.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published": item["snippet"]["publishedAt"][:10],
                    "views": views,
                    "likes": int(vid_stats.get("likeCount", 0)),
                    "comments": int(vid_stats.get("commentCount", 0)),
                    "duration": item.get("contentDetails", {}).get("duration", ""),
                })

        return {
            "source": "youtube",
            "status": "success",
            "data": {
                "channel": channel_data,
                "videos_30d": videos,
                "total_views_30d": total_views_30d,
                "videos_published_30d": len(videos),
            }
        }

    except Exception as e:
        return {"source": "youtube", "status": "error", "reason": str(e)}


def write(conn, result, date):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_daily (
            date TEXT PRIMARY KEY,
            channel_name TEXT,
            subscribers INTEGER,
            total_views INTEGER,
            total_videos INTEGER,
            views_30d INTEGER,
            videos_published_30d INTEGER,
            collected_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_videos (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            published_date TEXT,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            duration TEXT,
            last_updated TEXT
        )
    """)

    if result.get("status") != "success":
        conn.commit()
        return 0

    data = result["data"]
    channel = data["channel"]
    collected_at = datetime.now(timezone.utc).isoformat()
    records = 0

    conn.execute(
        "INSERT OR REPLACE INTO youtube_daily "
        "(date, channel_name, subscribers, total_views, total_videos, "
        "views_30d, videos_published_30d, collected_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (date, channel["channel_name"], channel["subscribers"],
         channel["total_views"], channel["total_videos"],
         data["total_views_30d"], data["videos_published_30d"], collected_at)
    )
    records += 1

    for video in data.get("videos_30d", []):
        conn.execute(
            "INSERT OR REPLACE INTO youtube_videos "
            "(video_id, title, published_date, views, likes, comments, duration, last_updated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (video["video_id"], video["title"], video["published"],
             video["views"], video["likes"], video["comments"],
             video["duration"], date)
        )
        records += 1

    conn.commit()
    return records


if __name__ == "__main__":
    result = collect()
    if result["status"] == "success":
        ch = result["data"]["channel"]
        print(f"Channel: {ch['channel_name']}")
        print(f"Abonnenten: {ch['subscribers']:,}")
        print(f"Videos (30 Tage): {result['data']['videos_published_30d']}")
        print(f"Aufrufe (30 Tage): {result['data']['total_views_30d']:,}")
    else:
        print(f"{result['status']}: {result.get('reason', '')}")
