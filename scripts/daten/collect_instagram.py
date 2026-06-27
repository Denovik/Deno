"""
Daten: Instagram-Sammler

Holt Follower-Zahl und Post-Anzahl vom mind.wave26-Konto.
Nutzt META_ACCESS_TOKEN und INSTAGRAM_ACCOUNT_ID aus der .env.

Erzeugte Tabelle: instagram_daily
"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

try:
    import requests
except ImportError:
    raise ImportError("Paket 'requests' fehlt: pip install requests")

GRAPH_API = "https://graph.instagram.com/v21.0"


def collect():
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()

    if not token:
        return {
            "source": "instagram", "status": "skipped",
            "reason": "META_ACCESS_TOKEN fehlt in .env"
        }
    if not account_id:
        return {
            "source": "instagram", "status": "skipped",
            "reason": "INSTAGRAM_ACCOUNT_ID fehlt in .env"
        }

    try:
        resp = requests.get(
            f"{GRAPH_API}/{account_id}",
            params={"fields": "followers_count,media_count,username", "access_token": token},
            timeout=15,
        )
        if resp.status_code != 200:
            return {
                "source": "instagram", "status": "error",
                "reason": f"HTTP {resp.status_code}: {resp.text[:100]}"
            }
        data = resp.json()
        return {
            "source": "instagram",
            "status": "success",
            "data": {
                "username": data.get("username", ""),
                "followers": data.get("followers_count", 0),
                "media_count": data.get("media_count", 0),
            }
        }
    except Exception as e:
        return {"source": "instagram", "status": "error", "reason": str(e)}


def write(conn, result, date):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS instagram_daily (
            date TEXT PRIMARY KEY,
            username TEXT,
            followers INTEGER,
            media_count INTEGER,
            collected_at TEXT
        )
    """)

    if result.get("status") != "success":
        conn.commit()
        return 0

    data = result["data"]
    collected_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        "INSERT OR REPLACE INTO instagram_daily "
        "(date, username, followers, media_count, collected_at) VALUES (?, ?, ?, ?, ?)",
        (date, data["username"], data["followers"], data["media_count"], collected_at)
    )
    conn.commit()
    return 1


if __name__ == "__main__":
    result = collect()
    if result["status"] == "success":
        d = result["data"]
        print(f"Account: @{d['username']}")
        print(f"Follower: {d['followers']:,}")
        print(f"Posts: {d['media_count']:,}")
    else:
        print(f"{result['status']}: {result.get('reason', '')}")
