import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging

# ===============================
# 🛠 CONFIGURATION
# ===============================
SCRAPER_CONFIG = {
    "sources": {
        "sportschau": "https://www.sportschau.de/live-und-ergebnisse/",
        "zdf": "https://www.zdf.de/live-tv",
        "eurosport": "https://netsport.eurosport.io/",
        "kicker": "https://www.kicker.de/live"
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ===============================
# 🧾 LOGGER
# ===============================
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

# ===============================
# 📡 SCRAPER: Sportschau
# ===============================
def scrape_sportschau():
    url = SCRAPER_CONFIG["sources"]["sportschau"]
    logger.info(f"Scraping: {url}")
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

                if time and home_team and away_team:
                    events.append({
                        "sport": current_sport or "unknown",
                        "time": time.text.strip(),
                        "title": f"{home_team.text.strip()} vs {away_team.text.strip()}",
                        "sender": "Sportschau Live",
                        "link": "https://www.sportschau.de" + link_tag["href"] if link_tag else None
                    })
        logger.info(f"→ {len(events)} events from Sportschau")
        return events
    except Exception as e:
        logger.error(f"Error scraping Sportschau: {e}")
        return []

# ===============================
# 📺 SCRAPER: ZDF
# ===============================
def scrape_zdf():
    url = SCRAPER_CONFIG["sources"]["zdf"]
    logger.info(f"Scraping: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        events = []
        for box in soup.select(".zdf-channel"):
            name_el = box.select_one(".channel-name")
            prog_el = box.select_one(".current-programme")
            if name_el and prog_el:
                events.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "title": prog_el.text.strip(),
                    "sender": name_el.text.strip()
                })
        logger.info(f"→ {len(events)} events from ZDF")
        return events
    except Exception as e:
        logger.error(f"Error scraping ZDF: {e}")
        return []

# ===============================
# 🏁 SCRAPER: Eurosport (via GraphQL)
# ===============================
def scrape_eurosport():
    logger.info("Scraping Eurosport via GraphQL")
    events = []

    try:
        iso_date = datetime.today().strftime("%Y-%m-%dT22:00:00.000Z")

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

        params = {
            "variables": variables,
            "extensions": extensions
        }

        headers = {
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
        }

        response = requests.get(SCRAPER_CONFIG["sources"]["eurosport"], params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        edges = data.get("data", {}).get("programsByDate", {}).get("edges", [])
        for item in edges:
            node = item.get("node", {})
            sport = node.get("sportName", "Unknown").strip()
            title = node.get("title", "").strip()
            subtitle = node.get("subtitle", "").strip()
            time = node.get("startTime", "")[11:16]
            url = node.get("programLink", {}).get("url", "")
            # ToDo: Get legal permission from Eurosport to use images.
            """image = None
            for pf in node.get("pictureFormats", []):
                if pf.get("assetPictureFormat") == "XXL_16_9":
                    image = pf.get("url")
                    break """
            
            events.append({
                "sport": sport,
                "time": time,
                "title": title,
                "subtitle": subtitle,
                "sender": "Eurosport",
                "link": url
                #,"image": image
            })

        logger.info(f"→ {len(events)} events from Eurosport")
        return events

    except Exception as e:
        logger.error(f"Error scraping Eurosport: {e}")
        return []

# ===============================
# ⚽️ SCRAPER: Kicker
# ===============================
def scrape_kicker():
    url = SCRAPER_CONFIG["sources"]["kicker"]
    logger.info(f"Scraping: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        events = []
        for entry in soup.select(".liveTickerEntry"):
            time_el = entry.select_one(".time")
            title_el = entry.select_one(".ticker-title")
            if time_el and title_el:
                events.append({
                    "time": time_el.text.strip(),
                    "title": title_el.text.strip(),
                    "sender": "Kicker"
                })
        logger.info(f"→ {len(events)} events from Kicker")
        return events
    except Exception as e:
        logger.error(f"Error scraping Kicker: {e}")
        return []

# ===============================
# 🏁 MAIN EXECUTION
# ===============================
def main():
    logger.info("Starting full scraping process")
    all_events = []
    scrapers = [scrape_sportschau, scrape_zdf, scrape_eurosport, scrape_kicker]

    for scraper in scrapers:
        try:
            result = scraper()
            if isinstance(result, list):
                all_events.extend(result)
            else:
                logger.warning(f"{scraper.__name__} returned non-list: {type(result)}")
        except Exception as e:
            logger.error(f"Unhandled error in {scraper.__name__}: {e}")

    today = datetime.today().strftime("%Y-%m-%d")
    output = {"date": today, "events": all_events}
    filename = f"sports_schedule_{today}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(all_events)} events to '{filename}'")
    except Exception as e:
        logger.error(f"Failed writing JSON '{filename}': {e}")

if __name__ == "__main__":
    main()
