# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Reel is a DVD/Blu-ray ripping GUI that wraps `makemkvcon` (MakeMKV's CLI). It ships two parallel frontends — GTK4 (`src/gtk/`) and Qt5 (`src/qt/`) — with nearly identical internal structure. The `src/reel` script is a thin launcher that puts the right lib directory on `sys.path`.

## Commands

### Build
```bash
make              # stages files into _build/
make clean        # removes _build/
```

### Install (requires build first)
```bash
sudo make install GTK_INSTALL=enable   # GTK frontend
sudo make install QT_INSTALL=enable    # Qt frontend
# Only one frontend flag at a time; specifying both is an error.
```

### Run Tests
```bash
pytest tests/                          # all tests (no GTK/Qt needed)
pytest tests/test_parser.py::test_parse_drives   # single test
```

The test suite only covers `MakeMKVParser` — it imports from `src/` directly and has no GUI dependency.

### Run (development, GTK)
```bash
cd src/gtk && python3 main.py
```
Requires `makemkvcon` on `PATH` and GTK4 + libadwaita installed.

## Architecture

```
src/
├── reel               # launcher: patches sys.path then calls main()
├── gtk/
│   ├── main.py        # Adw.Application entry point
│   ├── core/          # no GTK dependency — safe to unit-test
│   │   ├── models.py              # DriveInfo, TitleInfo, BackupJob, RipJob (dataclasses)
│   │   ├── makemkv_controller.py  # GObject that owns all subprocess calls
│   │   ├── makemkv_parser.py      # parses makemkvcon -r output
│   │   ├── makemkv_config.py      # read/write ~/.MakeMKV/settings.conf
│   │   ├── languages.py
│   │   └── version.py
│   └── ui/
│       ├── main_window.py         # AdwApplicationWindow + tab notebook
│       ├── disc_view.py           # drive picker, title list, rip controls
│       ├── backup_view.py         # full-disc backup
│       ├── log_view.py            # colour-coded makemkvcon output
│       └── settings_dialog.py    # Adw.PreferencesDialog
└── qt/                # mirrors gtk/ structure; PyQt5 equivalents
data/ui/               # GtkBuilder .ui XML — all static layout, labels, menus
tests/
```

### Signal / threading model

`MakeMKVController` is a `GObject` that runs every `makemkvcon` invocation on a daemon thread. Results are marshalled back to the GTK main loop exclusively via `GLib.idle_add()`. UI code connects to GObject signals (`drives-updated`, `titles-loaded`, `progress`, `rip-started`, `rip-finished`, `backup-finished`, `log-line`, `error`, `libre-drive`).

### UI convention

Static layout (labels, icons, tooltips, menus, about dialog) lives in `data/ui/*.ui` XML files loaded via `Gtk.Builder`. Python touches only dynamic behaviour: connecting signals, updating progress, appending log lines. No hardcoded display strings in Python.

### Config files written at runtime

| Path | Purpose |
|------|---------|
| `~/.MakeMKV/settings.conf` | Native MakeMKV settings (written by `MakeMKVConfig`) |
| `~/.config/reel/settings.json` | GUI-only prefs: `rip_destination`, `window_width`, `window_height` |

`MakeMKVConfig` must preserve MakeMKV's exact file format (quoted values, canonical key order, specific comment header) or MakeMKV itself will reject the file.

### Installed paths

The installed layout differs from the source tree:

| Source | Installed |
|--------|-----------|
| `src/gtk/` | `/usr/lib/reel/gtk/` |
| `data/ui/` | `/usr/share/reel/ui/` |

`main_window.py` and `settings_dialog.py` reference `/usr/share/reel/ui/*.ui` as hardcoded paths — these only work after `make install` or when the files are symlinked there for development.
