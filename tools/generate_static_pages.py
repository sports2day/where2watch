# tools/generate_static_pages.py
import os
import json
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
from datetime import datetime

# === CONFIG ===
TEMPLATE_PATH = "tools/templates/static_html_pages_template.html"
OUTPUT_DIR = "pages"  # Hier Ausgabeordner geändert
INPUT_JSON = "sports_schedule_2025-07-17.json" #"sports_schedule_{}.json".format(datetime.today().strftime("%Y-%m-%d"))

# === Load Events ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)
    events = data.get("events", [])

# === Grouping by sport and sender ===
sports = {}
senders = {}
for event in events:
    sport = slugify(event.get("sport", "Unbekannt"))
    sender = slugify(event.get("sender", "Unbekannt"))
    sports.setdefault(sport, []).append(event)
    senders.setdefault(sender, []).append(event)

# === Jinja2 Environment ===
env = Environment(loader=FileSystemLoader("tools/templates"))
template = env.get_template("static_html_pages_template.html")

# === Create output directory if not exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Page Generator Function ===
def generate_page(filename, title, description, heading, subheading, filtered_events):
    html = template.render(
        page_title=title,
        meta_description=description,
        heading=heading,
        subheading=subheading,
        events=filtered_events,
        slug=filename.replace(".html", "")
    )
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated: {filename}")

# === Generate sport pages ===
for sport_slug, sport_events in sports.items():
    title = f"{sport_events[0]['sport']} heute im TV"
    description = f"Alle {sport_events[0]['sport']}-Events heute im Fernsehen und Stream. Jetzt entdecken."
    heading = f"{sport_events[0]['sport']} heute im TV"
    subheading = f"Live-Übertragungen aus dem Bereich {sport_events[0]['sport']}"
    filename = f"{sport_slug}.html"
    generate_page(filename, title, description, heading, subheading, sport_events)

