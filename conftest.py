import platform
import sys

from pytest_metadata.plugin import metadata_key


def pytest_configure(config):
    config.stash[metadata_key]["Python"] = sys.version
    config.stash[metadata_key]["Platform"] = platform.platform()
    config.stash[metadata_key]["Architecture"] = platform.machine()