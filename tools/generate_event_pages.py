# tools/generate_event_pages.py

import sys
import os
import platform


# Print the current sys.path
print("Current sys.path:")
for p in sys.path:
    print(p)


# Clean up any existing 'tools' paths
sys.path = [path for path in sys.path if 'tools' not in path]

# Add the root of the project (i.e. where 'tools' is located)
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
## only one that works ##   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Print some debugging information
print(f"Python version: {platform.python_version()}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Print sys.path to verify it's correct
print("Updated sys.path:")
for p in sys.path:
    print(p)

# Now attempt to import
try:
    from tools.utils.date_utils import get_berlin_date_str
    print("Successfully imported get_berlin_date_str from tools.utils.date_utils"),
    print (get_berlin_date_str())
except ModuleNotFoundError as e:
    print(f"Error importing module: {e}")

import json
#from datetime import datetime
#from utils.date_utils import get_berlin_date_str
from tools.utils.jinja_env import get_env

from slugify import slugify
import logging

# === LOGGING SETUP ===
logger = logging.getLogger("generator")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("event_pages.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# === CONFIGURATION ===
TEMPLATE_NAME = "event_template.html"
EVENTS_DIR = "events"
JSON_SOURCE = f"sports_schedule_{get_berlin_date_str()}.json"
print(f"Using JSON source: {JSON_SOURCE}")

# === INIT JINJA2 ENVIRONMENT ===
env = get_env()
env.filters["slugify"] = slugify
template = env.get_template(TEMPLATE_NAME)
print(f"Using template: {TEMPLATE_NAME}")

# === CREATE OUTPUT DIR ===
os.makedirs(EVENTS_DIR, exist_ok=True)

# === LOAD EVENT DATA ===
try:
    with open(JSON_SOURCE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        events = raw.get("events", [])
except Exception as e:
    logger.error(f"❌ Fehler beim Laden von {JSON_SOURCE}: {e}")
    events = []

# === PAGE GENERATION FUNCTION ===
def generate_event_page(event):
    slug = event.get("slug") or slugify(event.get("title", "event"))
    filename = f"{slug}.html"
    output_path = os.path.join(EVENTS_DIR, filename)

    logger.info(f"Generating page for event: {event.get('title', 'Unknown')}")
    
    #Sicherstellen, dass alle erforderlichen Felder im JSON vorhanden sind
    event.setdefault("sender_slug", slugify(event.get("sender", "")))
    event.setdefault("sport_slug", slugify(event.get("sport", "")))
    for related in event.get("related_events", []):
        related.setdefault("slug", slugify(related.get("title", "")))


    # Prepare the context for rendering
    html = template.render(
        title=event.get("title", ""),
        subtitle=event.get("subtitle", ""),
        time=event.get("time", ""),
        iso_time=event.get("iso_time", ""),
        sender=event.get("sender", ""),
        sender_slug=event.get("sender_slug", ""),
        sport=event.get("sport", ""),
        sport_slug=event.get("sport_slug", ""),
        link=event.get("link", "#"),
        slug=slug,
        related_events=event.get("related_events", [])
    )


    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"✅ Generiert: {filename}")
        logger.info(f"Generating page for event: {event.get('title', 'Unknown')}")
        logger.info(html.link)
    except Exception as e:
        logger.error(f"❌ Fehler beim Schreiben von {filename}: {e}")

# === GENERATE ALL EVENT PAGES ===
logger.info(f"📦 Starte Generierung für {len(events)} Events …")
for event in events:
    generate_event_page(event)
logger.info("🏁 Alle Eventseiten erfolgreich verarbeitet.")
