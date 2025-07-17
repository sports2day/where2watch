from datetime import datetime
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")

def get_berlin_date_str():
    """Gibt aktuelles Datum in Berlin-Zeit zurück (YYYY-MM-DD)"""
    return datetime.now(BERLIN).strftime("%Y-%m-%d")

def get_berlin_iso():
    """Gibt ISO-Format mit Uhrzeit in Berlin-Zeit zurück"""
    return datetime.now(BERLIN).isoformat()

def berlin_iso_from_time_string(time_str: str) -> str:
    """
    Wandelt eine Uhrzeit wie '18:00' in ein ISO-Datum im Berlin-Zeitraum für das aktuelle Datum um.
    Beispiel: '18:00' → '2025-07-17T18:00:00+02:00'
    """
    try:
        today = get_berlin_date_str()  # z. B. '2025-07-17'
        dt_naive = datetime.fromisoformat(f"{today}T{time_str}:00")
        dt_berlin = dt_naive.replace(tzinfo=BERLIN)
        return dt_berlin.isoformat()
    except Exception:
        return ""
