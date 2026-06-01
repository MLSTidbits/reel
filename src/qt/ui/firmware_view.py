"""
FirmwareView — Dump and flash optical drive firmware to enable LibreDrive.
All layout built programmatically (Qt frontend convention — no .ui file).
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QLineEdit, QFileDialog, QScrollArea,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QMessageBox, QComboBox,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor

from core.makemkv_controller import MakeMKVController
from core.models import FirmwareJob


class FirmwareView(QWidget):
    """Page for dumping and flashing optical drive firmware."""

    def __init__(self, controller: MakeMKVController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._drives: list = []
        self._bin_path: str = ""
        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------ #
    #  Build UI                                                            #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # ── Drive selector ── #
        drive_box = QGroupBox("Drive")
        drive_layout = QVBoxLayout(drive_box)
        self._drive_combo = QComboBox()
        self._drive_combo.currentIndexChanged.connect(self._on_drive_changed)
        drive_layout.addWidget(self._drive_combo)
        self._status_label = QLabel("LibreDrive Status: —")
        drive_layout.addWidget(self._status_label)
        layout.addWidget(drive_box)

        # ── Firmware file ── #
        file_box = QGroupBox("Firmware File")
        file_layout = QHBoxLayout(file_box)
        self._file_edit = QLineEdit()
        self._file_edit.setReadOnly(True)
        self._file_edit.setPlaceholderText("No file selected — click Browse to select a .bin file")
        file_layout.addWidget(self._file_edit)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._on_browse_file)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_box)

        # ── Progress (hidden until operation starts) ── #
        self._progress_box = QGroupBox("Progress")
        prog_layout = QVBoxLayout(self._progress_box)
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        prog_layout.addWidget(self._progress_bar)
        self._progress_status = QLabel("")
        self._progress_status.setStyleSheet("color: gray; font-size: 11px;")
        prog_layout.addWidget(self._progress_status)
        self._progress_box.setVisible(False)
        layout.addWidget(self._progress_box)

        # ── Operation history ── #
        history_box = QGroupBox("Operation History")
        history_layout = QVBoxLayout(history_box)
        self._history_table = QTableWidget(0, 4)
        self._history_table.setHorizontalHeaderLabels(["Operation", "File", "Status", "Date"])
        self._history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._history_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self._history_table)
        layout.addWidget(history_box)

        layout.addStretch()

        # ── Footer ── #
        footer = QFrame()
        footer.setFrameShape(QFrame.StyledPanel)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 8, 12, 8)

        self._dump_btn = QPushButton("Dump Firmware")
        self._dump_btn.setEnabled(False)
        self._dump_btn.setToolTip("Save current drive firmware to a .bin file")
        self._dump_btn.clicked.connect(self._on_dump_clicked)
        footer_layout.addWidget(self._dump_btn, alignment=Qt.AlignLeft)

        footer_layout.addStretch()

        self._flash_btn = QPushButton("Flash Firmware")
        self._flash_btn.setEnabled(False)
        self._flash_btn.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; }"
            "QPushButton:hover { background-color: #e74c3c; }"
            "QPushButton:disabled { background-color: #888; color: #ccc; }"
        )
        self._flash_btn.setToolTip("Write a patched firmware .bin to the drive to enable LibreDrive")
        self._flash_btn.clicked.connect(self._on_flash_clicked)
        footer_layout.addWidget(self._flash_btn, alignment=Qt.AlignRight)

        root.addWidget(footer)

    # ------------------------------------------------------------------ #
    #  Signal connections                                                  #
    # ------------------------------------------------------------------ #

    def _connect_signals(self):
        self.controller.drives_updated.connect(self._on_drives_updated)
        self.controller.firmware_started.connect(self._on_firmware_started)
        self.controller.firmware_progress.connect(self._on_firmware_progress)
        self.controller.firmware_finished.connect(self._on_firmware_finished)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _selected_drive_index(self) -> int:
        idx = self._drive_combo.currentIndex()
        if 0 <= idx < len(self._drives):
            return self._drives[idx].drive_index
        return 0

    def _set_busy(self, busy: bool):
        self._dump_btn.setEnabled(not busy and bool(self._drives))
        self._flash_btn.setEnabled(
            not busy and bool(self._drives) and bool(self._bin_path)
        )

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    @pyqtSlot(list)
    def _on_drives_updated(self, drives: list):
        self._drives = list(drives)
        self._drive_combo.blockSignals(True)
        self._drive_combo.clear()
        for drive in self._drives:
            label = (
                f"{drive.device_path} — "
                f"{drive.disc_name or drive.drive_name or 'Unknown'}"
            )
            self._drive_combo.addItem(label)
        self._drive_combo.blockSignals(False)
        self._on_drive_changed(self._drive_combo.currentIndex())
        self._set_busy(False)

    def _on_drive_changed(self, index: int):
        if 0 <= index < len(self._drives):
            status = self._drives[index].libre_drive_status or "Unknown"
        else:
            status = "—"
        self._status_label.setText(f"LibreDrive Status: {status}")

    def _on_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Firmware .bin File",
            os.path.expanduser("~"),
            "Firmware files (*.bin *.BIN);;All files (*)",
        )
        if path:
            self._bin_path = path
            self._file_edit.setText(path)
            if self._drives:
                self._flash_btn.setEnabled(True)

    def _on_dump_clicked(self):
        idx = self._drive_combo.currentIndex()
        drive_label = "drive"
        if 0 <= idx < len(self._drives):
            d = self._drives[idx]
            drive_label = (
                d.disc_name or d.drive_name or f"drive{d.drive_index}"
            ).replace(" ", "_")
        output_path = os.path.expanduser(f"~/Downloads/{drive_label}_firmware.bin")
        self._progress_box.setVisible(True)
        self._set_busy(True)
        self.controller.dump_firmware(self._selected_drive_index(), output_path)

    def _on_flash_clicked(self):
        reply = QMessageBox.question(
            self,
            "Flash Drive Firmware?",
            "This will permanently modify the firmware of the selected drive.\n\n"
            "Only proceed if you have obtained a patched firmware from a trusted source. "
            "Flashing incorrect firmware may damage your drive.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._progress_box.setVisible(True)
        self._set_busy(True)
        self.controller.flash_firmware(self._selected_drive_index(), self._bin_path)

    @pyqtSlot(str)
    def _on_firmware_started(self, label: str):
        self._progress_status.setText(label)
        self._progress_bar.setValue(0)

    @pyqtSlot(float, str)
    def _on_firmware_progress(self, fraction: float, status: str):
        self._progress_bar.setValue(int(fraction * 100))
        self._progress_status.setText(status)

    @pyqtSlot(object)
    def _on_firmware_finished(self, job: FirmwareJob):
        self._progress_box.setVisible(False)
        self._set_busy(False)
        row = self._history_table.rowCount()
        self._history_table.insertRow(0)
        op_label = "Dump" if job.operation == "dump" else "Flash"
        self._history_table.setItem(0, 0, QTableWidgetItem(op_label))
        self._history_table.setItem(0, 1, QTableWidgetItem(os.path.basename(job.bin_path)))
        status_item = QTableWidgetItem(job.status.capitalize())
        if job.status == "done":
            status_item.setForeground(QColor("#27ae60"))
        elif job.status == "failed":
            status_item.setForeground(QColor("#c0392b"))
        self._history_table.setItem(0, 2, status_item)
        self._history_table.setItem(0, 3, QTableWidgetItem(job.timestamp))
