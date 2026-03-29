from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QTextEdit, QPushButton, QHBoxLayout, QFrame,
                               QWidget)
from PySide6.QtCore import QSettings, Qt

# ─── Adwaita Dark Palette (shared constants) ───────────────────────
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
_RADIUS          = "12px"
_RADIUS_SM       = "8px"
_FONT_FAMILY     = "'Cantarell', 'Inter', 'Segoe UI', system-ui, sans-serif"

SETTINGS_STYLESHEET = f"""
    QDialog {{
        background-color: {_WINDOW_BG};
        color: {_TEXT_PRIMARY};
        font-family: {_FONT_FAMILY};
    }}
    QLabel {{
        color: {_TEXT_SECONDARY};
        font-size: 12px;
        font-weight: 600;
        font-family: {_FONT_FAMILY};
        background: transparent;
    }}
    QLineEdit {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        color: {_TEXT_PRIMARY};
        padding: 8px 12px;
        font-size: 13px;
        font-family: {_FONT_FAMILY};
        selection-background-color: {_ACCENT};
    }}
    QLineEdit:focus {{
        border: 1px solid {_ACCENT};
    }}
    QTextEdit {{
        background-color: {_VIEW_BG};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        color: {_TEXT_PRIMARY};
        padding: 8px 10px;
        font-size: 13px;
        font-family: {_FONT_FAMILY};
        selection-background-color: {_ACCENT};
    }}
    QTextEdit:focus {{
        border: 1px solid {_ACCENT};
    }}
    QPushButton {{
        background-color: {_VIEW_BG_ALT};
        border: 1px solid {_BORDER_STRONG};
        border-radius: {_RADIUS_SM};
        color: {_TEXT_PRIMARY};
        padding: 7px 20px;
        font-size: 13px;
        font-weight: 500;
        font-family: {_FONT_FAMILY};
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.12);
    }}

    /* ── ScrollBar ──────────────────────────────────── */
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
"""


class PreferenceGroup(QFrame):
    """A rounded Adwaita-style preference card containing labeled rows."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            PreferenceGroup {{
                background-color: {_VIEW_BG};
                border: 1px solid {_BORDER};
                border-radius: {_RADIUS};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                color: {_TEXT_DIM};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                font-family: {_FONT_FAMILY};
                background: transparent;
                border: none;
            """)
            # Add title above the group frame
            self._external_title = title_label
        else:
            self._external_title = None

    def add_row(self, label_text, widget):
        """Add a label + widget row inside the preference card."""
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"""
            color: {_TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 600;
            font-family: {_FONT_FAMILY};
            background: transparent;
            border: none;
        """)
        self._layout.addWidget(lbl)
        self._layout.addWidget(widget)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(460, 380)
        self.setStyleSheet(SETTINGS_STYLESHEET)
        self.settings = QSettings("ParaScribe", "Settings")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── API Key Group ───────────────────────────────
        api_group = PreferenceGroup()
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)
        self.api_input.setText(self.settings.value("openai_api_key", ""))
        self.api_input.setPlaceholderText("sk-…")
        api_group.add_row("OpenAI API Key", self.api_input)

        api_title = QLabel("Verbindung")
        api_title.setStyleSheet(f"""
            color: {_TEXT_DIM};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            font-family: {_FONT_FAMILY};
        """)
        layout.addWidget(api_title)
        layout.addWidget(api_group)

        # ── Prompt Group ────────────────────────────────
        prompt_group = PreferenceGroup()
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlainText(
            self.settings.value(
                "system_prompt",
                "Du fasst das gegebene Transkript in Markdown zusammen."
            )
        )
        self.prompt_input.setMinimumHeight(100)
        prompt_group.add_row("System-Prompt (GPT)", self.prompt_input)

        prompt_title = QLabel("KI-Verarbeitung")
        prompt_title.setStyleSheet(f"""
            color: {_TEXT_DIM};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            font-family: {_FONT_FAMILY};
        """)
        layout.addWidget(prompt_title)
        layout.addWidget(prompt_group)

        layout.addStretch()

        # ── Buttons ─────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.cancel_btn = QPushButton("Abbrechen")
        self.save_btn = QPushButton("Speichern")
        # Suggested-action style for save
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: white;
                font-weight: 600;
                border: none;
                border-radius: {_RADIUS_SM};
                padding: 8px 24px;
                font-family: {_FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {_ACCENT_HOVER};
            }}
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)

    def save_settings(self):
        self.settings.setValue("openai_api_key", self.api_input.text().strip())
        self.settings.setValue("system_prompt", self.prompt_input.toPlainText().strip())
        self.accept()
