"""
Jarvis-Aktionen — was Jarvis auf Zuruf wirklich TUN kann.
"""

import os
import sys
import subprocess
import threading
import requests
from datetime import datetime
from config import BASE_DIR

RUN_PY = os.path.join(BASE_DIR, "scripts", "jarvis", "run.py")
ANALYSE_PY = os.path.join(BASE_DIR, "scripts", "intelligenz", "analyse.py")

_state = {"running": False, "started": None, "count": 0, "last_result": None}
_analyse_state = {"running": False, "last_result": None}


# ── Content-Pipeline ──────────────────────────────────────────────────────────

def run_pipeline(anzahl: int = 1) -> str:
    if _state["running"]:
        return f"Es läuft bereits eine Produktion (seit {_state['started']}). Ich starte keine zweite parallel."
    anzahl = max(1, min(int(anzahl or 1), 4))

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
    return (f"Produktion von {anzahl} Video(s) gestartet. Läuft im Hintergrund und wird automatisch "
            "auf YouTube und Instagram gepostet. Frag mich nach dem Status, wenn du wissen willst wie es läuft.")


def pipeline_status() -> str:
    if _state["running"]:
        return f"Gerade läuft eine Produktion von {_state['count']} Video(s), gestartet um {_state['started']} Uhr."
    if _state["last_result"]:
        return f"Im Moment läuft nichts. Die letzte Produktion wurde {_state['last_result']}."
    return "Im Moment läuft keine Produktion."


def analyse_starten() -> str:
    if _analyse_state["running"]:
        return "Eine Analyse läuft bereits."

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
    return "Ich analysiere gerade deine Videos auf YouTube und Instagram. Dauert etwa eine Minute."


# ── Wetter ────────────────────────────────────────────────────────────────────

def wetter_abrufen(ort: str = "Köln") -> str:
    """Aktuelles Wetter für einen Ort abrufen (Open-Meteo, kein API-Key nötig)."""
    try:
        # Schritt 1: Koordinaten per Geocoding holen
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ort, "count": 1, "language": "de"},
            timeout=10
        ).json()
        if not geo.get("results"):
            return f"Ort '{ort}' nicht gefunden."
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city = loc.get("name", ort)
        country = loc.get("country", "")

        # Schritt 2: Wetterdaten holen
        w = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
                "timezone": "Europe/Berlin",
                "forecast_days": 1,
            },
            timeout=10
        ).json()

        curr = w["current"]
        daily = w["daily"]
        temp = curr["temperature_2m"]
        feels = curr["apparent_temperature"]
        humidity = curr["relative_humidity_2m"]
        wind = curr["wind_speed_10m"]
        code = curr["weather_code"]
        max_t = daily["temperature_2m_max"][0]
        min_t = daily["temperature_2m_min"][0]
        sunrise = daily["sunrise"][0][11:]
        sunset = daily["sunset"][0][11:]

        beschreibung = {
            0: "Klarer Himmel", 1: "Überwiegend klar", 2: "Teilweise bewölkt", 3: "Bedeckt",
            45: "Nebelig", 48: "Nebelig", 51: "Leichter Nieselregen", 53: "Nieselregen",
            61: "Leichter Regen", 63: "Regen", 65: "Starker Regen",
            71: "Leichter Schnee", 73: "Schnee", 75: "Starker Schnee",
            80: "Regenschauer", 81: "Schauer", 82: "Starke Schauer",
            95: "Gewitter", 99: "Gewitter mit Hagel",
        }.get(code, f"Code {code}")

        return (
            f"Wetter in {city}, {country}: {beschreibung}. "
            f"Aktuell {temp}°C (gefühlt {feels}°C). "
            f"Heute {min_t}°C bis {max_t}°C. "
            f"Luftfeuchtigkeit {humidity}%, Wind {wind} km/h. "
            f"Sonnenaufgang {sunrise}, Sonnenuntergang {sunset} Uhr."
        )
    except Exception as e:
        return f"Wetter für '{ort}' konnte nicht abgerufen werden: {e}"


# ── Web-Suche ─────────────────────────────────────────────────────────────────

def web_suche(anfrage: str, anzahl: int = 5) -> str:
    """Sucht im Web nach einer Anfrage und gibt die wichtigsten Ergebnisse zurück."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(anfrage, max_results=int(anzahl)))

        if not results:
            return f"Keine Suchergebnisse für '{anfrage}' gefunden."

        lines = [f"Suchergebnisse für '{anfrage}':\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")[:200]
            url = r.get("href", "")
            lines.append(f"{i}. {title}\n   {body}\n   Quelle: {url}\n")

        return "\n".join(lines)
    except Exception as e:
        return f"Web-Suche fehlgeschlagen: {e}"


# ── Webseite lesen ────────────────────────────────────────────────────────────

def webseite_lesen(url: str) -> str:
    """Liest den Inhalt einer Webseite und gibt den Text zurück."""
    try:
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Navigationsmenüs, Scripts, Styles entfernen
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Leerzeilen bereinigen
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        text = "\n".join(lines)

        # Auf 3000 Zeichen kürzen
        if len(text) > 3000:
            text = text[:3000] + "\n\n[... Text gekürzt]"

        return f"Inhalt von {url}:\n\n{text}"
    except Exception as e:
        return f"Webseite konnte nicht gelesen werden: {e}"


# ── Datum & Uhrzeit ───────────────────────────────────────────────────────────

def datum_uhrzeit() -> str:
    """Gibt aktuelles Datum und Uhrzeit zurück."""
    now = datetime.now()
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag = wochentage[now.weekday()]
    return (f"Heute ist {wochentag}, der {now.strftime('%d.%m.%Y')}. "
            f"Es ist {now.strftime('%H:%M')} Uhr.")


# ── Rechner ───────────────────────────────────────────────────────────────────

def rechner(ausdruck: str) -> str:
    """Berechnet einen mathematischen Ausdruck."""
    import re, math
    try:
        # Natürliche Sprache → Mathe: "15% von 2000" → "2000 * 0.15"
        a = ausdruck.lower()
        m = re.match(r'([\d.,]+)\s*%\s*von\s*([\d.,]+)', a)
        if m:
            pct = float(m.group(1).replace(',', '.'))
            base = float(m.group(2).replace(',', '.'))
            result = base * pct / 100
            return f"{pct}% von {base} = {result:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Wörter ersetzen
        a = a.replace('mal', '*').replace('durch', '/').replace('plus', '+').replace('minus', '-')
        a = a.replace('geteilt durch', '/').replace('multipliziert mit', '*')
        # Nur sichere Zeichen
        clean = re.sub(r'[^0-9+\-*/()., ]', '', a).replace(',', '.')
        if not clean.strip():
            return "Ich konnte den Ausdruck nicht berechnen. Bitte nochmal umformulieren."
        result = eval(clean, {"__builtins__": {}, "math": math}, {})
        return f"{ausdruck} = {result:,}".replace(",", ".")
    except Exception as e:
        return f"Rechenfehler bei '{ausdruck}': {e}"


# ── Registry ──────────────────────────────────────────────────────────────────

ACTIONS = {
    "video_pipeline_starten": run_pipeline,
    "pipeline_status": pipeline_status,
    "analyse_starten": analyse_starten,
    "wetter_abrufen": wetter_abrufen,
    "web_suche": web_suche,
    "webseite_lesen": webseite_lesen,
    "datum_uhrzeit": datum_uhrzeit,
    "rechner": rechner,
}
