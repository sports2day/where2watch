import os
import json
from datetime import datetime
from pathlib import Path
from slugify import slugify

# === CONFIGURATION ===
TEMPLATE_PATH = "tools/templates/event_template.html"
EVENTS_DIR = "events"
JSON_SOURCE = f"sports_schedule_{datetime.today().strftime('%Y-%m-%d')}.json"

# === Load HTML template ===
def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

# === Save HTML file ===
def save_event_page(html, slug):
    os.makedirs(EVENTS_DIR, exist_ok=True)
    filepath = os.path.join(EVENTS_DIR, f"{slug}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

# === Main generator ===
def generate_event_pages():
    try:
        with open(JSON_SOURCE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON file not found: {JSON_SOURCE}")
        return

    template = load_template()
    events = data.get("events", [])

    for event in events:
        # Basic safety check
        if not event.get("title") or not event.get("sport"):
            continue

        slug = slugify(event["title"])  # e.g., "palmeiras-fc-porto"
        subtitle = event.get("subtitle", "")

        # Replace placeholders
        html = template
        html = html.replace("{{title}}", event["title"])
        html = html.replace("{{time}}", event["time"])
        html = html.replace("{{sport}}", event["sport"])
        html = html.replace("{{sender}}", event.get("sender", ""))
        html = html.replace("{{subtitle}}", subtitle)
        html = html.replace("{{link}}", event.get("link", ""))
        html = html.replace("{{slug}}", slug)

        save_event_page(html, slug)

    print(f"✅ Generated {len(events)} event pages in /{EVENTS_DIR}/")

if __name__ == "__main__":
    generate_event_pages()
