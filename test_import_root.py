# test_import_root.py
import sys
import os

# Print sys.path to verify
print("sys.path:")
for p in sys.path:
    print(p)

try:
    from tools.utils.date_utils import get_berlin_date_str
    print("Import successful!")
except ModuleNotFoundError as e:
    print(f"Error importing module: {e}")
