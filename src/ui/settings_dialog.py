"""
SettingsDialog — Preferences dialog.
Static structure (all 6 pages, groups, rows, labels) loaded from
data/ui/settings_dialog.ui via Gtk.Builder.
Python owns only dynamic behaviour: loading values into widgets,
saving/reloading, browse buttons, dest-sensitivity logic.

Writes to:
  • ~/.MakeMKV/settings.conf          (native MakeMKV keys)
  • ~/.config/makemkv-gui/settings.json  (GUI-only prefs)
"""

import gi
import os
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from core.makemkv_config import MakeMKVConfig

_UI_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "ui", "settings_dialog.ui",
)

GUI_CONFIG_PATH = os.path.expanduser("~/.config/makemkv-gui/settings.json")

# ── app_DestinationType ──────────────────────────────────────────────── #
# 0=None, missing=Auto, 2=Semi-Auto, 3=Custom
# Combo index:  0→None(0)  1→Auto(missing)  2→Semi-Auto(2)  3→Custom(3)
DEST_TYPE_OPTIONS = ["None", "Auto", "Semi-Auto", "Custom"]

def _dest_type_to_index(raw) -> int:
    if raw is None:
        return 1                          # key absent → Auto
    return {0: 0, 2: 2, 3: 3}.get(int(raw), 1)

def _index_to_dest_type(idx: int):
    return {0: 0, 1: None, 2: 2, 3: 3}.get(idx, None)

def _dest_enables_path(idx: int) -> bool:
    return idx in (2, 3)                  # Semi-Auto and Custom only

# ── app_DefaultProfileName ──────────────────────────────────────────── #
# key absent = Default (MakeMKV built-in), otherwise the profile name string
PROFILE_LABELS = ["Default", "AAC-stereo", "FLAC", "WDTV"]
PROFILE_VALUES = [None,      "AAC-stereo", "FLAC", "WDTV"]

def _profile_to_index(raw) -> int:
    if not raw:
        return 0   # absent / empty → Default
    try:
        return PROFILE_VALUES.index(raw)
    except ValueError:
        return 0

def _index_to_profile(idx: int):
    return PROFILE_VALUES[idx] if 0 <= idx < len(PROFILE_VALUES) else None

# ── dvd_SPRemoveMethod ───────────────────────────────────────────────── #
SP_REMOVE_OPTIONS = ["Auto", "CellWalk", "CellTrim", "CellFull"]

# ── io_RBufSizeMB ────────────────────────────────────────────────────── #
RBUF_LABELS  = ["Auto", "64 MB", "256 MB", "512 MB", "786 MB", "1024 MB"]
RBUF_VALUES  = [None,   64,      256,       512,      786,      1024]

def _rbuf_to_index(raw) -> int:
    if raw is None:
        return 0
    try:
        v = int(raw)
        return RBUF_VALUES.index(v)
    except (ValueError, TypeError):
        return 0

def _index_to_rbuf(idx: int):
    return RBUF_VALUES[idx] if 0 <= idx < len(RBUF_VALUES) else None

# ── GUI JSON helpers ─────────────────────────────────────────────────── #

