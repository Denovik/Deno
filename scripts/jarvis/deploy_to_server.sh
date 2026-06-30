#!/bin/bash
# Synct Jarvis-Pipeline-Code auf den Hetzner-Server. Secrets NICHT enthalten — die werden separat per scp übertragen (siehe reference/server-deployment.md).
set -e

SSH_KEY="$HOME/.ssh/mindwave_hetzner"
SERVER="root@167.233.95.3"
REMOTE_DIR="/opt/mindwave/jarvis"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

ssh -i "$SSH_KEY" "$SERVER" "mkdir -p $REMOTE_DIR/scripts $REMOTE_DIR/context $REMOTE_DIR/data $REMOTE_DIR/music $REMOTE_DIR/outputs/logs $REMOTE_DIR/outputs/scripts $REMOTE_DIR/outputs/videos $REMOTE_DIR/outputs/berichte"

rsync -avz --progress -e "ssh -i $SSH_KEY" \
  --exclude 'venv/' \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude 'credentials/' \
  --exclude 'outputs/videos/*.mp4' \
  --exclude '__pycache__/' \
  "$LOCAL_DIR/scripts/jarvis/" "$SERVER:$REMOTE_DIR/scripts/jarvis/"

rsync -avz --progress -e "ssh -i $SSH_KEY" "$LOCAL_DIR/scripts/daten/" "$SERVER:$REMOTE_DIR/scripts/daten/"
rsync -avz --progress -e "ssh -i $SSH_KEY" "$LOCAL_DIR/scripts/intelligenz/" "$SERVER:$REMOTE_DIR/scripts/intelligenz/"
rsync -avz --progress -e "ssh -i $SSH_KEY" "$LOCAL_DIR/context/" "$SERVER:$REMOTE_DIR/context/"

if [ -d "$LOCAL_DIR/music" ]; then
  rsync -avz --progress -e "ssh -i $SSH_KEY" "$LOCAL_DIR/music/" "$SERVER:$REMOTE_DIR/music/"
else
  echo "Lokaler music/-Ordner nicht gefunden — Hintergrundmusik wird übersprungen"
fi

if [ -f "$LOCAL_DIR/data/data.db" ]; then
  rsync -avz --progress -e "ssh -i $SSH_KEY" "$LOCAL_DIR/data/data.db" "$SERVER:$REMOTE_DIR/data/data.db"
else
  echo "data.db noch nicht vorhanden, wird beim ersten Lauf auf dem Server erzeugt"
fi

echo ""
echo "Code-Sync fertig. Secrets (.env, credentials/) separat per scp übertragen — siehe reference/server-deployment.md."
