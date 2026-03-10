"""
Single source of truth for the application version.
Reads the version string via core.paths.data_file("version").

Installed path : /usr/share/ripper/version
Development    : <project>/doc/version
"""

from core.paths import data_file


def get_version() -> str:
    """Return the version string, e.g. '0.1.0'."""
    try:
        with open(data_file("version")) as f:
            return f.read().strip()
    except OSError:
        return "unknown"
