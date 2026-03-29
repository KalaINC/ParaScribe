import os
from openai import OpenAI
from PySide6.QtCore import QThread, Signal, QSettings

class OpenAIWorker(QThread):
    finished_processing = Signal(str, str) # session_path, markdown_content
    failed = Signal(str)

    def __init__(self, session_path, transcript_text, parent=None):
        super().__init__(parent)
        self.session_path = session_path
        self.transcript_text = transcript_text
        self.settings = QSettings("ParaScribe", "Settings")

    def run(self):
        try:
            api_key = self.settings.value("openai_api_key", "")
            if not api_key:
                self.failed.emit("Kein API Key gefunden. Bitte in den Einstellungen eintragen.")
                return

            prompt = self.settings.value("system_prompt", "Du fasst das gegebene Transkript in Markdown zusammen.")

            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": self.transcript_text}
                ],
                #temperature=0.3
            )
            
            markdown_content = response.choices[0].message.content
            self.finished_processing.emit(self.session_path, markdown_content)
        except Exception as e:
            self.failed.emit(str(e))
