#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Jarvis Wöchentliche Performance-Analyse — Server-Version
# Wird vom Server-Cron aufgerufen (siehe reference/server-deployment.md)
# Analysiert Videos/Reels, schreibt Bericht nach outputs/berichte/
# ─────────────────────────────────────────────────────────────

PROJECT_DIR="/opt/mindwave/jarvis"
LOG_DIR="$PROJECT_DIR/outputs/logs"
mkdir -p "$LOG_DIR"

DATE=$(date "+%Y-%m-%d_%H%M")
LOG_FILE="$LOG_DIR/intelligenz-$DATE.log"

cd "$PROJECT_DIR" || exit 1

echo "===== Wöchentliche Analyse gestartet: $(date) =====" >> "$LOG_FILE"

source "$PROJECT_DIR/venv/bin/activate"
cd "$PROJECT_DIR/scripts/intelligenz" || exit 1
python3 analyse.py >> "$LOG_FILE" 2>&1

echo "===== Wöchentliche Analyse beendet: $(date) =====" >> "$LOG_FILE"
