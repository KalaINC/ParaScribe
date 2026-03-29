import sys
import os
import shutil

# Ensure Wayland support for PySide6 on modern Linux systems
if os.environ.get('XDG_SESSION_TYPE') == 'wayland' and 'QT_QPA_PLATFORM' not in os.environ:
    os.environ['QT_QPA_PLATFORM'] = 'wayland'

from PySide6.QtWidgets import QApplication
from src.ui.tray import TrayController
from src.ui.main_window import MainWindow
from src.ui.settings_dialog import SettingsDialog
from src.engine.audio_recorder import AudioRecorder
from src.engine.stt_worker import STTWorker
from src.engine.openai_worker import OpenAIWorker
import src.storage.fs_manager as fs

class ParaScribeApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Components
        self.tray = TrayController()
        self.window = MainWindow()
        self.settings_dialog = SettingsDialog()
        self.recorder = AudioRecorder()
        
        self.stt_worker = None
        self.openai_worker = None
        
        self.active_session = None

        self.setup_connections()

    def setup_connections(self):
        self.tray.start_recording_requested.connect(self.start_recording)
        self.tray.stop_recording_requested.connect(self.stop_recording)
        self.tray.open_settings_requested.connect(self.settings_dialog.exec)
        self.tray.quit_requested.connect(self.quit_app)
        self.tray.show_window_action.triggered.connect(self.window.show)

        # Main Window Signals
        self.window.process_note_requested.connect(self.request_openai_processing)
        self.window.file_dropped_for_stt.connect(self.handle_file_drop)
        self.window.set_active_session_requested.connect(self.set_active_session)
        
        # Audio
        self.recorder.finished_recording.connect(self.on_audio_recorded)

    def set_active_session(self, session_path):
        self.active_session = session_path

    def get_or_create_active_session(self):
        # We no longer auto-pull from window selection unless explicitly set.
        # But if it's not set, create a new one.
        if not self.active_session:
            self.active_session = fs.create_new_session_folder()
            self.window.refresh_sessions()
        return self.active_session

    def start_recording(self):
        if not self.active_session:
            self.active_session = fs.create_new_session_folder()
            self.window.refresh_sessions()
        self.recorder.start_recording()

    def stop_recording(self):
        self.recorder.stop_recording()

    def on_audio_recorded(self, audio_data):
        if audio_data.size == 0 or not self.active_session:
            self.active_session = None # Reset
            return
            
        current_sess = self.active_session
        self.active_session = None
        
        # 1. Save chunk to the full audio file (Append)
        fs.save_audio(current_sess, audio_data, samplerate=16000)
        
        # 2. Transcribe ONLY the new chunk to avoid model context limits
        # We save the chunk temporarily to disk for the STTWorker if needed, 
        # but our STTWorker can be modified to accept raw data.
        self.run_stt_on_data(current_sess, audio_data)

    def run_stt_on_data(self, session_path, audio_data):
        self.window.set_status("Parakeet transkribiert …", "#3584e4")
        self.stt_worker = STTWorker(session_path, None, audio_data=audio_data)
        self.stt_worker.finished_transcription.connect(self.on_stt_finished)
        self.stt_worker.failed.connect(self.on_stt_failed)
        self.stt_worker.start()

    def handle_file_drop(self, file_path):
        session = fs.create_new_session_folder()
        self.window.refresh_sessions()
        dest = os.path.join(session, "audio.wav")
        shutil.copy(file_path, dest)
        self.run_stt_file(session, dest)

    def run_stt_file(self, session_path, audio_file_path):
        self.window.set_status("Parakeet transkribiert …", "#3584e4")
        self.stt_worker = STTWorker(session_path, audio_file_path=audio_file_path)
        self.stt_worker.finished_transcription.connect(self.on_stt_finished)
        self.stt_worker.failed.connect(self.on_stt_failed)
        self.stt_worker.start()

    def on_stt_finished(self, session_path, transcript):

        if transcript.strip():
            fs.append_transcript(session_path, transcript)
        self.window.set_status("Bereit")
        self.window.update_detail_view()

    def on_stt_failed(self, error_msg):
        print(f"STT Error: {error_msg}")
        self.window.set_status(f"STT-Fehler: {error_msg}", "#e01b24")
        self.window.update_detail_view()

    def request_openai_processing(self, session_path):
        transcript = fs.read_transcript(session_path)
        if not transcript.strip():
            self.window.set_status("Kein Transkript vorhanden", "#e01b24")
            self.window.update_detail_view()
            return
        
        self.window.set_status("OpenAI verarbeitet …", "#3584e4")
        self.openai_worker = OpenAIWorker(session_path, transcript)
        self.openai_worker.finished_processing.connect(self.on_openai_finished)
        self.openai_worker.failed.connect(self.on_openai_failed)
        self.openai_worker.start()

    def on_openai_finished(self, session_path, markdown_content):
        fs.save_markdown(session_path, markdown_content)
        self.window.set_status("Bereit")
        self.window.update_detail_view()

    def on_openai_failed(self, error_msg):
        print(f"OpenAI Error: {error_msg}")
        self.window.set_status(f"OpenAI-Fehler: {error_msg}", "#e01b24")
        self.window.update_detail_view()


    def run(self):
        sys.exit(self.app.exec())

    def quit_app(self):
        if self.recorder._is_recording:
            self.recorder.stop_recording()
        self.app.quit()

if __name__ == "__main__":
    app = ParaScribeApp()
    app.run()
