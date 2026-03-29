import os
import datetime
import subprocess

def get_base_path():
    """Returns the base path ~/Documents/ParaScribe/"""
    home = os.path.expanduser("~")
    path = os.path.join(home, "Documents", "ParaScribe")
    os.makedirs(path, exist_ok=True)
    return path

def create_new_session_folder():
    """Creates a new session folder and returns its path."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("Note_%H%M%S")
    
    session_path = os.path.join(get_base_path(), date_str, time_str)
    os.makedirs(session_path, exist_ok=True)
    return session_path

def get_all_sessions():
    """List all sessions ordered by date."""
    base_path = get_base_path()
    sessions = []
    
    for root, dirs, files in os.walk(base_path):
        # Identify a session folder: contains audio.wav or transcript_raw.txt
        if "audio.wav" in files or "transcript_raw.txt" in files:
            sessions.append(root)
            
    # Sort them descending (using folder name/path which usually starts with date)
    sessions.sort(reverse=True)
    return sessions

def rename_session(old_path, new_name):
    """Renames the session folder to new_name."""
    parent = os.path.dirname(old_path)
    # Ensure name is filesystem safeish (very basic sanitization here)
    safe_name = "".join([c for c in new_name if c.isalnum() or c in (" ", "-", "_")])
    new_path = os.path.join(parent, safe_name)
    if os.path.exists(new_path):
        return False, "Ein Ordner mit diesem Namen existiert bereits."
    
    try:
        os.rename(old_path, new_path)
        return True, new_path
    except Exception as e:
        return False, str(e)

def save_audio(session_path, audio_data, samplerate=16000):
    """Saves numpy audio data to audio.wav in the session path."""
    import soundfile as sf
    import numpy as np
    
    file_path = os.path.join(session_path, "audio.wav")
    
    # Ensure audio_data is 1D for mono operations
    audio_data = np.squeeze(audio_data)
    
    # Check if we need to append
    if os.path.exists(file_path):
        data, sr = sf.read(file_path)
        data = np.squeeze(data) # Ensure existing data is also 1D
        combined = np.concatenate((data, audio_data), axis=0)
        sf.write(file_path, combined, samplerate)
    else:
        sf.write(file_path, audio_data, samplerate)


def append_transcript(session_path, text):
    """Appends to transcript_raw.txt"""
    file_path = os.path.join(session_path, "transcript_raw.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def read_transcript(session_path):
    file_path = os.path.join(session_path, "transcript_raw.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_markdown(session_path, markdown_text):
    """Saves to processed_notes.md"""
    file_path = os.path.join(session_path, "processed_notes.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

def open_in_nautilus(session_path):
    """Opens the directory in the default file manager (Cross-Platform)."""
    import platform
    if platform.system() == "Windows":
        os.startfile(session_path)
    elif platform.system() == "Darwin": # macOS
        subprocess.Popen(["open", session_path])
    else: # Linux/Unix
        subprocess.Popen(["xdg-open", session_path])

def delete_session(session_path):
    """Deletes the entire session folder."""
    import shutil
    if os.path.exists(session_path):
        shutil.rmtree(session_path)

