"""Create path context to use src modules into notebooks."""

import os
import sys

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

print("OK NOT")

if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)
