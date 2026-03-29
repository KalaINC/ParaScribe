import os
import soundfile as sf
import sounddevice as sd
import numpy as np
import sherpa_onnx
from PySide6.QtCore import QThread, Signal

def get_recognizer():
    # Try possible directory names
    possible_dirs = [
        "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8",
        "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3"
    ]
    
    model_dir = None
    for d in possible_dirs:
        path = os.path.join(os.getcwd(), "models", d)
        if os.path.exists(path):
            model_dir = path
            break

    if not model_dir:
        print(f"Model directory not found in models/ {possible_dirs}")
        return None

    encoder = os.path.join(model_dir, "encoder.int8.onnx")
    decoder = os.path.join(model_dir, "decoder.int8.onnx")
    joiner = os.path.join(model_dir, "joiner.int8.onnx")
    tokens = os.path.join(model_dir, "tokens.txt")

    # If encoder.int8.onnx doesn't exist, try model.onnx (general fallback)
    if not os.path.exists(encoder):
        encoder = os.path.join(model_dir, "model.onnx")

    if os.path.exists(joiner):
        # Transducer / TDT configuration
        return sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            tokens=tokens,
            model_type="nemo_transducer",
            num_threads=4,
            sample_rate=16000,
            feature_dim=80,
            decoding_method="greedy_search",
        )

    else:
        # Fallback to CTC
        return sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
            model=encoder,
            tokens=tokens,
            num_threads=4,
            sample_rate=16000,
            feature_dim=80,
        )


class STTWorker(QThread):
    finished_transcription = Signal(str, str) # session_path, transcript
    failed = Signal(str)

    def __init__(self, session_path, audio_file_path=None, audio_data=None, parent=None):
        super().__init__(parent)
        self.session_path = session_path
        self.audio_file_path = audio_file_path
        self.audio_data = audio_data
        self.recognizer = get_recognizer()

    def run(self):
        if not self.recognizer:
            self.failed.emit("Model not loaded. Try downloading it first.")
            return

        try:
            sample_rate = 16000
            if self.audio_data is not None:
                samples = self.audio_data.astype('float32')
            else:
                samples, sample_rate = sf.read(self.audio_file_path, dtype='float32')
            
            if samples.ndim > 1:
                # Average to mono
                samples = samples.mean(axis=1)

            stream = self.recognizer.create_stream()
            stream.accept_waveform(sample_rate, samples)
            self.recognizer.decode_stream(stream)
            
            transcript = stream.result.text
            self.finished_transcription.emit(self.session_path, transcript)
        except Exception as e:
            self.failed.emit(str(e))


