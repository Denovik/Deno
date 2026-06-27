"""
Mindwave Command Center Dashboard
Start: python scripts/daten/dashboard.py → http://localhost:8002
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "data.db"

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def q(sql, params=()):
    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q1(sql, params=()):
    conn = get_db()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return dict(row) if row else {}


@app.route("/api/data")
def api_data():
    yt = q1("SELECT * FROM youtube_daily ORDER BY date DESC LIMIT 1")
    ig = q1("SELECT * FROM instagram_daily ORDER BY date DESC LIMIT 1")
    yt_trend = q("SELECT date, subscribers, total_views, views_30d FROM youtube_daily ORDER BY date ASC")
    videos = q("SELECT title, views, likes, comments, published_date FROM youtube_videos ORDER BY views DESC LIMIT 10")
    ig_trend = q("SELECT date, followers, media_count FROM instagram_daily ORDER BY date ASC")

    now = datetime.now()
    deadline = datetime(2026, 12, 31)
    monate = max(0, (deadline.year - now.year) * 12 + deadline.month - now.month)
    tage = max(0, (deadline - now).days)

    return jsonify({
        "yt": yt,
        "ig": ig,
        "yt_trend": yt_trend,
        "ig_trend": ig_trend,
        "videos": videos,
        "monate_noch": monate,
        "tage_noch": tage,
        "last_updated": now.strftime("%d.%m.%Y %H:%M"),
    })


TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mindwave Command Center</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #07070f;
    --bg2: #0d0d1a;
    --bg3: #11111f;
    --border: #1a1a30;
    --border2: #222238;
    --text: #c8c8e0;
    --text-dim: #44445a;
    --text-muted: #2a2a40;
    --blue: #4a7fff;
    --blue-dim: rgba(74,127,255,0.15);
    --orange: #ff7c2a;
    --orange-dim: rgba(255,124,42,0.15);
    --green: #2aff8f;
    --green-dim: rgba(42,255,143,0.1);
    --purple: #a855f7;
    --purple-dim: rgba(168,85,247,0.12);
    --red: #ff4466;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    font-size: 12px;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* TOP BAR */
  .topbar {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 0 20px;
    height: 44px;
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .topbar-logo {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 700; color: #fff; letter-spacing: 2px;
  }
  .topbar-logo .orb {
    width: 22px; height: 22px;
    background: radial-gradient(circle, var(--orange) 0%, var(--blue) 100%);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--orange);
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100%{box-shadow:0 0 10px var(--orange)} 50%{box-shadow:0 0 20px var(--orange),0 0 40px rgba(255,124,42,0.3)} }

  .topbar-status { display: flex; gap: 16px; margin-left: auto; }
  .status-item { display: flex; align-items: center; gap: 5px; color: var(--text-dim); font-size: 10px; letter-spacing: 1px; }
  .status-dot { width: 6px; height: 6px; border-radius: 50%; }
  .status-dot.green { background: var(--green); box-shadow: 0 0 6px var(--green); animation: blink 2s ease-in-out infinite; }
  .status-dot.blue { background: var(--blue); }
  .status-dot.orange { background: var(--orange); }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .topbar-time { color: var(--blue); font-size: 11px; letter-spacing: 1px; }

  /* GRID */
  .grid {
    flex: 1;
    display: grid;
    grid-template-columns: 220px 1fr 1fr 220px;
    grid-template-rows: 1fr 1fr 140px;
    gap: 1px;
    background: var(--border);
    overflow: hidden;
  }
  .panel {
    background: var(--bg2);
    padding: 16px;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  .panel-title {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }
  .panel-title::before {
    content: '';
    display: inline-block;
    width: 2px; height: 10px;
    border-radius: 1px;
  }
  .panel-title.blue::before { background: var(--blue); }
  .panel-title.orange::before { background: var(--orange); }
  .panel-title.green::before { background: var(--green); }
  .panel-title.purple::before { background: var(--purple); }

  /* KPI CARDS (LEFT PANEL) */
  .kpi-stack { display: flex; flex-direction: column; gap: 10px; flex: 1; }
  .kpi {
    background: var(--bg3);
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 12px 14px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .kpi-label { font-size: 9px; letter-spacing: 1.5px; color: var(--text-dim); text-transform: uppercase; }
  .kpi-value { font-size: 26px; font-weight: 700; color: #fff; line-height: 1; margin: 6px 0; }
  .kpi-sub { font-size: 9px; color: var(--text-muted); }
  .kpi.blue { border-color: rgba(74,127,255,0.3); }
  .kpi.orange { border-color: rgba(255,124,42,0.3); }
  .kpi.green { border-color: rgba(42,255,143,0.25); }
  .kpi.purple { border-color: rgba(168,85,247,0.3); }

  /* CHARTS */
  .chart-wrap { flex: 1; position: relative; min-height: 0; }
  canvas { display: block; }

  /* VIDEO TABLE */
  .vtable { width: 100%; border-collapse: collapse; flex: 1; overflow: hidden; }
  .vtable th {
    font-size: 8px; letter-spacing: 1.5px; color: var(--text-dim);
    text-transform: uppercase; padding: 0 8px 8px; text-align: left;
    border-bottom: 1px solid var(--border2);
  }
  .vtable td {
    padding: 7px 8px; font-size: 10px; color: var(--text);
    border-bottom: 1px solid var(--bg3);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    max-width: 0;
  }
  .vtable tr:hover td { background: rgba(74,127,255,0.04); }
  .vtable .num { text-align: right; font-variant-numeric: tabular-nums; color: #fff; }
  .vtable .title-col { max-width: 200px; }
  .rank { color: var(--text-muted); font-size: 9px; width: 20px; }

  /* PROGRESS BAR */
  .progress-section { display: flex; flex-direction: column; gap: 12px; flex: 1; }
  .progress-item { flex: 1; }
  .progress-label { display: flex; justify-content: space-between; margin-bottom: 6px; }
  .progress-label span:first-child { font-size: 9px; letter-spacing: 1px; color: var(--text-dim); text-transform: uppercase; }
  .progress-label span:last-child { font-size: 11px; color: #fff; font-weight: 600; }
  .progress-track {
    background: var(--bg3); border-radius: 3px; height: 4px;
    border: 1px solid var(--border2); overflow: hidden;
  }
  .progress-fill { height: 100%; border-radius: 3px; transition: width 1.5s ease; }
  .progress-fill.blue { background: linear-gradient(90deg, var(--blue), #7eb8ff); box-shadow: 0 0 8px var(--blue); }
  .progress-fill.orange { background: linear-gradient(90deg, var(--orange), #ffb07a); box-shadow: 0 0 8px var(--orange); }

  /* BOTTOM TICKER */
  .ticker-panel {
    grid-column: 1 / -1;
    background: var(--bg2);
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 32px;
    overflow: hidden;
    flex-direction: row;
    flex-shrink: 0;
  }
  .ticker-label { font-size: 9px; letter-spacing: 2px; color: var(--text-dim); text-transform: uppercase; white-space: nowrap; }
  .ticker-items { display: flex; gap: 32px; overflow: hidden; }
  .ticker-item { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
  .ticker-item .k { font-size: 9px; color: var(--text-dim); letter-spacing: 1px; }
  .ticker-item .v { font-size: 13px; color: #fff; font-weight: 700; }
  .ticker-item .tag {
    font-size: 8px; padding: 2px 6px; border-radius: 3px;
    letter-spacing: 1px; text-transform: uppercase;
  }
  .tag.live { background: rgba(255,68,102,0.2); color: var(--red); border: 1px solid rgba(255,68,102,0.3); }
  .tag.auto { background: rgba(42,255,143,0.15); color: var(--green); border: 1px solid rgba(42,255,143,0.3); }
  .tag.wait { background: rgba(255,124,42,0.15); color: var(--orange); border: 1px solid rgba(255,124,42,0.3); }

  /* GOAL BIG */
  .goal-big { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; gap: 8px; }
  .goal-circle {
    width: 100px; height: 100px;
    border-radius: 50%;
    border: 2px solid var(--border2);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: radial-gradient(circle at center, rgba(74,127,255,0.08), transparent);
    box-shadow: 0 0 30px rgba(74,127,255,0.05);
    position: relative;
  }
  .goal-circle svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; transform: rotate(-90deg); }
  .goal-circle .inner { text-align: center; }
  .goal-circle .pct { font-size: 18px; font-weight: 700; color: #fff; }
  .goal-circle .lbl { font-size: 7px; letter-spacing: 1px; color: var(--text-dim); text-transform: uppercase; }
  .goal-stats { display: flex; gap: 16px; }
  .goal-stat { text-align: center; }
  .goal-stat .gv { font-size: 18px; font-weight: 700; color: #fff; }
  .goal-stat .gl { font-size: 8px; color: var(--text-dim); letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }

  .scan-line {
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px; background: linear-gradient(90deg, transparent, rgba(74,127,255,0.3), transparent);
    animation: scan 4s linear infinite;
    pointer-events: none;
  }
  @keyframes scan { from{top:0} to{top:100%} }
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-logo">
    <div class="orb"></div>
    MINDWAVE
  </div>
  <div class="status-item">
    <div class="status-dot green"></div>
    PIPELINE AKTIV
  </div>
  <div class="status-item">
    <div class="status-dot blue"></div>
    YOUTUBE LIVE
  </div>
  <div class="status-item">
    <div class="status-dot orange"></div>
    INSTAGRAM LIVE
  </div>
  <div class="topbar-status">
    <div class="status-item">TIKTOK: <span style="color:var(--orange);margin-left:4px">REVIEW</span></div>
  </div>
  <div class="topbar-time" id="clock">--:--:--</div>
</div>

<div class="grid">

  <!-- LINKS: KPIs -->
  <div class="panel" style="grid-row: 1 / 3;">
    <div class="panel-title blue">KPI OVERVIEW</div>
    <div class="kpi-stack">
      <div class="kpi blue">
        <div class="kpi-label">YT Abonnenten</div>
        <div class="kpi-value" id="yt-subs">—</div>
        <div class="kpi-sub">Mindwave Kanal</div>
      </div>
      <div class="kpi blue">
        <div class="kpi-label">YT Views gesamt</div>
        <div class="kpi-value" id="yt-views">—</div>
        <div class="kpi-sub" id="yt-views-sub">—</div>
      </div>
      <div class="kpi orange">
        <div class="kpi-label">YT Views 30 Tage</div>
        <div class="kpi-value" id="yt-30d">—</div>
        <div class="kpi-sub" id="yt-videos-sub">—</div>
      </div>
      <div class="kpi purple">
        <div class="kpi-label">IG Follower</div>
        <div class="kpi-value" id="ig-followers">—</div>
        <div class="kpi-sub">@mind.wave26</div>
      </div>
      <div class="kpi green">
        <div class="kpi-label">IG Posts</div>
        <div class="kpi-value" id="ig-posts">—</div>
        <div class="kpi-sub" id="ig-posts-sub">—</div>
      </div>
    </div>
    <div class="scan-line"></div>
  </div>

  <!-- MITTE OBEN: Views-Chart -->
  <div class="panel">
    <div class="panel-title blue">YOUTUBE · VIEWS (30 TAGE)</div>
    <div class="chart-wrap">
      <canvas id="chartViews"></canvas>
    </div>
  </div>

  <!-- MITTE RECHTS OBEN: Abonnenten-Chart -->
  <div class="panel">
    <div class="panel-title orange">YOUTUBE · ABONNENTEN</div>
    <div class="chart-wrap">
      <canvas id="chartSubs"></canvas>
    </div>
  </div>

  <!-- RECHTS: Ziel -->
  <div class="panel" style="grid-row: 1 / 3;">
    <div class="panel-title orange">ZIEL 2026</div>
    <div class="goal-big">
      <div class="goal-circle">
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="44" fill="none" stroke="#1a1a30" stroke-width="3"/>
          <circle id="goal-arc" cx="50" cy="50" r="44" fill="none" stroke="var(--blue)" stroke-width="3"
            stroke-dasharray="276.5" stroke-dashoffset="276.5" stroke-linecap="round"/>
        </svg>
        <div class="inner">
          <div class="pct" id="goal-pct">0%</div>
          <div class="lbl">Erreicht</div>
        </div>
      </div>
      <div class="goal-stats">
        <div class="goal-stat">
          <div class="gv" id="goal-monate">—</div>
          <div class="gl">Monate</div>
        </div>
        <div class="goal-stat">
          <div class="gv" id="goal-tage">—</div>
          <div class="gl">Tage</div>
        </div>
      </div>
      <div style="text-align:center;margin-top:8px;">
        <div style="font-size:9px;color:var(--text-dim);letter-spacing:1px">ZIEL</div>
        <div style="font-size:22px;font-weight:700;color:#fff">2.000 €</div>
        <div style="font-size:9px;color:var(--text-dim);letter-spacing:1px">/ MONAT</div>
      </div>
    </div>
    <div style="margin-top:16px;">
      <div class="panel-title green" style="margin-bottom:10px">FORTSCHRITT</div>
      <div class="progress-section">
        <div class="progress-item">
          <div class="progress-label">
            <span>YouTube</span>
            <span id="prog-yt-val">Live ✓</span>
          </div>
          <div class="progress-track"><div class="progress-fill blue" id="prog-yt" style="width:100%"></div></div>
        </div>
        <div class="progress-item">
          <div class="progress-label">
            <span>Instagram</span>
            <span id="prog-ig-val">Live ✓</span>
          </div>
          <div class="progress-track"><div class="progress-fill blue" id="prog-ig" style="width:100%"></div></div>
        </div>
        <div class="progress-item">
          <div class="progress-label">
            <span>TikTok</span>
            <span id="prog-tt-val">Review...</span>
          </div>
          <div class="progress-track"><div class="progress-fill orange" style="width:55%"></div></div>
        </div>
        <div class="progress-item">
          <div class="progress-label">
            <span>Einnahmen</span>
            <span>0 € / 2000 €</span>
          </div>
          <div class="progress-track"><div class="progress-fill orange" style="width:0%"></div></div>
        </div>
      </div>
    </div>
    <div class="scan-line"></div>
  </div>

  <!-- MITTE UNTEN LINKS: Top Videos -->
  <div class="panel" style="grid-column: 2 / 4;">
    <div class="panel-title green">TOP VIDEOS · PERFORMANCE</div>
    <table class="vtable">
      <thead>
        <tr>
          <th style="width:24px">#</th>
          <th class="title-col">Titel</th>
          <th style="text-align:right">Views</th>
          <th style="text-align:right">Likes</th>
          <th style="text-align:right">Datum</th>
        </tr>
      </thead>
      <tbody id="video-table"></tbody>
    </table>
  </div>

  <!-- BOTTOM TICKER -->
  <div class="ticker-panel">
    <div class="ticker-label">LIVE STATUS</div>
    <div class="ticker-items">
      <div class="ticker-item">
        <span class="k">PIPELINE</span>
        <span class="v">AKTIV</span>
        <span class="tag auto">AUTO</span>
      </div>
      <div class="ticker-item">
        <span class="k">YOUTUBE</span>
        <span class="v">ONLINE</span>
        <span class="tag live">LIVE</span>
      </div>
      <div class="ticker-item">
        <span class="k">INSTAGRAM</span>
        <span class="v">ONLINE</span>
        <span class="tag live">LIVE</span>
      </div>
      <div class="ticker-item">
        <span class="k">TIKTOK</span>
        <span class="v">WARTE</span>
        <span class="tag wait">REVIEW</span>
      </div>
      <div class="ticker-item">
        <span class="k">JARVIS</span>
        <span class="v">BEREIT</span>
        <span class="tag auto">KI</span>
      </div>
      <div class="ticker-item">
        <span class="k">DATEN</span>
        <span class="v">08:00</span>
        <span class="tag auto">TÄGLICH</span>
      </div>
      <div class="ticker-item">
        <span class="k">LETZTES UPDATE</span>
        <span class="v" id="last-update">—</span>
      </div>
    </div>
  </div>

</div>

<script>
let chartViews, chartSubs;

function fmt(n) {
  if (n == null) return '—';
  return parseInt(n).toLocaleString('de-DE');
}

function initCharts() {
  const defaults = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800 },
    plugins: { legend: { display: false }, tooltip: {
      backgroundColor: '#13131f',
      borderColor: '#2a2a40',
      borderWidth: 1,
      titleColor: '#888',
      bodyColor: '#fff',
    }},
    scales: {
      x: { grid: { color: '#111120' }, ticks: { color: '#333', font: { size: 9 }, maxRotation: 0, maxTicksLimit: 7 }},
      y: { grid: { color: '#111120' }, ticks: { color: '#333', font: { size: 9 }}, beginAtZero: true }
    }
  };

  chartViews = new Chart(document.getElementById('chartViews'), {
    type: 'line',
    data: { labels: [], datasets: [{
      data: [],
      borderColor: '#4a7fff',
      backgroundColor: 'rgba(74,127,255,0.08)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: '#4a7fff',
    }]},
    options: { ...defaults }
  });

  chartSubs = new Chart(document.getElementById('chartSubs'), {
    type: 'bar',
    data: { labels: [], datasets: [{
      data: [],
      backgroundColor: 'rgba(255,124,42,0.3)',
      borderColor: '#ff7c2a',
      borderWidth: 1,
      borderRadius: 3,
    }]},
    options: { ...defaults }
  });
}

function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('de-DE', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
}

async function loadData() {
  try {
    const res = await fetch('/api/data');
    const d = await res.json();

    // KPIs
    document.getElementById('yt-subs').textContent = fmt(d.yt.subscribers);
    document.getElementById('yt-views').textContent = fmt(d.yt.total_views);
    document.getElementById('yt-views-sub').textContent = `Stand ${d.yt.date || '—'}`;
    document.getElementById('yt-30d').textContent = fmt(d.yt.views_30d);
    document.getElementById('yt-videos-sub').textContent = `${d.yt.videos_published_30d || 0} Videos (30T)`;
    document.getElementById('ig-followers').textContent = fmt(d.ig.followers);
    document.getElementById('ig-posts').textContent = fmt(d.ig.media_count);
    document.getElementById('ig-posts-sub').textContent = `Stand ${d.ig.date || '—'}`;

    // Goal
    document.getElementById('goal-monate').textContent = d.monate_noch;
    document.getElementById('goal-tage').textContent = d.tage_noch;
    document.getElementById('last-update').textContent = d.last_updated;

    const pct = 0; // 0€ von 2000€
    document.getElementById('goal-pct').textContent = pct + '%';
    const circ = 276.5;
    document.getElementById('goal-arc').style.strokeDashoffset = circ - (circ * pct / 100);

    // Views Chart
    if (d.yt_trend && d.yt_trend.length > 0) {
      chartViews.data.labels = d.yt_trend.map(r => r.date ? r.date.slice(5) : '');
      chartViews.data.datasets[0].data = d.yt_trend.map(r => r.views_30d || 0);
      chartViews.update();

      chartSubs.data.labels = d.yt_trend.map(r => r.date ? r.date.slice(5) : '');
      chartSubs.data.datasets[0].data = d.yt_trend.map(r => r.subscribers || 0);
      chartSubs.update();
    }

    // Video Table
    const tbody = document.getElementById('video-table');
    tbody.innerHTML = '';
    (d.videos || []).forEach((v, i) => {
      const tr = document.createElement('tr');
      const title = (v.title || '').substring(0, 45);
      tr.innerHTML = `
        <td class="rank">${i+1}</td>
        <td class="title-col" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${title}</td>
        <td class="num">${fmt(v.views)}</td>
        <td class="num">${fmt(v.likes)}</td>
        <td class="num">${v.published_date || '—'}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch(e) {
    console.error('Fehler beim Laden:', e);
  }
}

initCharts();
loadData();
setInterval(loadData, 30000); // alle 30s aktualisieren
setInterval(updateClock, 1000);
updateClock();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(TEMPLATE)


if __name__ == "__main__":
    import webbrowser, threading
    def open_browser():
        import time; time.sleep(1)
        webbrowser.open("http://localhost:8002")
    threading.Thread(target=open_browser, daemon=True).start()
    print("Mindwave Command Center → http://localhost:8002")
    app.run(host="127.0.0.1", port=8002, debug=False)
