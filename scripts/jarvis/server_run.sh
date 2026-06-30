#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Jarvis Täglicher Auto-Lauf — Server-Version
# Wird vom Server-Cron aufgerufen (siehe reference/server-deployment.md)
# Produziert und postet 2 Videos, schreibt ein Log mit.
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="/opt/mindwave/jarvis"
LOG_DIR="$PROJECT_DIR/outputs/logs"
mkdir -p "$LOG_DIR"

DATE=$(date "+%Y-%m-%d_%H%M")
LOG_FILE="$LOG_DIR/daily-$DATE.log"

cd "$PROJECT_DIR" || exit 1

echo "===== Jarvis Auto-Lauf gestartet: $(date) =====" >> "$LOG_FILE"

# venv aktivieren und 2 Videos produzieren/posten
source "$PROJECT_DIR/venv/bin/activate"
python3 "$PROJECT_DIR/scripts/jarvis/run.py" --once --count 1 >> "$LOG_FILE" 2>&1

echo "===== Jarvis Auto-Lauf beendet: $(date) =====" >> "$LOG_FILE"
