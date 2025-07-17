import os,sys
sys.path = [path for path in sys.path if 'tools' not in path]

# Add the root of the project (i.e. where 'tools' is located)
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
## only one that works ##   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import datetime
from slugify import slugify
from jinja2 import Environment, FileSystemLoader, select_autoescape
from tools.utils.date_utils import get_berlin_date_str

# === CONFIGURATION ===
TEMPLATE_PATH = "tools/templates/index_template.html"
OUTPUT_FILE = "index.html"
JSON_SOURCE = f"sports_schedule_{get_berlin_date_str()}.json" #"sports_schedule_2025-07-15.json" #f"sports_schedule_{datetime.today().strftime('%Y-%m-%d')}.json"
SPORT_META_PATH = "tools/config/sport_meta.json"

# === Load Jinja2 Environment ===
env = Environment(
    loader=FileSystemLoader("tools/templates"),
    autoescape=select_autoescape(["html"])
)
template = env.get_template("index_template.html")

# === Load Sport Meta (icons & colors) ===
def load_sport_meta():
    try:
        with open(SPORT_META_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"⚠️ sport_meta.json not found: {SPORT_META_PATH}")
        return {}

# === Load & Group Events ===
def load_and_group_events():
    try:
        with open(JSON_SOURCE, "r", encoding="utf-8") as f:
            events = json.load(f).get("events", [])
    except FileNotFoundError:
        print(f"❌ JSON file not found: {JSON_SOURCE}")
        return {}

    grouped = {}
    for event in events:
        sport = event.get("sport", "Unknown")
        event["slug"] = event.get("slug") or slugify(event.get("title", "event"))
        grouped.setdefault(sport, []).append(event)

    for sport in grouped:
        grouped[sport] = sorted(grouped[sport], key=lambda x: x.get("time", ""))

    return grouped

# === Main Generator ===
def generate_index():
    grouped_events = load_and_group_events()
    sport_meta = load_sport_meta()

    sport_icons = {sport: meta.get("icon") for sport, meta in sport_meta.items()}
    sport_colors = {sport: meta.get("color") for sport, meta in sport_meta.items()}

    rendered = template.render(
        grouped_events=grouped_events,
        sport_icons=sport_icons,
        sport_colors=sport_colors
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"✅ index.html generated with {sum(len(e) for e in grouped_events.values())} events")

if __name__ == "__main__":
    generate_index()
