python vintage_booth_gui.py
Here is the complete, production-ready `README.md` code. It includes an architecture overview section so people can see how your Tkinter event loop handles the OpenCV camera stream and image processing matrices under the hood.

You can copy and paste this entire block directly into your GitHub file editor:
```markdown
# 🎞️ Analog Engine - Vintage Photo Booth

A retro-inspired digital darkroom application built with Python. This app hooks into your native webcam array, applies real-time vintage film simulation matrices (including classic Fujifilm profiles and expired slide stocks), and exports a formatted 3-panel physical-style photostrip.

---

## 🛠️ System Architecture & Data Pipeline

The application operates on a dual-phase execution pipeline combining an asynchronous frame-polling thread with deterministic color-space transformation matrices.

### 1. Real-Time Viewport Pipeline
* **Ingestion:** OpenCV handles raw hardware webcam frames via `cv2.VideoCapture(0)` operating in a native BGR color profile.
* **Matrix Transformation:** Frames are passed directly into the active vector-optimized NumPy film simulation recipe.
* **Tkinter Interface Sync:** The modified array is mirrored, color-converted to standard RGB format, wrapped into a PIL Image matrix, and dynamically rescaled via a 60 FPS update cycle (`self.after(15, ...)`).

### 2. Automated Photostrip Generation Sequence
```text
[Trigger Clicked]
       │
       ▼
 ┌───────────┐      ┌─────────────────────────┐      ┌───────────────────────────┐
 │ Disable   │ ───> │ Run 3s Visual Countdown │ ───> │ Flash Matrix Overlay      │
 │ UI Inputs │      │ (Overlay Text Array)    │      │ (White Screen State Frame)│
 └───────────┘      └─────────────────────────┘      └───────────────────────────┘
                                                                   │
                                                                   ▼
 ┌───────────┐      ┌─────────────────────────┐      ┌───────────────────────────┐
 │ Re-enable │ <─── │ Render & Save Vertical  │ <─── │ Capture Frame at 0s       │
 │ Controls  │      │ Strip via cv2.vconcat() │      │ (Loop 3 Times total)      │
 └───────────┘      └─────────────────────────┘      └───────────────────────────┘

✨ Features
Real-time Previews: Instantly test film simulation lookup matrices on your live video stream.

Automated Photostrip Sequence: Features a visual screen flash overlay and automatic 3-second countdown per shot.

Clean Directory Structure: Auto-creates an isolated /captures folder to keep your main workspace organized.

🚀 Getting Started
Follow these steps to set up and run the Vintage Photo Booth locally on your machine.

Prerequisites
Make sure you have Python 3.10 or higher installed.

Installation
Clone the repository:

Bash
git clone https://github.com/ankitadasdk/vintage_photobooth.git
cd vintage_photobooth
Set up a Virtual Environment (Recommended):

Windows:

Bash
python -m venv venv
.\venv\Scripts\activate
Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate
Install the required packages:

Bash
pip install -r requirements.txt
Running the App
Once the dependencies are installed, boot up the interface by executing:

Bash
python vintage_booth_gui.py
 Film Recipes Included
Classic Chrome: Soft, deep-tonal emulation based on high-contrast slide film with rich, saturated shadows.

Superia Warm: Elevated red and green gains with desaturated blues to emulate a warm, nostalgic consumer film stock.

Fuji ACROS B&W: Custom parabolic contrast curve modification for a punchy, sharp, fine-grain black-and-white print profile.

1970s Sepia: Matrix transformations optimized with an added white-wash canvas weighting layer for an authentic degraded layout.

Expired Slide: Cross-processed analog aesthetics showing severe green-channel suppression alongside strong blue and red channel clipping.

 Built With
CustomTkinter - Modern GUI Widget Toolkit

OpenCV - Computer Vision Engine & Real-time Array Buffering

Pillow - High-level Python Image Processing Library

NumPy - Multidimensional Array Vectorization & Math Lookups
