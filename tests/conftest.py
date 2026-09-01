"""Shared pytest configuration for NGP Sovereign Synesis bounty test suites."""
import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.resolve()))


def pytest_configure(config):
    pathlib.Path("results").mkdir(exist_ok=True)


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "docker" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        if "determinism" in item.name.lower():
            item.add_marker(pytest.mark.slow)
