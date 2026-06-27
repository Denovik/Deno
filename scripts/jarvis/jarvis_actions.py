"""
Jarvis-Aktionen — was Jarvis auf Zuruf wirklich TUN kann.
Bewusst auf sichere, definierte Business-Aktionen begrenzt (kein freier Terminal-Zugriff).
"""

import os
import sys
import subprocess
import threading
from datetime import datetime
from config import BASE_DIR

RUN_PY = os.path.join(BASE_DIR, "scripts", "jarvis", "run.py")
ANALYSE_PY = os.path.join(BASE_DIR, "scripts", "intelligenz", "analyse.py")

_state = {"running": False, "started": None, "count": 0, "last_result": None}


def run_pipeline(anzahl: int = 1) -> str:
    """Startet die Content-Pipeline (Video erstellen + auf YouTube/Instagram posten) im Hintergrund."""
    if _state["running"]:
        return f"Es läuft bereits eine Produktion (seit {_state['started']}). Ich starte keine zweite parallel."

    anzahl = max(1, min(int(anzahl or 1), 4))   # Sicherheitsgrenze: 1-4

    def worker():
        _state.update(running=True, started=datetime.now().strftime("%H:%M"), count=anzahl, last_result=None)
        try:
            r = subprocess.run(
                [sys.executable, RUN_PY, "--once", "--count", str(anzahl)],
                cwd=BASE_DIR, capture_output=True, text=True, timeout=2400,
            )
            _state["last_result"] = "erfolgreich abgeschlossen" if r.returncode == 0 else "mit einem Fehler beendet"
        except Exception as e:
            _state["last_result"] = f"abgebrochen ({e})"
        finally:
            _state["running"] = False

    threading.Thread(target=worker, daemon=True).start()
    return (f"Ich habe die Produktion von {anzahl} Video(s) gestartet. "
            "Das läuft jetzt im Hintergrund und wird automatisch auf YouTube und Instagram gepostet. "
            "Das dauert ein paar Minuten — du kannst mich nach dem Status fragen.")


def pipeline_status() -> str:
    """Gibt Auskunft, ob eine Produktion läuft und wie die letzte ausging."""
    if _state["running"]:
        return f"Gerade läuft eine Produktion von {_state['count']} Video(s), gestartet um {_state['started']} Uhr."
    if _state["last_result"]:
        return f"Im Moment läuft nichts. Die letzte Produktion wurde {_state['last_result']}."
    return "Im Moment läuft keine Produktion. Sag einfach Bescheid, wenn ich welche starten soll."


_analyse_state = {"running": False, "last_result": None}


def analyse_starten() -> str:
    """Analysiert die Content-Performance auf YouTube und Instagram (läuft im Hintergrund)."""
    if _analyse_state["running"]:
        return "Eine Analyse läuft bereits. Ich melde mich, wenn sie fertig ist."

    def worker():
        _analyse_state.update(running=True, last_result=None)
        try:
            r = subprocess.run(
                [sys.executable, ANALYSE_PY],
                cwd=BASE_DIR, capture_output=True, text=True, timeout=300,
            )
            _analyse_state["last_result"] = "fertig" if r.returncode == 0 else "fehlgeschlagen"
        except Exception as e:
            _analyse_state["last_result"] = f"abgebrochen ({e})"
        finally:
            _analyse_state["running"] = False

    threading.Thread(target=worker, daemon=True).start()
    return ("Ich analysiere gerade deine Videos auf YouTube und Instagram. "
            "Das dauert etwa eine Minute. Du findest den Bericht danach in outputs/berichte/ "
            "und die Kurzfassung in deinem Kontext.")


# Registry: Name → Funktion (wird vom Gehirn aufgerufen)
ACTIONS = {
    "video_pipeline_starten": run_pipeline,
    "pipeline_status": pipeline_status,
    "analyse_starten": analyse_starten,
}
