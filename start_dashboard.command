#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
"$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/scripts/daten/dashboard.py"
