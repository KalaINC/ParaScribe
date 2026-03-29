from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal, QObject, Qt


class TrayController(QObject):
    start_recording_requested = Signal()
    stop_recording_requested = Signal()
    open_settings_requested = Signal()
    quit_requested = Signal()

    # GNOME palette
    _IDLE_COLOR = QColor("#3584e4")      # Adwaita blue
    _RECORDING_COLOR = QColor("#e01b24") # Adwaita destructive red

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setToolTip("ParaScribe")

        self.idle_icon = self._create_icon(self._IDLE_COLOR)
        self.recording_icon = self._create_icon(self._RECORDING_COLOR)
        self.tray_icon.setIcon(self.idle_icon)

        self.menu = QMenu()
        self.start_action = self.menu.addAction("Aufnahme starten")
        self.stop_action = self.menu.addAction("Aufnahme stoppen")
        self.stop_action.setEnabled(False)
        self.menu.addSeparator()

        self.settings_action = self.menu.addAction("Einstellungen")
        self.show_window_action = self.menu.addAction("Dashboard öffnen")
        self.menu.addSeparator()

        self.quit_action = self.menu.addAction("Beenden")

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

        # Internal connections
        self.start_action.triggered.connect(self.on_start)
        self.stop_action.triggered.connect(self.on_stop)
        self.settings_action.triggered.connect(self.open_settings_requested.emit)
        self.quit_action.triggered.connect(self.quit_requested.emit)

    @staticmethod
    def _create_icon(color: QColor) -> QIcon:
        """Simple 64x64 filled-circle icon for the system tray."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()
        return QIcon(pixmap)

    def on_start(self):
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.tray_icon.setIcon(self.recording_icon)
        self.tray_icon.setToolTip("ParaScribe – Aufnahme läuft …")
        self.start_recording_requested.emit()

    def on_stop(self):
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.tray_icon.setIcon(self.idle_icon)
        self.tray_icon.setToolTip("ParaScribe")
        self.stop_recording_requested.emit()
