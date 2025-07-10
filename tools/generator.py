import json
from datetime import datetime
from jinja2 import Template

def main():
    today = datetime.today().strftime("%Y-%m-%d")
    json_filename = f"sports_schedule_{today}.json"
    with open(json_filename, encoding="utf-8") as f:
        data = json.load(f)

    with open("template.html", encoding="utf-8") as f:
        template = Template(f.read())

    output = template.render(date=data["date"], events=data["events"])

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(output)

    print("✅ HTML generiert: index.html")

if __name__ == "__main__":
    main()
