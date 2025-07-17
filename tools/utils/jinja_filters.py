# tools/utils/jinja_filters.py
from datetime import datetime

def format_time(value):
    """
    Konvertiert ISO-Zeit (z. B. 2027-06-04T14:05:00+02:00)
    → in Uhrzeitformat HH:MM
    """
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%H:%M")
    except Exception:
        return value

def format_datetime(value):
    """
    Konvertiert ISO-Zeit in formatierte Anzeige:
    → z. B. Donnerstag · 14:05 Uhr
    """
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%A · %H:%M Uhr")
    except Exception:
        return value
