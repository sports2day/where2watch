# tools/utils/jinja_env.py
from jinja2 import Environment, FileSystemLoader
from tools.utils.jinja_filters import format_time, format_datetime

def get_env(template_dir="tools/templates"):
    """
    Initialisiert zentrales Jinja2-Environment mit eingebauten Filtern
    """
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["format_time"] = format_time
    env.filters["format_datetime"] = format_datetime
    return env
