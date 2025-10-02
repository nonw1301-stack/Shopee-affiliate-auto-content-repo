import os
import sys


def pytest_configure():
    # Add the project root (one level up from tests/) to sys.path so tests can import src
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root not in sys.path:
        sys.path.insert(0, root)
