#!/usr/bin/env python3
"""
Reel — GTK4 Frontend for MakeMKV
Entry point for the application.
"""

import sys
import os

# Ensure the src/ directory is on the path so 'ui' and 'core' packages resolve
# correctly whether the script is launched from src/, the project root, or
# anywhere else (e.g. via a .desktop file or symlink).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib
from ui.main_window import MainWindow

APP_ID = "com.MLSTidbits.Reel"

class ReelApp(Adw.Application):
    def __init__(self):
        GLib.set_prgname("reel")
        GLib.set_application_name("Reel")
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        win = MainWindow(application=app)
        win.present()


def main():
    app = ReelApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
