# test_import.py
try:
    from tools.utils.date_utils import get_berlin_date_str
    print("Import successful!")
except ModuleNotFoundError as e:
    print(f"Error importing module: {e}")