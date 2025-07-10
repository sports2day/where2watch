# scraper_sportschau.py
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
        "eurosport": "https://www.eurosport.de/watch/schedule.shtml",
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

URL = "https://www.sportschau.de/live-und-ergebnisse/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

# ===============================
# 📡 SCRAPER: Sportschau
# ===============================
def scrape_sportschau():
    url = SCRAPER_CONFIG["sources"]["sportschau"]
    logger.info(f"Scraping: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        ##response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")

        events = []
        current_sport = None

        # Loop through all <li> elements inside the gameplan
        for li in soup.select("ul.hs-filter-sport-competition > li"):
            # If it's a sport header, store the sport name
            sport_header = li.select_one("h4")
            if sport_header:
                current_sport = sport_header.text.strip()
                continue

            # If it's a match item
            if "match" in li.get("class", []):
                time = li.select_one(".match-time")
                home_team = li.select_one(".team-name-home")
                away_team = li.select_one(".team-name-away")
                link_tag = li.select_one(".match-more a")

                if time and home_team and away_team:
                    events.append({
                        "sport": current_sport or "unbekannt",
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

def scrape_eurosport():
    url = SCRAPER_CONFIG["sources"]["eurosport"]
    logger.info(f"Scraping: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        events = []
        # Assume Eurosport lists schedule in <td class="time"> and <td class="title">
        for row in soup.select("table .program-row"):
            time_el = row.select_one(".time")
            title_el = row.select_one(".title")
            if time_el and title_el:
                events.append({
                    "time": time_el.text.strip(),
                    "title": title_el.text.strip(),
                    "sender": "Eurosport"
                })
        logger.info(f"→ {len(events)} items from Eurosport")
        return events
    except Exception as e:
        logger.error(f"Error scraping Eurosport: {e}")
        return []

def scrape_kicker():
    url = SCRAPER_CONFIG["sources"]["kicker"]
    logger.info(f"Scraping: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        events = []
        # Using Live-ticker entries
        for entry in soup.select(".liveTickerEntry"):
            time_el = entry.select_one(".time")
            title_el = entry.select_one(".ticker-title")
            if time_el and title_el:
                events.append({
                    "time": time_el.text.strip(),
                    "title": title_el.text.strip(),
                    "sender": "Kicker"
                })
        logger.info(f"→ {len(events)} items from Kicker")
        return events
    except Exception as e:
        logger.error(f"Error scraping Kicker: {e}")
        return []

   
# ========== MAIN EXECUTION ==========
def main():
    logger.info("Starting full scraping process")
    all_events = []
    for scraper in (scrape_sportschau, scrape_zdf, scrape_eurosport, scrape_kicker): # type: ignore
        all_events.extend(scraper())

    today = datetime.today().strftime("%Y-%m-%d")
    output = {"date": today, "events": all_events}
    json_filename = f"sports_schedule_{today}.json"

    try:
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(all_events)} events to '{json_filename}'")
    except Exception as e:
        logger.error(f"Failed writing JSON '{json_filename}': {e}")
  

if __name__ == "__main__":
    main()
