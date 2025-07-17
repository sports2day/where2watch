# scraper.py

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from slugify import slugify
from tools.utils.date_utils import get_berlin_date_str, berlin_iso_from_time_string

# === CONFIGURATION ===
SCRAPER_CONFIG = {
    "sources": {
        "sportschau": "https://www.sportschau.de/live-und-ergebnisse/",
        "eurosport": "https://netsport.eurosport.io/"
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BERLIN = ZoneInfo("Europe/Berlin")

# === LOGGER SETUP ===
def setup_logger():
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("scraper.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

logger = setup_logger()

# === Utility for Matching   ===
def abs_time_diff(t1, t2):
    if t1 and t2:
        try:
            dt1 = datetime.fromisoformat(t1)
            dt2 = datetime.fromisoformat(t2)
            return abs(int((dt2 - dt1).total_seconds()) // 60)
        except Exception:
            pass
    return None  # Zeitvergleich nicht möglich


# === SCRAPER: Sportschau ===
def scrape_sportschau():
    url = SCRAPER_CONFIG["sources"]["sportschau"]
    logger.info(f"Scraping Sportschau: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        events = []
        current_sport = None

        for li in soup.select("ul.hs-filter-sport-competition > li"):
            sport_header = li.select_one("h4")
            if sport_header:
                current_sport = sport_header.text.strip()
                continue

            if "match" in li.get("class", []):
                time = li.select_one(".match-time")
                home_team = li.select_one(".team-name-home")
                away_team = li.select_one(".team-name-away")
                link_tag = li.select_one(".match-more a")

                title = f"{home_team.text.strip()} vs {away_team.text.strip()}" if home_team and away_team else "Unbenanntes Spiel"
                raw_time = time.text.strip() if time else ""

                sport = current_sport or "Unbekannt"
                sender = "Sportschau Live"
                today = get_berlin_date_str()  # z. B. "2025-07-17"
                parsed_iso = berlin_iso_from_time_string(raw_time)

                events.append({
                    "title": title,
                    "time": raw_time,
                    "iso_time": "",  # Sportschau liefert keine echte ISO-Zeit
                    "sport": sport,
                    "sport_slug": slugify(sport),
                    "sender": sender,
                    "sender_slug": slugify(sender),
                    "link": "https://www.sportschau.de" + link_tag["href"] if link_tag and link_tag.get("href") else None,
                    "slug": slugify(title),
                    "subtitle": "",
                    "related_events": []  # Optionale Erweiterung später
                })
        logger.info(f"→ {len(events)} Events von Sportschau")
        return events
    except Exception as e:
        logger.error(f"Fehler beim Scrapen von Sportschau: {e}")
        return []

# === SCRAPER: Eurosport ===
def scrape_eurosport():
    logger.info("Scraping Eurosport via GraphQL")
    events = []

    try:
        iso_date = get_berlin_date_str() + "T00:00:00.000Z"

        variables = json.dumps({
            "after": None,
            "date": iso_date,
            "first": 500
        }, separators=(",", ":"))

        extensions = json.dumps({
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a9fb22686737ac30083dbae4c0927a1d07056d783357d3821c9140f810656753"
            }
        }, separators=(",", ":"))

        response = requests.get(
            SCRAPER_CONFIG["sources"]["eurosport"],
            params={"variables": variables, "extensions": extensions},
            headers={
                "User-Agent": SCRAPER_CONFIG["user_agent"],
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Referer": "https://www.eurosport.de/watch/schedule.shtml",
                "Origin": "https://www.eurosport.de",
                "apollographql-client-name": "web",
                "apollographql-client-version": "0.366.0-csr-92",
                "premium-country-code": "DE",
                "x-timezone": "Europe/Berlin",
                "domain": "www.eurosport.de"
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        edges = data.get("data", {}).get("programsByDate", {}).get("edges", [])
        if not edges:
            logger.warning("Keine Events in Eurosport-Daten gefunden")
            return []

        for item in edges:
            node = item.get("node", {})
            sport = (node.get("sportName") or "Unbekannt").strip()
            title = (node.get("title") or "Ohne Titel").strip()
            subtitle = (node.get("subtitle") or "").strip()
            raw_time = node.get("startTime", "")  # UTC ISO-Zeit
            url = node.get("programLink", {}).get("url", "")

            try:
                iso_local = datetime.fromisoformat(raw_time.replace("Z", "+00:00")).astimezone(BERLIN).isoformat()
                time_str = iso_local[11:16]
            except Exception as e:
                logger.warning(f"⚠️ Fehler bei Zeitformat für '{title}': {e}")
                iso_local = ""
                time_str = ""

            events.append({
                "title": title,
                "subtitle": subtitle,
                "sport": sport,
                "sport_slug": slugify(sport),
                "sender": "Eurosport",
                "sender_slug": slugify("Eurosport"),
                "time": time_str,
                "iso_time": iso_local,
                "link": url,
                "slug": slugify(title),
                "related_events": []
            })
        logger.info(f"→ {len(events)} Events von Eurosport")
        return events

    except Exception as e:
        logger.error(f"Fehler beim Scrapen von Eurosport: {e}")
        return []

# === MAIN EXECUTION ===
def main():
    logger.info("🚀 Starte Scraping-Prozess")
    all_events = []
    scrapers = [scrape_sportschau, scrape_eurosport]

    for scraper in scrapers:
        try:
            result = scraper()
            if isinstance(result, list):
                all_events.extend(result)
            else:
                logger.warning(f"{scraper.__name__} lieferte kein list-Objekt: {type(result)}")
        except Exception as e:
            logger.error(f"Unhandled error in {scraper.__name__}: {e}")

    # === Related matching ===
# === RELATED EVENTS ZUORDNEN ===
    for base_event in all_events:
        base_sport = base_event.get("sport_slug", "")
        base_slug = base_event.get("slug", "")
        base_iso = base_event.get("iso_time", "")
        base_time = base_event.get("time", "")

        related = []

        for candidate in all_events:
            if candidate.get("slug") == base_slug:
                continue
            if candidate.get("sport_slug") != base_sport:
                continue

            time_diff = abs_time_diff(base_iso, candidate.get("iso_time", ""))
            if time_diff is None:
                is_similar = base_time and candidate.get("time") == base_time
            else:
                is_similar = time_diff <= 180

            if is_similar:
                related.append({
                    "title": candidate.get("title", ""),
                    "time": candidate.get("time", ""),
                    "sender": candidate.get("sender", ""),
                    "slug": candidate.get("slug", "")
                })

        base_event["related_events"] = related[:3]


# Ende matching #     


    today = get_berlin_date_str()
    filename = f"sports_schedule_{get_berlin_date_str()}.json" #f"sports_schedule_{today}.json"
    output = {"date": today, "events": all_events}

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ {len(all_events)} Events gespeichert in '{filename}'")
    except Exception as e:
        logger.error(f"❌ Fehler beim Schreiben der JSON-Datei: {e}")

if __name__ == "__main__":
    main()
