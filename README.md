# MP4 Video Converter

Simple and fast video converter with a clean GUI.

Convert multiple video formats to MP4 using FFmpeg with optional GPU acceleration.

---

## Features

- Convert multiple formats to MP4
- Fast processing with NVENC (NVIDIA GPU)
- Smart fallback (no re-encode when possible)
- Automatic folder workflow
- Clean dark mode interface
- Cross-platform (Windows & Linux)

---

## Download

Go to the **Releases** section and download the version for your system:

- Windows → `.exe`
- Linux → binary

---

## How to Use

1. Open the application
2. Click **"Open Convert Folder"**
3. Drop your videos into the folder
4. Click **CONVERT**
5. Done ✅

Converted files will appear in the `converted` folder.

---

## Requirements

- Windows or Linux
- NVIDIA GPU (optional, for NVENC acceleration)

---

## How It Works

- First tries **lossless copy** (fast, no quality loss)
- If not possible → uses **H.264 NVENC encoding**
- Audio is converted to AAC for compatibility

---

## Built With

- Python
- Tkinter (GUI)
- FFmpeg

---

## Notes

- On Linux, you may need to make the file executable:
  ```bash
  chmod +x mp4-converter
