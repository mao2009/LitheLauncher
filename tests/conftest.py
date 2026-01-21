# tests/conftest.py
import os
import sys
from pathlib import Path

# Add the 'src' directory to the Python path for pytest to discover modules
# Ensure this happens at the very beginning of the test collection phase
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# You can also add other pytest fixtures or hooks here
# For example, to ensure specific logging behavior during tests
# @pytest.fixture(autouse=True)
# def disable_logging_during_tests():
#     logging.disable(logging.CRITICAL)
#     yield
#     logging.disable(logging.NOTSET)