import os
import urllib.request
import tarfile
import sys

MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2"
ARCHIVE_NAME = "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3.tar.bz2"
MODEL_DIR = "models"
EXTRACTED_DIR = "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3"

def download_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\rDownloading: {percent}%")
    sys.stdout.flush()

def main():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    archive_path = os.path.join(MODEL_DIR, ARCHIVE_NAME)
    extracted_path = os.path.join(MODEL_DIR, EXTRACTED_DIR)

    if os.path.exists(extracted_path):
        print("Model already exists.")
        return

    if not os.path.exists(archive_path):
        print(f"Downloading {MODEL_URL}...")
        urllib.request.urlretrieve(MODEL_URL, archive_path, reporthook=download_progress)
        print("\nDownload finished.")

    print(f"Extracting {archive_path}...")
    with tarfile.open(archive_path, "r:bz2") as tar:
        tar.extractall(path=MODEL_DIR)
    print("Extraction finished.")

if __name__ == "__main__":
    main()
