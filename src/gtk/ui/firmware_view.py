"""
FirmwareView — Dump and flash optical drive firmware to enable LibreDrive.
Static structure loaded from data/ui/firmware_view.ui.
Python owns only dynamic behaviour: drive list, file selection, progress, history.
"""

import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from core.makemkv_controller import MakeMKVController
from core.models import FirmwareJob

_UI_FILE = "/usr/share/reel/ui/firmware_view.ui"


class FirmwareHistoryRow(Adw.ActionRow):
    """Displays a single completed firmware operation in the history list."""

    _STATUS_ICONS = {
        "done":    ("emblem-ok-symbolic",            ["success"]),
        "running": ("emblem-synchronizing-symbolic", ["accent"]),
        "failed":  ("dialog-error-symbolic",         ["error"]),
    }

    def __init__(self, job: FirmwareJob):
        op_label = "Dump" if job.operation == "dump" else "Flash"
        super().__init__(
            title=f"{op_label} — {os.path.basename(job.bin_path)}",
            subtitle=f"{job.bin_path}  ·  {job.timestamp}",
        )
        self.job = job
        icon_name, css = self._STATUS_ICONS.get(job.status, ("help-symbolic", []))
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_css_classes(css)
        self.add_suffix(icon)


class FirmwareView(Gtk.Box):
    """Page for dumping and flashing optical drive firmware."""

    def __init__(self, controller: MakeMKVController):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.controller = controller
        self._drives: list = []
        self._bin_path: str = ""
        self._load_ui()
        self._build_layout()
        self._connect_signals()

    # ------------------------------------------------------------------ #
    #  Load XML                                                            #
    # ------------------------------------------------------------------ #

    def _load_ui(self):
        b = Gtk.Builder()
        b.add_from_file(_UI_FILE)

        self._drive_group     = b.get_object("drive_group")
        self._drive_row       = b.get_object("drive_row")
        self._status_row      = b.get_object("status_row")
        self._file_group      = b.get_object("file_group")
        self._file_row        = b.get_object("file_row")
        self._file_browse_btn = b.get_object("file_browse_btn")
        self._progress_group  = b.get_object("progress_group")
        self._history_group   = b.get_object("history_group")
        self._history_list    = b.get_object("history_list")
        self._empty_label     = b.get_object("empty_label")
        self._dump_btn        = b.get_object("dump_btn")
        self._flash_btn       = b.get_object("flash_btn")

        self._drive_model = Gtk.StringList()
        self._drive_row.set_model(self._drive_model)
        self._drive_row.connect("notify::selected", self._on_drive_selected)

        self._file_row.connect("activated",      self._on_browse_file)
        self._file_browse_btn.connect("clicked", self._on_browse_file)
        self._dump_btn.connect("clicked",        self._on_dump_clicked)
        self._flash_btn.connect("clicked",       self._on_flash_clicked)

    # ------------------------------------------------------------------ #
    #  Assemble layout                                                     #
    # ------------------------------------------------------------------ #

    def _build_layout(self):
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        self.append(scroll)

        clamp = Adw.Clamp(maximum_size=700)
        scroll.set_child(clamp)

        page_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            margin_top=18, margin_bottom=18,
        )
        clamp.set_child(page_box)

        self._progress_bar = Gtk.ProgressBar(show_text=True, margin_top=4, margin_bottom=4)
        self._progress_group.add(self._progress_bar)

        self._progress_status = Gtk.Label(
            label="",
            halign=Gtk.Align.START,
            css_classes=["dim-label", "caption"],
            margin_bottom=8,
        )
        self._progress_group.add(self._progress_status)

        page_box.append(self._drive_group)
        page_box.append(self._file_group)
        page_box.append(self._progress_group)
        page_box.append(self._history_group)

        footer = Gtk.ActionBar()
        footer.pack_start(self._dump_btn)
        footer.pack_end(self._flash_btn)
        self.append(footer)

    # ------------------------------------------------------------------ #
    #  Signal connections                                                  #
    # ------------------------------------------------------------------ #

    def _connect_signals(self):
        self.controller.connect("drives-updated",    self._on_drives_updated)
        self.controller.connect("firmware-started",  self._on_firmware_started)
        self.controller.connect("firmware-progress", self._on_firmware_progress)
        self.controller.connect("firmware-finished", self._on_firmware_finished)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _selected_drive_index(self) -> int:
        idx = self._drive_row.get_selected()
        if 0 <= idx < len(self._drives):
            return self._drives[idx].drive_index
        return 0

    def _update_status_row(self):
        idx = self._drive_row.get_selected()
        if 0 <= idx < len(self._drives):
            status = self._drives[idx].libre_drive_status or "Unknown"
        else:
            status = "No drive selected"
        self._status_row.set_subtitle(status)

    def _set_busy(self, busy: bool):
        self._dump_btn.set_sensitive(not busy and bool(self._drives))
        self._flash_btn.set_sensitive(
            not busy and bool(self._drives) and bool(self._bin_path)
        )

    # ------------------------------------------------------------------ #
    #  Callbacks                                                           #
    # ------------------------------------------------------------------ #

    def _on_drives_updated(self, _ctrl, drives):
        self._drives = list(drives)
        while self._drive_model.get_n_items() > 0:
            self._drive_model.remove(0)
        for drive in self._drives:
            label = (
                f"{drive.device_path} — "
                f"{drive.disc_name or drive.drive_name or 'Unknown'}"
            )
            self._drive_model.append(label)
        self._update_status_row()
        self._set_busy(False)

    def _on_drive_selected(self, *_):
        self._update_status_row()

    def _on_browse_file(self, *_):
        filt = Gtk.FileFilter()
        filt.set_name("Firmware files (*.bin)")
        filt.add_pattern("*.bin")
        filt.add_pattern("*.BIN")
        dialog = Gtk.FileDialog(title="Select Firmware .bin File")
        dialog.set_default_filter(filt)
        dialog.open(
            parent=self.get_root(),
            cancellable=None,
            callback=self._on_file_chosen,
        )

    def _on_file_chosen(self, dialog, result):
        try:
            f = dialog.open_finish(result)
            if f:
                self._bin_path = f.get_path()
                self._file_row.set_subtitle(self._bin_path)
                if self._drives:
                    self._flash_btn.set_sensitive(True)
        except Exception:
            pass

    def _on_dump_clicked(self, _btn):
        idx = self._drive_row.get_selected()
        drive_label = "drive"
        if 0 <= idx < len(self._drives):
            d = self._drives[idx]
            drive_label = (
                d.disc_name or d.drive_name or f"drive{d.drive_index}"
            ).replace(" ", "_")
        output_path = os.path.expanduser(f"~/Downloads/{drive_label}_firmware.bin")
        self._progress_group.set_visible(True)
        self._set_busy(True)
        self.controller.dump_firmware(self._selected_drive_index(), output_path)

    def _on_flash_clicked(self, _btn):
        dialog = Adw.AlertDialog(
            heading="Flash Drive Firmware?",
            body=(
                "This will permanently modify the firmware of the selected drive.\n\n"
                "Only proceed if you have obtained a patched firmware from a trusted source. "
                "Flashing incorrect firmware may damage your drive."
            ),
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("flash",  "Flash Firmware")
        dialog.set_response_appearance("flash", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.connect("response", self._on_flash_confirmed)
        dialog.present(self.get_root())

    def _on_flash_confirmed(self, _dialog, response: str):
        if response != "flash":
            return
        self._progress_group.set_visible(True)
        self._set_busy(True)
        self.controller.flash_firmware(self._selected_drive_index(), self._bin_path)

    def _on_firmware_started(self, _ctrl, label: str):
        self._progress_status.set_text(label)
        self._progress_bar.set_fraction(0.0)

    def _on_firmware_progress(self, _ctrl, fraction: float, status: str):
        self._progress_bar.set_fraction(fraction)
        self._progress_status.set_text(status)

    def _on_firmware_finished(self, _ctrl, job: FirmwareJob):
        self._progress_group.set_visible(False)
        self._set_busy(False)
        if self._empty_label.get_parent():
            self._history_list.remove(self._empty_label)
        self._history_list.prepend(FirmwareHistoryRow(job))
