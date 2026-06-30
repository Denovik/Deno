#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Jarvis Daten-Sammlung — Server-Version
# Wird vom Server-Cron aufgerufen (siehe reference/server-deployment.md)
# Sammelt YouTube/Instagram-Kennzahlen, aktualisiert context/group/key-metrics.md
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="/opt/mindwave/jarvis"
LOG_DIR="$PROJECT_DIR/outputs/logs"
mkdir -p "$LOG_DIR"

DATE=$(date "+%Y-%m-%d_%H%M")
LOG_FILE="$LOG_DIR/daten-$DATE.log"

cd "$PROJECT_DIR" || exit 1

echo "===== Daten-Sammlung gestartet: $(date) =====" >> "$LOG_FILE"

source "$PROJECT_DIR/venv/bin/activate"
cd "$PROJECT_DIR/scripts/daten" || exit 1
python3 collect.py >> "$LOG_FILE" 2>&1

echo "===== Daten-Sammlung beendet: $(date) =====" >> "$LOG_FILE"
