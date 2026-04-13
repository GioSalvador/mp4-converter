import os
import sys
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk
import re

# ---------------- PATH HANDLING ---------------- #

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg_bin", "ffmpeg")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg_bin", "ffmpeg")

APP_DIR = get_app_dir()
FFMPEG_PATH = get_ffmpeg_path()

INPUT_DIR = os.path.join(APP_DIR, "convert")
OUTPUT_DIR = os.path.join(APP_DIR, "converted")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIDEO_EXTENSIONS = (
    ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv",
    ".mp4", ".mpg", ".mpeg", ".m4v", ".3gp", ".ts"
)

processed_files = set()

# ---------------- UTILS ---------------- #

def open_folder(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def get_video_duration(file_path):
    try:
        cmd = [FFMPEG_PATH, "-i", file_path]
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        _, stderr = process.communicate()

        match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", stderr)
        if match:
            h, m, s = match.groups()
            return int(h)*3600 + int(m)*60 + float(s)
    except:
        pass
    return 0

# ---------------- FFMPEG ---------------- #

def convert_with_progress(input_path, output_path, progress_callback, error_callback):
    duration = get_video_duration(input_path)

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", input_path,
        "-c:v", "h264_nvenc",
        "-preset", "p5",
        "-cq", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        if "out_time_ms=" in line:
            try:
                out_time_ms = int(line.split("=")[1])
                current_time = out_time_ms / 1_000_000

                if duration > 0:
                    percent = (current_time / duration) * 100
                    progress_callback(percent)
            except:
                pass

    _, stderr = process.communicate()

    if process.returncode != 0:
        error_callback("Conversion failed (NVENC)")
        return False

    return True


def convert_video(input_path, output_path, progress_callback, error_callback):
    # try copy first
    copy_cmd = [
        FFMPEG_PATH, "-y",
        "-i", input_path,
        "-c", "copy",
        output_path
    ]

    result = subprocess.run(copy_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        progress_callback(100)
        return True

    return convert_with_progress(input_path, output_path, progress_callback, error_callback)

# ---------------- PROCESSING ---------------- #

def process_file(file, progress_bar, status_label, error_label):
    if file in processed_files:
        return

    if not file.lower().endswith(VIDEO_EXTENSIONS):
        return

    input_path = os.path.join(INPUT_DIR, file)
    output_file = os.path.splitext(file)[0] + ".mp4"
    output_path = os.path.join(OUTPUT_DIR, output_file)

    if os.path.exists(output_path):
        processed_files.add(file)
        return

    root.after(0, lambda: status_label.config(text=f"Processing {file}"))
    root.after(0, lambda: error_label.config(text=""))

    def update_progress(percent):
        root.after(0, lambda: progress_bar.config(value=percent))

    def show_error(msg):
        root.after(0, lambda: error_label.config(text=msg))

    success = convert_video(input_path, output_path, update_progress, show_error)

    if success:
        os.remove(input_path)
        root.after(0, lambda: status_label.config(text=f"Done: {file}"))
    else:
        root.after(0, lambda: status_label.config(text=f"Failed: {file}"))

    processed_files.add(file)


def process_videos(progress_bar, status_label, error_label):
    files = os.listdir(INPUT_DIR)

    if not files:
        status_label.config(text="No files found.")
        return

    def worker():
        with ThreadPoolExecutor(max_workers=2) as executor:
            for file in files:
                executor.submit(process_file, file, progress_bar, status_label, error_label)

    threading.Thread(target=worker, daemon=True).start()

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("MP4 Video Converter")
root.geometry("420x260")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")

style.configure("TProgressbar",
                troughcolor="#2a2a2a",
                background="#4caf50",
                thickness=20)

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(expand=True)

title = tk.Label(frame, text="MP4 Converter",
                 fg="white", bg="#1e1e1e",
                 font=("Arial", 16))
title.pack(pady=10)

progress = ttk.Progressbar(frame, length=320)
progress.pack(pady=10)

status = tk.Label(frame, text="Idle",
                  fg="gray", bg="#1e1e1e")
status.pack(pady=5)

error_label = tk.Label(frame, text="",
                       fg="red", bg="#1e1e1e",
                       wraplength=350)
error_label.pack(pady=5)

convert_btn = tk.Button(
    frame,
    text="CONVERT",
    bg="#4caf50",
    fg="white",
    font=("Arial", 12),
    command=lambda: process_videos(progress, status, error_label)
)
convert_btn.pack(pady=5)

tk.Button(frame, text="Open Convert Folder",
          command=lambda: open_folder(INPUT_DIR)).pack(pady=2)

tk.Button(frame, text="Open Converted Folder",
          command=lambda: open_folder(OUTPUT_DIR)).pack(pady=2)

root.mainloop()