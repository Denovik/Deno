"""
Daten: Dashboard

Visuelles Web-Dashboard für deine Geschäftszahlen.
Start: python scripts/daten/dashboard.py → http://localhost:8002
"""

import sqlite3
import json
from pathlib import Path
from flask import Flask, render_template_string

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "data.db"

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def query_one(sql, params=()):
    conn = get_db()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return dict(row) if row else None


TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mindwave Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
    padding: 32px 24px;
  }
  .header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 40px;
  }
  .logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #4f8ef7, #9b59f7);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
  }
  .header h1 { font-size: 22px; font-weight: 600; color: #fff; }
  .header p { font-size: 13px; color: #666; margin-top: 2px; }

  .refresh-btn {
    margin-left: auto;
    background: rgba(79,142,247,0.15);
    border: 1px solid rgba(79,142,247,0.3);
    color: #4f8ef7;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    text-decoration: none;
  }
  .refresh-btn:hover { background: rgba(79,142,247,0.25); }

  .section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 16px;
    margin-top: 40px;
  }
  .section-title:first-of-type { margin-top: 0; }

  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 8px;
  }
  .card {
    background: #13131a;
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 20px;
  }
  .card .label {
    font-size: 12px;
    color: #555;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .card .value {
    font-size: 32px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
  }
  .card .sub {
    font-size: 12px;
    color: #444;
    margin-top: 6px;
  }
  .card.highlight {
    border-color: #4f8ef7;
    background: linear-gradient(135deg, rgba(79,142,247,0.08), rgba(155,89,247,0.05));
  }
  .card.green { border-color: #27ae60; background: rgba(39,174,96,0.06); }
  .card.purple { border-color: #9b59f7; background: rgba(155,89,247,0.06); }

  .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
  }
  .dot.blue { background: #4f8ef7; }
  .dot.red { background: #e74c3c; }
  .dot.green { background: #27ae60; }
  .dot.purple { background: #9b59f7; }

  table {
    width: 100%;
    border-collapse: collapse;
    background: #13131a;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #1e1e2e;
  }
  th {
    text-align: left;
    padding: 14px 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    color: #555;
    text-transform: uppercase;
    border-bottom: 1px solid #1e1e2e;
    background: #0f0f16;
  }
  td {
    padding: 14px 20px;
    font-size: 13px;
    border-bottom: 1px solid #111119;
    color: #ccc;
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,0.02); }
  td.num { font-variant-numeric: tabular-nums; color: #e0e0e0; font-weight: 500; }
  td.title-cell { max-width: 320px; }
  .title-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; display: block; }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
  }
  .badge.blue { background: rgba(79,142,247,0.15); color: #4f8ef7; }
  .badge.red { background: rgba(231,76,60,0.15); color: #e74c3c; }

  .trend-chart {
    background: #13131a;
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 8px;
  }
  .trend-chart h3 { font-size: 13px; color: #888; margin-bottom: 16px; font-weight: 500; }
  .bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  .bar-date { font-size: 11px; color: #444; width: 80px; flex-shrink: 0; }
  .bar-track { flex: 1; background: #1a1a24; border-radius: 4px; height: 24px; position: relative; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #4f8ef7, #9b59f7); transition: width 0.3s; display: flex; align-items: center; padding-left: 8px; min-width: 2px; }
  .bar-val { font-size: 11px; color: rgba(255,255,255,0.7); white-space: nowrap; }

  .footer { margin-top: 48px; text-align: center; font-size: 12px; color: #333; }
  .footer span { color: #444; }

  .empty { color: #333; font-style: italic; font-size: 13px; padding: 20px 0; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">⚡</div>
  <div>
    <h1>Mindwave Dashboard</h1>
    <p>Stand: {{ stand }}</p>
  </div>
  <a href="/" class="refresh-btn">↻ Aktualisieren</a>
</div>

<!-- YouTube -->
<div class="section-title">🎬 YouTube</div>
<div class="cards">
  <div class="card highlight">
    <div class="label"><span class="dot red"></span> Abonnenten</div>
    <div class="value">{{ yt.subscribers | fmt }}</div>
    <div class="sub">Stand {{ yt.date }}</div>
  </div>
  <div class="card">
    <div class="label"><span class="dot blue"></span> Views gesamt</div>
    <div class="value">{{ yt.total_views | fmt }}</div>
    <div class="sub">Kanal {{ yt.channel_name }}</div>
  </div>
  <div class="card">
    <div class="label"><span class="dot blue"></span> Views (30 Tage)</div>
    <div class="value">{{ yt.views_30d | fmt }}</div>
    <div class="sub">Letzte 30 Tage</div>
  </div>
  <div class="card">
    <div class="label"><span class="dot blue"></span> Videos gesamt</div>
    <div class="value">{{ yt.total_videos | fmt }}</div>
    <div class="sub">{{ yt.videos_published_30d }} davon letzte 30 Tage</div>
  </div>
</div>

{% if yt_trend %}
<div class="trend-chart" style="margin-top:16px">
  <h3>Views pro Tag (letzte {{ yt_trend|length }} Messungen)</h3>
  {% set max_val = yt_trend | map(attribute='views_30d') | max %}
  {% for row in yt_trend %}
  <div class="bar-row">
    <div class="bar-date">{{ row.date[5:] }}</div>
    <div class="bar-track">
      <div class="bar-fill" style="width: {{ ((row.views_30d or 0) / (max_val or 1) * 100)|int }}%">
        <span class="bar-val">{{ row.views_30d | fmt }}</span>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

{% if videos %}
<div class="section-title" style="margin-top:24px">📹 Videos (beste zuerst)</div>
<table>
  <thead>
    <tr>
      <th>Titel</th>
      <th>Views</th>
      <th>Likes</th>
      <th>Datum</th>
    </tr>
  </thead>
  <tbody>
    {% for v in videos %}
    <tr>
      <td class="title-cell"><span class="title-text">{{ v.title }}</span></td>
      <td class="num">{{ v.views | fmt }}</td>
      <td class="num">{{ v.likes | fmt }}</td>
      <td>{{ v.published_date }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endif %}

<!-- Instagram -->
<div class="section-title">📸 Instagram</div>
<div class="cards">
  <div class="card purple">
    <div class="label"><span class="dot purple"></span> Follower</div>
    <div class="value">{{ ig.followers | fmt }}</div>
    <div class="sub">@{{ ig.username }}</div>
  </div>
  <div class="card">
    <div class="label"><span class="dot purple"></span> Posts gesamt</div>
    <div class="value">{{ ig.media_count | fmt }}</div>
    <div class="sub">Stand {{ ig.date }}</div>
  </div>
</div>

<!-- Ziel -->
<div class="section-title">🎯 Ziel</div>
<div class="cards">
  <div class="card">
    <div class="label">Monatliches Ziel</div>
    <div class="value">2.000 €</div>
    <div class="sub">Deadline: Dezember 2026</div>
  </div>
  <div class="card">
    <div class="label">Aktuell</div>
    <div class="value">0 €</div>
    <div class="sub">Aufbauphase</div>
  </div>
  <div class="card">
    <div class="label">Noch nötig</div>
    <div class="value">2.000 €</div>
    <div class="sub">{{ monate_noch }} Monate bis Deadline</div>
  </div>
</div>

<div class="footer">
  Mindwave Dashboard · Daten lokal in <span>data/data.db</span> · Täglich um 08:00 aktualisiert
</div>

</body>
</html>
"""


@app.template_filter('fmt')
def fmt_number(value):
    if value is None:
        return "—"
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


@app.route("/")
def index():
    from datetime import datetime

    # YouTube
    yt = query_one("SELECT * FROM youtube_daily ORDER BY date DESC LIMIT 1") or {}
    yt_trend = query("SELECT date, views_30d FROM youtube_daily ORDER BY date DESC LIMIT 14")
    yt_trend = list(reversed(yt_trend))

    # Videos
    videos = query("SELECT title, views, likes, published_date FROM youtube_videos ORDER BY views DESC LIMIT 10")

    # Instagram
    ig = query_one("SELECT * FROM instagram_daily ORDER BY date DESC LIMIT 1") or {}

    # Monate bis Dez 2026
    now = datetime.now()
    deadline = datetime(2026, 12, 31)
    monate_noch = max(0, (deadline.year - now.year) * 12 + deadline.month - now.month)

    stand = yt.get("date") or ig.get("date") or "Keine Daten"

    return render_template_string(
        TEMPLATE,
        yt=yt,
        yt_trend=yt_trend,
        videos=videos,
        ig=ig,
        stand=stand,
        monate_noch=monate_noch,
    )


if __name__ == "__main__":
    import webbrowser, threading
    def open_browser():
        import time; time.sleep(1)
        webbrowser.open("http://localhost:8002")
    threading.Thread(target=open_browser, daemon=True).start()
    print("Dashboard startet → http://localhost:8002")
    app.run(host="127.0.0.1", port=8002, debug=False)
