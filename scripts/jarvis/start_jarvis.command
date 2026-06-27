#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Jarvis Web-Interface — Doppelklick-Starter
# Startet den Server und öffnet Jarvis im Browser.
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="/Users/dennisgluck/Desktop/CLAUDE/ceogpt-start"
cd "$PROJECT_DIR" || exit 1

source "$PROJECT_DIR/venv/bin/activate"

# Browser kurz verzögert öffnen, damit der Server bereit ist
( sleep 4 && open "http://localhost:5005" ) &

echo "Starte JARVIS ... (dieses Fenster offen lassen, zum Beenden Strg+C)"
python3 "$PROJECT_DIR/scripts/jarvis/web_app.py"
