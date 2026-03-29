# Parascribe with NVIDIA parakeet

Parascribe ist inspiriert von OpenWhispr und existiert nur, weil OpenWhispr aktuell unter Ubuntu/Wayland zickt, **ich empfehle sonst OpenWhispr zu verwenden**.  
Also hab ich mir die Funktionen, die ich benötige, selbst gebaut.  
[OpenWhispr GitHub](https://github.com/OpenWhispr/openwhispr)

Parascribe ist eine Tray-basierte Desktop-Anwendung, die stabiles lokales Speech-to-Text (STT) und optionale KI-gestützte Textverarbeitung bietet. Das Design orientiert sich an der **GNOME/Adwaita** Designsprache für ein natives und sauberes Nutzererlebnis.

## Funktionen

-  **Lokales STT**: Nutzt `sherpa-onnx` mit dem `NVIDIA Parakeet-TDT 0.6b` Modell für hochpräzise, lokale Transkription ohne Cloud-Zwang.
-  **Drag & Drop**: Ziehe `.wav` oder `.ogg` Dateien direkt in das Dashboard für eine sofortige Transkription.
-  **Anhängen (Append)**: Ergänze bestehende Sessions nahtlos um neue Aufnahmen, um zusammengehörende Notizen an einem Ort zu bündeln.
-  **KI-Aufbereitung**: Verwandle rohe Transkripte per Mausklick in strukturierte Markdown-Notizen (via OpenAI).
-  **Keine Datenbank**: Rein ordnerbasiertes Speichersystem unter `~/Documents/ParaScribe/`.
-  **Audio-Wiedergabe**: Höre deine Aufnahmen direkt im Dashboard an.
-  **Systemübergreifend**: Läuft auf Linux (Wayland/X11), Windows und macOS mit einem konsistenten, modernen **Adwaita Dark** UI.

## Technische Architektur

- **UI-Framework**: PySide6 (Qt6 für Python)
- **STT-Engine**: sherpa-onnx (Offline Transducer Modell)
- **Audio-Logik**: sounddevice & soundfile (PCM 16kHz Mono)
- **Dateisystem**: Automatisches Verzeichnis-Management für Sessions.
- **Verarbeitung**: QThread-basierte Hintergrundprozesse für eine flüssige Bedienung.

## Installation

### System-Abhängigkeiten (Ubuntu/Debian)

Für die Audio-Aufnahme und Qt-Stabilität unter Wayland werden folgende Pakete benötigt:

```bash
sudo apt update
sudo apt install libportaudio2 portaudio19-dev libxcb-cursor0
```

### Setup

1. **Repository klonen/herunterladen**.
2. **Virtuelle Umgebung erstellen**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Modell-Einrichtung**:
   Lade das benötigte STT-Modell automatisch herunter und entpacke es:
   ```bash
   python download_model.py
   ```

### Konfiguration

Öffne die **Einstellungen** über das Tray-Menü (Rechtsklick auf das blaue Icon), um deinen **OpenAI API Key** zu hinterlegen und den System-Prompt anzupassen.

## Bedienung

1. **Aufnahme starten**: Rechtsklick auf das ParaScribe Icon im Tray und "Aufnahme starten" wählen.
2. **Stoppen & Transkribieren**: Wähle "Aufnahme stoppen". Die Transkription erfolgt automatisch im Hintergrund.
3. **Sessions verwalten**: Öffne das Dashboard, um alle Notizen einzusehen.
4. **Anhängen**: Wähle eine Session aus und klicke auf **"Anhängen"**, um neue Aufnahmen dieser spezifischen Notiz hinzuzufügen.
5. **KI-Verarbeitung**: Klicke im Dashboard auf **"Mit KI aufbereiten"**, um eine saubere, strukturierte Fassung deines Transkripts zu erstellen.
6. **Verwalten**: Klicke mit der **rechten Maustaste** auf eine Session in der Liste, um sie umzubenennen oder zu löschen.

## Ordnerstruktur

Sessions werden wie folgt gespeichert:
```text
~/Documents/ParaScribe/
    ├── 2026-03-29/
    │   ├── Note_225201/
    │   │   ├── audio.wav
    │   │   ├── transcript_raw.txt
    │   │   └── processed_notes.md
```

## Lizenz

Dieses Projekt ist Open-Source und steht unter der MIT-Lizenz.
