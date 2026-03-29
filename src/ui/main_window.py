import os
import soundfile as sf
import sounddevice as sd
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QListWidget,
                               QPushButton, QLabel, QFrame, QHBoxLayout, QSplitter,
                               QTextEdit, QMessageBox, QMenu, QInputDialog)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont
import src.storage.fs_manager as fs

# ─── Adwaita Dark Palette ───────────────────────────────────────────
_WINDOW_BG      = "#242424"
_VIEW_BG        = "#303030"
_VIEW_BG_ALT    = "#383838"
_BORDER         = "rgba(255, 255, 255, 0.08)"
_BORDER_STRONG  = "rgba(255, 255, 255, 0.12)"
_TEXT_PRIMARY    = "#ffffff"
_TEXT_SECONDARY  = "#9a9996"
_TEXT_DIM        = "#77767b"
_ACCENT          = "#3584e4"
_ACCENT_HOVER    = "#4a9cf7"
_ACCENT_ACTIVE   = "#2b71c7"
_DESTRUCTIVE     = "#e01b24"
_SUCCESS         = "#33d17a"
_SELECTION_BG    = "rgba(53, 132, 228, 0.20)"
_HOVER_BG        = "rgba(255, 255, 255, 0.04)"
_ACTIVE_BG       = "rgba(255, 255, 255, 0.08)"
_RADIUS          = "12px"
_RADIUS_SM       = "8px"
_FONT_FAMILY     = "'Cantarell', 'Inter', 'Segoe UI', system-ui, sans-serif"


# ─── Global Stylesheet ─────────────────────────────────────────────
ADWAITA_STYLESHEET = f"""
    /* ── Window ─────────────────────────────────────── */
    QMainWindow {{
        background-color: {_WINDOW_BG};
        color: {_TEXT_PRIMARY};
    }}

    /* ── Typography ─────────────────────────────────── */
    QLabel {{
        color: {_TEXT_PRIMARY};
        font-family: {_FONT_FAMILY};
    }}

    /* ── Views (Lists, TextEdits) ───────────────────── */
    QListWidget {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER};
        border-radius: {_RADIUS};
        color: {_TEXT_PRIMARY};
        padding: 4px;
        font-family: {_FONT_FAMILY};
        font-size: 13px;
        outline: none;
    }}
    QListWidget::item {{
        border-radius: {_RADIUS_SM};
        padding: 8px 10px;
        margin: 1px 2px;
    }}
    QListWidget::item:hover {{
        background-color: {_HOVER_BG};
    }}
    QListWidget::item:selected {{
        background-color: {_SELECTION_BG};
        color: {_TEXT_PRIMARY};
    }}

    QTextEdit {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER};
        border-radius: {_RADIUS};
        color: {_TEXT_PRIMARY};
        font-family: {_FONT_FAMILY};
        font-size: 13px;
        padding: 10px;
        selection-background-color: {_ACCENT};
    }}

    /* ── Buttons ────────────────────────────────────── */
    QPushButton {{
        background-color: {_VIEW_BG_ALT};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        color: {_TEXT_PRIMARY};
        font-family: {_FONT_FAMILY};
        font-size: 13px;
        padding: 7px 16px;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.12);
    }}
    QPushButton:pressed {{
        background-color: {_ACTIVE_BG};
    }}
    QPushButton:disabled {{
        color: {_TEXT_DIM};
        background-color: rgba(48, 48, 48, 0.5);
        border-color: rgba(255, 255, 255, 0.04);
    }}

    /* ── Splitter ───────────────────────────────────── */
    QSplitter::handle {{
        background-color: {_BORDER};
    }}
    QSplitter::handle:horizontal {{
        width: 1px;
        margin: 8px 4px;
    }}
    QSplitter::handle:vertical {{
        height: 1px;
        margin: 4px 8px;
    }}

    /* ── ScrollBar (thin, Adwaita-style) ────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(255, 255, 255, 0.15);
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(255, 255, 255, 0.25);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}

    /* ── Context Menu ───────────────────────────────── */
    QMenu {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        padding: 4px;
        font-family: {_FONT_FAMILY};
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 6px;
        color: {_TEXT_PRIMARY};
    }}
    QMenu::item:selected {{
        background-color: {_ACCENT};
        color: white;
    }}
    QMenu::separator {{
        height: 1px;
        background: {_BORDER};
        margin: 4px 8px;
    }}

    /* ── InputDialog / MessageBox ────────────────────── */
    QDialog {{
        background-color: {_WINDOW_BG};
        color: {_TEXT_PRIMARY};
    }}
    QInputDialog QLineEdit, QDialog QLineEdit {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        color: {_TEXT_PRIMARY};
        padding: 6px 10px;
        font-family: {_FONT_FAMILY};
    }}
"""


