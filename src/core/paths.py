"""
paths.py — Resolve runtime data paths for both installed and development layouts.

Installed layout (after `make install` or package install):
  /usr/lib/ripper/ui/        <- src/ui/   Python modules
  /usr/lib/ripper/core/      <- src/core/ Python modules
  /usr/share/ripper/ui/      <- data/ui/  GtkBuilder XML files
  /usr/share/doc/ripper/     <- doc/      version, README, changelog, etc.

Development layout (running from source tree via run.sh):
  <project>/src/ui/
  <project>/src/core/
  <project>/data/ui/
  <project>/doc/

The resolution order for each path type:
  1. Installed system path  (/usr/share/…)
  2. Source-tree path       (<project root>/…)
"""

import os

# This file lives at /usr/lib/ripper/core/paths.py (installed)
# or <project>/src/core/paths.py (development).
# Either way: dirname(__file__) = .../core/
#             dirname(dirname(__file__)) = /usr/lib/ripper  OR  <project>/src

_HERE = os.path.dirname(os.path.abspath(__file__))   # .../core
_LIB  = os.path.dirname(_HERE)                        # /usr/lib/ripper  OR  src/

# Installed paths
_SHARE_DIR = "/usr/share/ripper"
_DOC_DIR   = "/usr/share/doc/ripper"

# Development paths (two levels up from src/core/ reaches the project root)
_PROJECT_ROOT    = os.path.dirname(_LIB)
_SOURCE_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
_SOURCE_DOC_DIR  = os.path.join(_PROJECT_ROOT, "doc")


def _resolve(installed: str, source: str) -> str:
    """Return the installed path if it exists, otherwise fall back to source."""
    return installed if os.path.exists(installed) else source


def ui_file(name: str) -> str:
    """Return the full path to a GtkBuilder UI file, e.g. ui_file("main_window.ui")."""
    return _resolve(
        os.path.join(_SHARE_DIR, "ui", name),
        os.path.join(_SOURCE_DATA_DIR, "ui", name),
    )


def doc_file(name: str) -> str:
    """
    Return the full path to a documentation/metadata file,
    e.g. doc_file("version"), doc_file("README.md"), doc_file("changelog").

    Installed: /usr/share/doc/ripper/<name>
    Source:    <project>/doc/<name>
    """
    return _resolve(
        os.path.join(_DOC_DIR, name),
        os.path.join(_SOURCE_DOC_DIR, name),
    )
