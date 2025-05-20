import os
import sys
import datetime
import threading
import traceback
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import tkinter as tk
from tkinter import messagebox, scrolledtext
from collections import deque
from pathlib import Path

# ————— Configuration Parameters —————
SAMPLE_RATE = 16000      # Sample rate
WINDOW = 30              # Inference window length (seconds)
STEP = 15                # Inference interval (seconds)
OUTPUT_DIR = "transcripts"
LOG_FILE = "log.txt"

# Determine BASE_DIR depending on whether the script is packaged
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Paths
MODEL_PATH = os.path.join(BASE_DIR, "models", "medium")
log_file_path = os.path.join(BASE_DIR, LOG_FILE)
OUTPUT_PATH = os.path.join(BASE_DIR, OUTPUT_DIR)

# Initialize
os.makedirs(OUTPUT_PATH, exist_ok=True)
log_lock = threading.Lock()
stop_event = threading.Event()
log_text_widget = None  # Will be set in the GUI

# Logging function
def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{ts}] {msg}"
    print(full_msg)

    # Write to log file
    with log_lock, open(log_file_path, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

    # Update GUI log if available
    if log_text_widget:
        gui_ts = datetime.datetime.now().strftime("%H:%M:%S")
        log_text_widget.insert(tk.END, f"[{gui_ts}] {msg}\n")
        log_text_widget.see(tk.END)

# Audio buffer
buffer = deque(maxlen=WINDOW * SAMPLE_RATE)
last_log_time = [0]

def audio_callback(indata, frames, time, status):
    if status:
        log(f"[Audio callback status] {status}")
    buffer.extend(indata[:, 0].tolist())

    now = datetime.datetime.now().timestamp()
    if now - last_log_time[0] >= 5:
        last_log_time[0] = now
        log(f"[Audio collection] Received {frames} frames, current buffer length: {len(buffer)}")

def transcribe_loop():
    while not stop_event.is_set():
        if len(buffer) >= WINDOW * SAMPLE_RATE:
            log(f"[Inference prep] Collected {len(buffer)} samples, starting inference...")
            audio = np.array(buffer, dtype=np.float32)[-WINDOW * SAMPLE_RATE:]
            try:
                segments, _ = model.transcribe(
                    audio,
                    beam_size=10,
                    language="en",
                    vad_filter=False
                )
                text_parts = [seg.text for seg in segments]
                text = "".join(text_parts).strip()

                if text:
                    ts = datetime.datetime.now()
                    fname = ts.strftime("%Y-%m-%d_%H") + ".txt"
                    path = os.path.join(OUTPUT_PATH, fname)
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(f"[{ts.strftime('%H:%M:%S')}] {text}\n")
                    log(f"💾 Successfully wrote transcription to: {path}")
                    log(f"📌 Content: {text}")
                else:
                    log("📭 No valid speech content")
            except Exception as e:
                err = f"[Inference error] {e}\n{traceback.format_exc()}"
                log(err)
                messagebox.showerror("Inference Error", err)
        for _ in range(STEP):
            if stop_event.is_set():
                break
            sd.sleep(1000)

def start_recording():
    try:
        stop_event.clear()
        buffer.clear()
        stream.start()
        threading.Thread(target=transcribe_loop, daemon=True).start()
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")
        log("▶️ Started recording + transcription")
    except Exception as e:
        log(f"[Startup error] {e}")
        messagebox.showerror("Startup Failed", str(e))

def stop_recording():
    try:
        stop_event.set()
        stream.stop()
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        log("⏹️ Stopped recording")
    except Exception as e:
        log(f"[Stop error] {e}")
        messagebox.showerror("Stop Failed", str(e))

def on_closing():
    try:
        if stop_btn['state'] == 'normal':
            stop_recording()
        root.destroy()
    except Exception as e:
        log(f"[Close error] {e}")
        sys.exit(1)

def create_gui():
    global root, start_btn, stop_btn, stream, model, log_text_widget

    log(f"Model path: {MODEL_PATH}")
    log(f"BASE_DIR: {BASE_DIR}")

    if not os.path.exists(MODEL_PATH):
        log(f"⚠️ Model directory does not exist: {MODEL_PATH}")
        dirs = os.listdir(BASE_DIR)
        log(f"BASE_DIR contents: {dirs}")
        if "models" in dirs:
            models_dir = os.path.join(BASE_DIR, "models")
            log(f"models directory contents: {os.listdir(models_dir)}")

    try:
        model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", local_files_only=True)
        log(f"✅ Model loaded successfully: {MODEL_PATH}")
    except Exception as e:
        log(f"[Model loading error] {e}\n{traceback.format_exc()}")
        messagebox.showerror("Model Loading Failed", f"{e}")
        sys.exit(1)

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback
    )

    # GUI
    root = tk.Tk()
    root.title("Real-time English Speech Transcription")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    main_frame = tk.Frame(root, padx=15, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    top_frame = tk.Frame(main_frame)
    top_frame.pack(fill=tk.X, pady=5)

    lang_label = tk.Label(top_frame, text="Current Mode: English", fg="blue")
    lang_label.pack(side=tk.RIGHT, pady=5)

    control_frame = tk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=10)

    start_btn = tk.Button(control_frame, text="Start Recording & Transcription", command=start_recording)
    start_btn.pack(side=tk.LEFT, padx=5)

    stop_btn = tk.Button(control_frame, text="Stop", command=stop_recording, state="disabled")
    stop_btn.pack(side=tk.LEFT, padx=5)

    tk.Label(main_frame, text="Transcripts will be saved to the 'transcripts' folder by hour", fg="gray").pack(anchor="w", pady=5)

    log_frame = tk.LabelFrame(main_frame, text="Activity Log")
    log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    log_text_widget = scrolledtext.ScrolledText(log_frame, height=15)
    log_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def open_output_folder():
        try:
            output_path = os.path.abspath(OUTPUT_PATH)
            if os.path.exists(output_path):
                if sys.platform == 'win32':
                    os.startfile(output_path)
                elif sys.platform == 'darwin':
                    import subprocess
                    subprocess.Popen(['open', output_path])
                else:
                    import subprocess
                    subprocess.Popen(['xdg-open', output_path])
            else:
                log(f"Output directory does not exist: {output_path}")
        except Exception as e:
            log(f"Error opening output folder: {e}")

    folder_btn = tk.Button(main_frame, text="Open Transcripts Folder", command=open_output_folder)
    folder_btn.pack(anchor="e", pady=5)

    root.geometry("650x500")
    root.mainloop()

if __name__ == "__main__":
    create_gui()
