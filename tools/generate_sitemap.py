import os
from datetime import datetime


# --- Config: URLs for rarely changed SEO pages ---
#STATIC_SEO_PAGES = [
 #   ("impressum.html", 0.3, "yearly"),
  #  ("datenschutz.html", 0.3, "yearly"),
#]

# Directories for event pages and static pages
EVENTS_DIR = "events"       # event detail pages (e.g. croatia-vs-algeria.html)
PAGES_DIR = "pages"         # provider and sport pages (zdf.html, mountainbike.html)

# Output files
SITEMAP_FILE = "sitemap.xml"
ROBOTS_FILE = "robots.txt"

today = datetime.today().strftime("%Y-%m-%d")

def write_url_entry(f, loc, lastmod, priority, changefreq):
    """Write a single <url> entry in sitemap."""
    f.write("  <url>\n")
    f.write(f"    <loc>{loc}</loc>\n")
    f.write(f"    <lastmod>{lastmod}</lastmod>\n")
    f.write(f"    <changefreq>{changefreq}</changefreq>\n")
    f.write(f"    <priority>{priority}</priority>\n")
    f.write("  </url>\n")

def generate_sitemap(base_url):
    """Generate sitemap.xml including homepage, SEO pages and event pages."""

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

        # 1. Homepage
        write_url_entry(f, base_url + "/", today, "1.0", "daily")

        # 2. Static SEO pages with fixed priority & changefreq
        #for page, priority, changefreq in STATIC_SEO_PAGES:
         #   write_url_entry(f, f"{base_url}/{page}", today, str(priority), changefreq)
        
        #3. Event pages from PAGES_DIR (daily updated)
        if os.path.isdir(PAGES_DIR):
            for filename in sorted(os.listdir(PAGES_DIR)):
                if filename.endswith(".html"):
                    write_url_entry(f, f"{base_url}/pages/{filename}", today, "0.7", "daily")
        else:
            print(f"⚠️ Pages directory '{PAGES_DIR}' not found, skipping event URLs.")

        # 4. Event pages from EVENTS_DIR (daily updated)
        if os.path.isdir(EVENTS_DIR):
            for filename in sorted(os.listdir(EVENTS_DIR)):
                if filename.endswith(".html"):
                    write_url_entry(f, f"{base_url}/events/{filename}", today, "0.7", "daily")
        else:
            print(f"⚠️ Events directory '{EVENTS_DIR}' not found, skipping event URLs.")

        f.write("</urlset>\n")

    print(f"✅ Sitemap '{SITEMAP_FILE}' generated successfully.")

def update_robots(base_url):
    """Add sitemap URL entry to robots.txt if not already present."""
    sitemap_line = f"Sitemap: {base_url}/sitemap.xml\n"

    if os.path.exists(ROBOTS_FILE):
        with open(ROBOTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if any("Sitemap:" in line for line in lines):
            print("ℹ️ robots.txt already contains a Sitemap entry.")
            return
    else:
        lines = []

    lines.append(sitemap_line)

    with open(ROBOTS_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ robots.txt updated with Sitemap entry.")

if __name__ == "__main__":
    base_url = "https://sports2day.github.io/where2watch"
    generate_sitemap(base_url)
    update_robots(base_url)
