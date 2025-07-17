# tools/generate_sender_pages.py

import os
import json
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
from datetime import datetime

# === CONFIG ===
TEMPLATE_PATH = "tools/templates/sender_template.html"
OUTPUT_DIR = "pages"
INPUT_JSON = "sports_schedule_2025-07-17.json" #f"sports_schedule_{datetime.today().strftime('%Y-%m-%d')}.json"

# === Load Events ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    events = json.load(f).get("events", [])

# === Group by sender ===
senders = {}
for event in events:
    sender = slugify(event.get("sender", "Unbekannt"))
    senders.setdefault(sender, []).append(event)

# === Setup Jinja2 ===
env = Environment(loader=FileSystemLoader("tools/templates"))
template = env.get_template("sender_template.html")

# === Ensure output folder exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Generator ===
for sender_slug, sender_events in senders.items():
    title = f"{sender_events[0]['sender']} Sportprogramm heute"
    description = f"Sport live im TV auf {sender_events[0]['sender']}. Alle Übertragungen auf einen Blick."
    heading = f"{sender_events[0]['sender']} heute im Überblick"
    subheading = f"Live-Übertragungen bei {sender_events[0]['sender']}"
    filename = f"{sender_slug}.html"

    html = template.render(
        page_title=title,
        meta_description=description,
        heading=heading,
        subheading=subheading,
        events=sender_events,
        slug=sender_slug
    )

    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📡 Senderseite generiert: {filename}")
