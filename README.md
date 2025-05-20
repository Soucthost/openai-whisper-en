# EnglishTranscription

**EnglishTranscription** is a lightweight real-time desktop application for converting spoken English into text using [Faster-Whisper](https://github.com/guillaumekln/faster-whisper), a fast and accurate speech recognition engine.

The app runs entirely offline, requires no internet connection, and offers a simple graphical interface for starting and stopping transcription with live logging and automatic file saving.

---

## ✨ Features

- 🎧 Real-time English speech recognition
- 📄 Transcripts are automatically saved by hour (`transcripts/YYYY-MM-DD_HH.txt`)
- 💻 Runs fully offline (after model download)
- 🧠 Based on Faster-Whisper `medium` model
- 🪟 Simple GUI with start/stop buttons and activity log
- 📦 Packaged as a standalone `.exe` (Windows)

---

## ⚙️ Requirements (Before You Start)

1. **Install VB-CABLE and Enable Monitoring**
   - Download and install VB-Audio Virtual Cable: https://vb-audio.com/Cable/
   - Set **CABLE Input** as your default **Recording Device**
   - Enable **monitoring (listen to this device)** to route system audio to the virtual mic

2. **Download the Model**
   - Download the `medium` model from Google Drive:  
     👉 [Download Link](https://drive.google.com/open?id=1c042FdrPb4NZGq1KigfC05mBH3iAViGp&usp=drive_fs)
   - Place the downloaded `medium` folder inside a `models` directory next to `EnglishTranscription.exe`:
     ```
     EnglishTranscription/
     ├── EnglishTranscription.exe
     └── models/
         └── medium/
             ├── config.json
             ├── model.bin
             └── ...
     ```

---

## 🚀 How to Use

1. Launch `EnglishTranscription.exe`
2. Click **"Start Recording & Transcription"**
3. The app will begin listening via the virtual audio device and transcribing English speech
4. Transcripts are saved automatically in the `transcripts` folder
5. Click **"Stop"** to end the process

You can also click **"Open Transcripts Folder"** to view the saved text files.

---

## 📂 Output Example

Transcript files are saved by hour:

