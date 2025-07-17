import requests
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRAPER_CONFIG = {
    "sources": {
        "sportschau": "https://www.sportschau.de/live-und-ergebnisse/",
        "zdf": "https://www.zdf.de/live-tv",
        "eurosport": "https://netsport.eurosport.io/",
        "kicker": "https://www.kicker.de/live"
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def save_raw_response():
    url = SCRAPER_CONFIG["sources"]["sportschau"]
    logger.info(f"Fetching: {url}")
    try:
        # Send the GET request
        response = requests.get(url, headers={"User-Agent": SCRAPER_CONFIG["user_agent"]}, timeout=10)
        response.raise_for_status()  # Raises an HTTPError if the response was bad (4xx/5xx)

        # Determine content type
        content_type = response.headers.get("Content-Type", "").lower()

        # Check if it's JSON (optional, to choose appropriate file extension)
        if "json" in content_type:
            file_extension = "json"
        elif "xml" in content_type:
            file_extension = "xml"
        else:
            file_extension = "html"

        # Save the raw response content to a file
        filename = f"raw_response.{file_extension}"
        with open(filename, 'wb') as file:  # 'wb' mode to save bytes, as content could be binary
            file.write(response.content)  # Write the raw bytes

        logger.info(f"Response saved to: {filename}")

    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
    except Exception as e:
        logger.error("An error occurred: %s", e)

# Call the function to test it
save_raw_response()
