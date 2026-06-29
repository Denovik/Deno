#!/bin/bash
# Einmalig auf dem Server ausführen: bash scripts/jarvis/comment_responder_setup.sh

cat > /etc/systemd/system/mindwave-comments.service << 'EOF'
[Unit]
Description=Mindwave Kommentar-Responder
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/opt/mindwave
ExecStart=/opt/mindwave/venv/bin/python3 scripts/jarvis/comment_responder.py
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/mindwave-comments.timer << 'EOF'
[Unit]
Description=Mindwave Kommentar-Responder täglich 12:00 UTC

[Timer]
OnCalendar=*-*-* 12:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable mindwave-comments.timer
systemctl start mindwave-comments.timer
echo "Timer aktiviert."
