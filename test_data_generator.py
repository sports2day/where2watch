import json
from datetime import datetime, timedelta
import random

def generate_test_data(days=7, events_per_day=5):
    for i in range(days):
        date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        events = []
        for j in range(events_per_day):
            t = f"{random.randint(0,23):02d}:{random.choice(['00','15','30','45'])}"
            events.append({"time": t, "title": f"Test Match {j+1}", "sender": random.choice(["Sportschau","ZDF","Eurosport","Kicker"])})
        fn = f"sports_schedule_{date}.json"
        with open(fn, "w", encoding="utf-8") as f:
            json.dump({"date": date, "events": events}, f, ensure_ascii=False, indent=2)
        print(f"Generated {fn}")

if __name__ == "__main__":
    generate_test_data()
