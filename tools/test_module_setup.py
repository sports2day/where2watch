# tools/test_module_setup.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools.utils.date_utils import get_berlin_date_str
from tools.utils.jinja_env import get_env
from tools.utils.jinja_filters import format_time, format_datetime
from datetime import datetime


def test_date_utils():
    print("📅 Berlin-Tagesdatum:", get_berlin_date_str())

def test_jinja_env():
    env = get_env()
    html = env.from_string("Zeit: {{ iso_time|format_time }} · {{ iso_time|format_datetime }}").render(
        iso_time=datetime.now().isoformat()
    )
    print("🧪 Jinja-Rendering:", html)

def test_filters_direct():
    now_iso = datetime.now().isoformat()
    print("⏱ Direkt format_time():", format_time(now_iso))
    print("⏱ Direkt format_datetime():", format_datetime(now_iso))

if __name__ == "__main__":
    test_date_utils()
    test_jinja_env()
    test_filters_direct()