class DropFrame(QFrame):
    """Drag-and-drop zone / status indicator — Adwaita card style."""
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._update_style(hovered=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.label = QLabel("Audio-Datei hierher ziehen  (.wav, .ogg)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"""
            color: {_TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 500;
            font-family: {_FONT_FAMILY};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.label)

    def _update_style(self, hovered=False):
        border_color = _ACCENT if hovered else "rgba(255, 255, 255, 0.10)"
        bg = "rgba(53, 132, 228, 0.06)" if hovered else _VIEW_BG
        self.setStyleSheet(f"""
            DropFrame {{
                border: 1.5px dashed {border_color};
                border-radius: {_RADIUS};
                background: {bg};
            }}
        """)

    def set_text(self, text, color=None):
        c = color or _TEXT_SECONDARY
        self.label.setText(text)
        self.label.setStyleSheet(f"""
            color: {c};
            font-size: 13px;
            font-weight: 500;
            font-family: {_FONT_FAMILY};
            background: transparent;
            border: none;
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._update_style(hovered=True)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._update_style(hovered=False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._update_style(hovered=False)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            ext = os.path.splitext(path)[1].lower()
            if ext in [".wav", ".ogg"]:
                self.file_dropped.emit(path)


class MainWindow(QMainWindow):
    # Signals to main controller
    process_note_requested = Signal(str)  # session_path
    file_dropped_for_stt = Signal(str)
    set_active_session_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parascribe with NVIDIA parakeet")
        self.resize(1050, 720)
        self.setStyleSheet(ADWAITA_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 10, 12, 12)
        main_layout.setSpacing(10)

        # ── Drop / Status Frame ─────────────────────────
        self.drop_frame = DropFrame()
        self.drop_frame.file_dropped.connect(self.file_dropped_for_stt.emit)
        self.drop_frame.setFixedHeight(56)
        main_layout.addWidget(self.drop_frame)

        # ── Main Splitter ───────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        # ── Left Panel: Session List ────────────────────
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 4, 0, 0)
        left_layout.setSpacing(6)

        # List header
        list_header = QHBoxLayout()
        list_header.setContentsMargins(4, 0, 4, 0)
        lbl = QLabel("Sessions")
        lbl.setStyleSheet(f"""
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: {_TEXT_DIM};
            font-family: {_FONT_FAMILY};
        """)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setToolTip("Liste aktualisieren")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                padding: 0px;
                border-radius: 6px;
                background-color: transparent;
                border: none;
                color: {_TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {_HOVER_BG};
                color: {_TEXT_PRIMARY};
            }}
        """)
        self.refresh_btn.clicked.connect(self.refresh_sessions)

        list_header.addWidget(lbl)
        list_header.addStretch()
        list_header.addWidget(self.refresh_btn)
        left_layout.addLayout(list_header)

        self.session_list = QListWidget()
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.on_context_menu)
        self.session_list.currentItemChanged.connect(self.on_session_selected)
        left_layout.addWidget(self.session_list)

        # ── Right Panel: Session Detail ─────────────────
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(12, 4, 0, 0)
        self.right_layout.setSpacing(10)

        # Title
        self.title_label = QLabel("Wähle eine Session")
        title_font = QFont()
        title_font.setPointSize(17)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-family: {_FONT_FAMILY};")
        self.right_layout.addWidget(self.title_label)

        # ── Control Buttons ─────────────────────────────
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(6)

        self.play_audio_btn = QPushButton("▶  Wiedergabe")
        self.play_audio_btn.clicked.connect(self.play_audio)
        self.play_audio_btn.setEnabled(False)

        self.stop_audio_btn = QPushButton("◼  Stopp")
        self.stop_audio_btn.clicked.connect(self.stop_audio)
        self.stop_audio_btn.setEnabled(False)

        self.set_active_btn = QPushButton("Anhängen")
        self.set_active_btn.clicked.connect(self.on_set_active)
        self.set_active_btn.setEnabled(False)

        self.open_nautilus_btn = QPushButton("Ordner öffnen")
        self.open_nautilus_btn.clicked.connect(self.open_nautilus)
        self.open_nautilus_btn.setEnabled(False)

        ctrl_layout.addWidget(self.play_audio_btn)
        ctrl_layout.addWidget(self.stop_audio_btn)
        ctrl_layout.addWidget(self.set_active_btn)
        ctrl_layout.addWidget(self.open_nautilus_btn)
        ctrl_layout.addStretch()
        self.right_layout.addLayout(ctrl_layout)

        # ── Vertical Splitter: Text Areas ───────────────
        self.text_splitter = QSplitter(Qt.Vertical)

        # Raw transcript
        raw_widget = QWidget()
        raw_layout = QVBoxLayout(raw_widget)
        raw_layout.setContentsMargins(0, 0, 0, 0)
        raw_layout.setSpacing(4)
        raw_label = QLabel("Transkript")
        raw_label.setStyleSheet(f"""
            color: {_TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 600;
            font-family: {_FONT_FAMILY};
        """)
        raw_layout.addWidget(raw_label)
        self.raw_transcript_text = QTextEdit()
        self.raw_transcript_text.setReadOnly(True)
        self.raw_transcript_text.setPlaceholderText("Noch kein Transkript vorhanden …")
        raw_layout.addWidget(self.raw_transcript_text)
        self.text_splitter.addWidget(raw_widget)

        # Process button — Adwaita "suggested-action" style
        self.process_btn = QPushButton("Mit KI aufbereiten")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: white;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-radius: {_RADIUS_SM};
                font-family: {_FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {_ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {_ACCENT_ACTIVE};
            }}
            QPushButton:disabled {{
                background-color: rgba(48, 48, 48, 0.6);
                color: {_TEXT_DIM};
            }}
        """)
        self.process_btn.clicked.connect(self.request_process_note)
        self.process_btn.setEnabled(False)
        self.text_splitter.addWidget(self.process_btn)

        # Processed notes
        proc_widget = QWidget()
        proc_layout = QVBoxLayout(proc_widget)
        proc_layout.setContentsMargins(0, 0, 0, 0)
        proc_layout.setSpacing(4)
        proc_label = QLabel("Aufbereitete Notiz")
        proc_label.setStyleSheet(f"""
            color: {_TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 600;
            font-family: {_FONT_FAMILY};
        """)
        proc_layout.addWidget(proc_label)
        self.processed_notes_text = QTextEdit()
        self.processed_notes_text.setReadOnly(True)
        self.processed_notes_text.setPlaceholderText("Wird nach der KI-Verarbeitung angezeigt …")
        proc_layout.addWidget(self.processed_notes_text)
        self.text_splitter.addWidget(proc_widget)

        self.right_layout.addWidget(self.text_splitter, 1)

        self.text_splitter.setCollapsible(0, False)
        self.text_splitter.setCollapsible(1, False)
        self.text_splitter.setCollapsible(2, False)

        # ── Splitter proportions ────────────────────────
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

        self.refresh_sessions()

    # ── Status ──────────────────────────────────────────
    def set_status(self, text, color=None):
        if text == "Bereit":
            self.drop_frame.set_text("Audio-Datei hierher ziehen  (.wav, .ogg)")
        else:
            self.drop_frame.set_text(text, color)

    # ── Context menu ────────────────────────────────────
    def on_context_menu(self, pos: QPoint):
        item = self.session_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Umbenennen")
        delete_action = menu.addAction("Löschen")
        # Style destructive action
        delete_action.setData("destructive")

        action = menu.exec(self.session_list.mapToGlobal(pos))

        if action == rename_action:
            self.rename_selected_session()
        elif action == delete_action:
            self.delete_selected_session()

    def rename_selected_session(self):
        old_path = self.get_selected_session_path()
        if not old_path:
            return

        old_name = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(
            self, "Umbenennen", "Neuer Name für diese Session:",
            text=old_name
        )

        if ok and new_name and new_name != old_name:
            success, result = fs.rename_session(old_path, new_name)
            if success:
                self.refresh_sessions()
                renamed_name = os.path.basename(result)
                items = self.session_list.findItems(renamed_name, Qt.MatchExactly)
                if items:
                    self.session_list.setCurrentItem(items[0])
            else:
                QMessageBox.warning(self, "Fehler", f"Konnte nicht umbenennen: {result}")

    def delete_selected_session(self):
        path = self.get_selected_session_path()
        if not path:
            return

        confirm = QMessageBox.question(
            self, "Session löschen",
            f"Soll die Session '{os.path.basename(path)}' unwiderruflich gelöscht werden?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            fs.delete_session(path)
            self.refresh_sessions()
            if self.session_list.count() == 0:
                self.on_session_selected(None, None)

    # ── Session list management ─────────────────────────
    def refresh_sessions(self):
        current = self.session_list.currentItem()
        current_name = current.text() if current else None

        self.session_list.clear()
        sessions = fs.get_all_sessions()

        for s in sessions:
            name = os.path.basename(s)
            self.session_list.addItem(name)

        if current_name:
            items = self.session_list.findItems(current_name, Qt.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])

    def on_session_selected(self, current, previous):
        if not current:
            self.title_label.setText("Wähle eine Session")
            self.raw_transcript_text.clear()
            self.processed_notes_text.clear()
            self.play_audio_btn.setEnabled(False)
            self.stop_audio_btn.setEnabled(False)
            self.open_nautilus_btn.setEnabled(False)
            self.process_btn.setEnabled(False)
            self.set_active_btn.setEnabled(False)
            return

        session_path = self.get_selected_session_path()
        if not session_path:
            return

        self.title_label.setText(os.path.basename(session_path))
        self.open_nautilus_btn.setEnabled(True)
        self.set_active_btn.setEnabled(True)

        audio_path = os.path.join(session_path, "audio.wav")
        has_audio = os.path.exists(audio_path)
        self.play_audio_btn.setEnabled(has_audio)

        raw = fs.read_transcript(session_path)
        self.raw_transcript_text.setPlainText(raw)
        self.process_btn.setEnabled(len(raw.strip()) > 0)

        md_path = os.path.join(session_path, "processed_notes.md")
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                self.processed_notes_text.setMarkdown(f.read())
        else:
            self.processed_notes_text.clear()

    # ── Audio playback ──────────────────────────────────
    def play_audio(self):
        session_path = self.get_selected_session_path()
        if not session_path:
            return
        audio_path = os.path.join(session_path, "audio.wav")
        if os.path.exists(audio_path):
            try:
                data, fs_rate = sf.read(audio_path)
                sd.play(data, fs_rate)
                self.stop_audio_btn.setEnabled(True)
            except Exception as e:
                QMessageBox.warning(self, "Audio-Fehler", str(e))

    def stop_audio(self):
        sd.stop()
        self.stop_audio_btn.setEnabled(False)

    def on_set_active(self):
        path = self.get_selected_session_path()
        if path:
            self.set_active_session_requested.emit(path)
            QMessageBox.information(
                self, "Append-Modus",
                f"Die Session '{os.path.basename(path)}' ist nun das Ziel für neue Aufnahmen."
            )

    def request_process_note(self):
        path = self.get_selected_session_path()
        if path:
            self.process_note_requested.emit(path)
            self.process_btn.setEnabled(False)
            self.process_btn.setText("Verarbeite …")

    def update_detail_view(self):
        """Called externally when STT or OpenAI finishes."""
        self.refresh_sessions()
        current = self.session_list.currentItem()
        if current:
            self.on_session_selected(current, None)
            self.process_btn.setText("Mit KI aufbereiten")

    def get_selected_session_path(self):
        item = self.session_list.currentItem()
        if item:
            sessions = fs.get_all_sessions()
            for s in sessions:
                if os.path.basename(s) == item.text():
                    return s
        return None

    def open_nautilus(self):
        path = self.get_selected_session_path()
        if path:
            fs.open_in_nautilus(path)