def _load_gui() -> dict:
    try:
        with open(GUI_CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def _save_gui(data: dict):
    os.makedirs(os.path.dirname(GUI_CONFIG_PATH), exist_ok=True)
    with open(GUI_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ── Dialog ───────────────────────────────────────────────────────────── #

class SettingsDialog(Adw.PreferencesDialog):
    """
    Multi-page preferences dialog.
    All page/group/row structure lives in settings_dialog.ui.
    This class: loads values into widgets, wires save/reload, file browsers.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Preferences")
        self.set_search_enabled(True)

        self._mkv = MakeMKVConfig()
        self._gui = _load_gui()

        self._load_ui()
        self._build_general_page()
        self._build_output_page()
        self._build_dvd_page()
        self._build_io_page()
        self._build_tools_page()
        self._build_app_page()

    # ------------------------------------------------------------------ #
    #  Load XML                                                            #
    # ------------------------------------------------------------------ #

    def _load_ui(self):
        b = Gtk.Builder()
        b.add_from_file(_UI_FILE)
        self._b = b                       # keep reference so objects stay alive

        # ── General ──
        self._key_row       = b.get_object("key_row")
        self._iface_lang_row = b.get_object("iface_lang_row")
        self._pref_lang_row  = b.get_object("pref_lang_row")
        self._proxy_row      = b.get_object("proxy_row")
        self._expert_row     = b.get_object("expert_row")
        self._profile_row    = b.get_object("profile_row")

        # ── Output ──
        self._dest_dir_row       = b.get_object("dest_dir_row")
        self._dest_type_row      = b.get_object("dest_type_row")
        self._backup_decrypt_row = b.get_object("backup_decrypt_row")
        self._use_title_row      = b.get_object("use_title_row")

        # ── DVD ──
        self._min_length_row = b.get_object("min_length_row")
        self._sp_remove_row  = b.get_object("sp_remove_row")

        # ── I/O ──
        self._retry_row   = b.get_object("retry_row")
        self._rbuf_row    = b.get_object("rbuf_row")
        self._sdf_stop_row = b.get_object("sdf_stop_row")

        # ── Tools ──
        self._ccextractor_row = b.get_object("ccextractor_row")
        self._java_row        = b.get_object("java_row")

        # ── App ──
        self._binary_row   = b.get_object("binary_row")
        self._auto_rip_row = b.get_object("auto_rip_row")
        self._eject_row    = b.get_object("eject_row")
        self._notify_row   = b.get_object("notify_row")
        self._action_group = b.get_object("action_group")

        # Pages (add to dialog in build methods)
        self._page_general = b.get_object("page_general")
        self._page_output  = b.get_object("page_output")
        self._page_dvd     = b.get_object("page_dvd")
        self._page_io      = b.get_object("page_io")
        self._page_tools   = b.get_object("page_tools")
        self._page_app     = b.get_object("page_app")

    # ------------------------------------------------------------------ #
    #  Page builders — populate widgets, wire signals, add to dialog      #
    # ------------------------------------------------------------------ #

    def _build_general_page(self):
        # Config-file status row injected dynamically (path isn't static)
        conf_exists = os.path.isfile(self._mkv.path)
        info_group = self._b.get_object("licence_group")   # reuse first group as anchor

        status_row = Adw.ActionRow(
            title="settings.conf",
            subtitle=(
                "Present — click Save to write changes"
                if conf_exists else "Not found — defaults shown"
            ),
        )
        status_row.add_prefix(Gtk.Image.new_from_icon_name(
            "emblem-ok-symbolic" if conf_exists else "dialog-warning-symbolic"
        ))
        # Insert before licence_group by adding a dedicated info_group at the top
        info_grp = Adw.PreferencesGroup(
            title="Configuration File",
            description=self._mkv.path
            + ("" if conf_exists else "  (will be created on first save)"),
        )
        info_grp.add(status_row)
        self._page_general.add(info_grp)
        # Move licence_group in — GTK adds in order; info_grp already appended first

        # Populate values — AFTER add() so EntryRow is fully realised
        self._key_row.set_text(self._mkv.get_str("app_Key", ""))
        self._iface_lang_row.set_text(self._mkv.get_str("app_InterfaceLanguage", "en"))
        self._pref_lang_row.set_text(self._mkv.get_str("app_PreferredLanguage", "eng"))
        self._proxy_row.set_text(self._mkv.get_str("app_Proxy", ""))
        self._expert_row.set_active(self._mkv.get_bool("app_ExpertMode", False))

        # Profile combo — visible only when Expert Mode is on
        profile_model = Gtk.StringList()
        for opt in PROFILE_LABELS:
            profile_model.append(opt)
        self._profile_row.set_model(profile_model)
        self._profile_row.set_selected(
            _profile_to_index(self._mkv.get_str("app_DefaultProfileName", ""))
        )
        self._update_profile_visibility(self._expert_row.get_active())
        self._expert_row.connect(
            "notify::active",
            lambda w, _: self._update_profile_visibility(w.get_active()),
        )

        self.add(self._page_general)

    def _build_output_page(self):
        # Destination type combo needs a model
        dest_model = Gtk.StringList()
        for opt in DEST_TYPE_OPTIONS:
            dest_model.append(opt)
        self._dest_type_row.set_model(dest_model)

        # Folder-browse button suffix on dest_dir_row
        self._dest_dir_row.add_suffix(self._folder_btn(self._dest_dir_row))

        # Populate values
        self._dest_dir_row.set_text(
            self._mkv.get_str("app_DestinationDir")
            or self._gui.get("rip_destination", os.path.expanduser("~/Videos/Rips"))
        )
        self._dest_type_row.set_selected(
            _dest_type_to_index(self._mkv.get("app_DestinationType"))
        )
        self._update_dest_sensitivity(self._dest_type_row.get_selected())
        self._dest_type_row.connect(
            "notify::selected",
            lambda w, _: self._update_dest_sensitivity(w.get_selected()),
        )
        self._backup_decrypt_row.set_active(
            self._mkv.get_bool("app_BackupDecrypted", True)
        )
        self._use_title_row.set_active(self._gui.get("use_title_name", True))

        self.add(self._page_output)

    def _build_dvd_page(self):
        # SP remove combo model
        sp_model = Gtk.StringList()
        for opt in SP_REMOVE_OPTIONS:
            sp_model.append(opt)
        self._sp_remove_row.set_model(sp_model)

        # Populate values — SpinRow: set_value AFTER page is added
        self.add(self._page_dvd)
        self._min_length_row.set_value(
            float(self._mkv.get_int("dvd_MinimumTitleLength", 120))
        )
        self._sp_remove_row.set_selected(self._mkv.get_int("dvd_SPRemoveMethod", 0))

    def _build_io_page(self):
        # Read-buffer combo model
        rbuf_model = Gtk.StringList()
        for opt in RBUF_LABELS:
            rbuf_model.append(opt)
        self._rbuf_row.set_model(rbuf_model)

        # Populate values — SpinRow: set_value AFTER page is added
        self.add(self._page_io)
        self._retry_row.set_value(float(self._mkv.get_int("io_ErrorRetryCount", 4)))
        self._rbuf_row.set_selected(_rbuf_to_index(self._mkv.get("io_RBufSizeMB")))
        self._sdf_stop_row.set_active(self._mkv.get_bool("sdf_Stop", False))

    def _build_tools_page(self):
        # File-browse button suffixes
        self._ccextractor_row.add_suffix(self._file_btn(self._ccextractor_row))
        self._java_row.add_suffix(self._file_btn(self._java_row))

        # Populate values — AFTER add() so EntryRow is realised
        self.add(self._page_tools)
        self._ccextractor_row.set_text(self._mkv.get_str("app_ccextractor", ""))
        self._java_row.set_text(self._mkv.get_str("app_Java", ""))

    def _build_app_page(self):
        # Save / Reload button box (purely dynamic — content isn't static text)
        btn_box = Gtk.Box(
            spacing=12, halign=Gtk.Align.CENTER,
            margin_top=12, margin_bottom=4,
        )
        save_btn = Gtk.Button(
            label="Save All Settings",
            css_classes=["suggested-action", "pill"],
        )
        save_btn.connect("clicked", self._on_save)
        btn_box.append(save_btn)

        reload_btn = Gtk.Button(label="Reload from Disk", css_classes=["pill"])
        reload_btn.connect("clicked", self._on_reload)
        btn_box.append(reload_btn)

        self._action_group.add(btn_box)

        # Populate values — AFTER add() so EntryRow is realised
        self.add(self._page_app)
        self._binary_row.set_text(self._gui.get("binary_path", "makemkvcon"))
        self._auto_rip_row.set_active(self._gui.get("auto_rip", False))
        self._eject_row.set_active(self._gui.get("eject_after_rip", True))
        self._notify_row.set_active(self._gui.get("notifications", True))

    # ------------------------------------------------------------------ #
    #  Helper widgets                                                      #
    # ------------------------------------------------------------------ #

    def _update_profile_visibility(self, expert_on: bool):
        """Show/hide the profile combo row based on Expert Mode toggle."""
        self._profile_row.set_visible(expert_on)

    def _update_dest_sensitivity(self, idx: int):
        self._dest_dir_row.set_sensitive(_dest_enables_path(idx))

    def _folder_btn(self, row: Adw.EntryRow) -> Gtk.Button:
        btn = Gtk.Button(
            icon_name="folder-open-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
        )
        btn.connect("clicked", lambda _: self._browse_folder(row))
        return btn

    def _file_btn(self, row: Adw.EntryRow) -> Gtk.Button:
        btn = Gtk.Button(
            icon_name="document-open-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
        )
        btn.connect("clicked", lambda _: self._browse_file(row))
        return btn

    def _parent_window(self):
        root = self.get_root()
        return root if isinstance(root, Gtk.Window) else None

    def _browse_folder(self, row: Adw.EntryRow):
        Gtk.FileDialog(title="Choose Folder").select_folder(
            parent=self._parent_window(), cancellable=None,
            callback=lambda d, r: self._finish_folder(d, r, row),
        )

    def _finish_folder(self, dialog, result, row):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                row.set_text(folder.get_path())
        except Exception:
            pass

    def _browse_file(self, row: Adw.EntryRow):
        Gtk.FileDialog(title="Choose File").open(
            parent=self._parent_window(), cancellable=None,
            callback=lambda d, r: self._finish_file(d, r, row),
        )

    def _finish_file(self, dialog, result, row):
        try:
            f = dialog.open_finish(result)
            if f:
                row.set_text(f.get_path())
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  Save / Reload                                                       #
    # ------------------------------------------------------------------ #

    def _on_save(self, _btn):
        # ── settings.conf ──
        self._mkv.set_str("app_Key",               self._key_row.get_text())
        self._mkv.set_str("app_InterfaceLanguage", self._iface_lang_row.get_text())
        self._mkv.set_str("app_PreferredLanguage", self._pref_lang_row.get_text())
        self._mkv.set_str("app_Proxy",             self._proxy_row.get_text())
        self._mkv.set_bool("app_ExpertMode",        self._expert_row.get_active())
        profile_val = _index_to_profile(self._profile_row.get_selected())
        if profile_val:
            self._mkv.set_str("app_DefaultProfileName", profile_val)
        else:
            self._mkv.remove("app_DefaultProfileName")   # absent = Default
        self._mkv.set_str("app_DestinationDir",    self._dest_dir_row.get_text())

        dt_val = _index_to_dest_type(self._dest_type_row.get_selected())
        if dt_val is None:
            self._mkv.remove("app_DestinationType")
        else:
            self._mkv.set_int("app_DestinationType", dt_val)

        self._mkv.set_bool("app_BackupDecrypted",   self._backup_decrypt_row.get_active())
        self._mkv.set_int("dvd_MinimumTitleLength", int(self._min_length_row.get_value()))
        self._mkv.set_int("dvd_SPRemoveMethod",     self._sp_remove_row.get_selected())
        self._mkv.set_int("io_ErrorRetryCount",     int(self._retry_row.get_value()))

        rbuf_val = _index_to_rbuf(self._rbuf_row.get_selected())
        if rbuf_val is None:
            self._mkv.remove("io_RBufSizeMB")
        else:
            self._mkv.set_int("io_RBufSizeMB", rbuf_val)

        self._mkv.set_bool("sdf_Stop",       self._sdf_stop_row.get_active())
        self._mkv.set_str("app_ccextractor", self._ccextractor_row.get_text())
        self._mkv.set_str("app_Java",        self._java_row.get_text())
        self._mkv.save()

        # ── GUI JSON ──
        self._gui.update({
            "binary_path":     self._binary_row.get_text(),
            "auto_rip":        self._auto_rip_row.get_active(),
            "eject_after_rip": self._eject_row.get_active(),
            "notifications":   self._notify_row.get_active(),
            "rip_destination": self._dest_dir_row.get_text(),
            "use_title_name":  self._use_title_row.get_active(),
        })
        _save_gui(self._gui)
        self.close()

    def _on_reload(self, _btn):
        self._mkv.load()
        self._gui = _load_gui()

        self._key_row.set_text(self._mkv.get_str("app_Key", ""))
        self._iface_lang_row.set_text(self._mkv.get_str("app_InterfaceLanguage", "en"))
        self._pref_lang_row.set_text(self._mkv.get_str("app_PreferredLanguage", "eng"))
        self._proxy_row.set_text(self._mkv.get_str("app_Proxy", ""))
        self._expert_row.set_active(self._mkv.get_bool("app_ExpertMode", False))
        self._profile_row.set_selected(
            _profile_to_index(self._mkv.get_str("app_DefaultProfileName", ""))
        )
        self._update_profile_visibility(self._expert_row.get_active())

        self._dest_dir_row.set_text(
            self._mkv.get_str("app_DestinationDir")
            or self._gui.get("rip_destination", os.path.expanduser("~/Videos/Rips"))
        )
        raw_type = self._mkv.get("app_DestinationType")
        self._dest_type_row.set_selected(_dest_type_to_index(raw_type))
        self._update_dest_sensitivity(self._dest_type_row.get_selected())
        self._backup_decrypt_row.set_active(self._mkv.get_bool("app_BackupDecrypted", True))
        self._use_title_row.set_active(self._gui.get("use_title_name", True))

        self._min_length_row.set_value(
            float(self._mkv.get_int("dvd_MinimumTitleLength", 120))
        )
        self._sp_remove_row.set_selected(self._mkv.get_int("dvd_SPRemoveMethod", 0))

        self._retry_row.set_value(float(self._mkv.get_int("io_ErrorRetryCount", 4)))
        self._rbuf_row.set_selected(_rbuf_to_index(self._mkv.get("io_RBufSizeMB")))
        self._sdf_stop_row.set_active(self._mkv.get_bool("sdf_Stop", False))

        self._ccextractor_row.set_text(self._mkv.get_str("app_ccextractor", ""))
        self._java_row.set_text(self._mkv.get_str("app_Java", ""))

        self._binary_row.set_text(self._gui.get("binary_path", "makemkvcon"))
        self._auto_rip_row.set_active(self._gui.get("auto_rip", False))
        self._eject_row.set_active(self._gui.get("eject_after_rip", True))
        self._notify_row.set_active(self._gui.get("notifications", True))
