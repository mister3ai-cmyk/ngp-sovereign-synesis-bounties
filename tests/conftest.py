"""Shared pytest configuration for NGP Sovereign Synesis bounty test suites."""
import pathlib
import sys
import pytest

# Ensure workspace root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def pytest_configure(config):
    pathlib.Path("results").mkdir(exist_ok=True)
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "docker" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        if "determinism" in item.name.lower():
            item.add_marker(pytest.mark.slow)
