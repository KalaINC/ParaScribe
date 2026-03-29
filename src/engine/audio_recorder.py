import queue
import numpy as np
import sounddevice as sd
from PySide6.QtCore import QThread, Signal

class AudioRecorder(QThread):
    finished_recording = Signal(np.ndarray)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.samplerate = 16000
        self.channels = 1
        self.q = queue.Queue()
        self._is_recording = False
        self.stream = None
        self.audio_data = []

    def callback(self, indata, frames, time, status):
        """This is called for each audio block by sounddevice."""
        if status:
            print(status, flush=True)
        if self._is_recording:
            self.q.put(indata.copy())

    def start_recording(self):
        self.audio_data = []
        self._is_recording = True
        self.q = queue.Queue()
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            device=None,
            channels=self.channels,
            callback=self.callback,
            dtype='float32'
        )
        self.stream.start()
        self.start()  # Start the QThread event loop

    def stop_recording(self):
        self._is_recording = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        # Process remaining
        while not self.q.empty():
            self.audio_data.append(self.q.get())

        if self.audio_data:
            concatenated_audio = np.concatenate(self.audio_data, axis=0)
            self.finished_recording.emit(concatenated_audio)
        else:
            self.finished_recording.emit(np.array([]))

    def run(self):
        while self._is_recording:
            try:
                # 100ms timeout so QThread doesn't block forever
                data = self.q.get(timeout=0.1)
                self.audio_data.append(data)
            except queue.Empty:
                continue
