# 🎞️ Analog Engine - Vintage Photo Booth

A retro-inspired digital darkroom application built with Python. This app hooks into your native webcam array, applies real-time vintage film simulation matrices (including classic Fujifilm profiles and expired slide stocks), and exports a formatted 3-panel physical-style photostrip.

---

# 🛠️ System Architecture & Data Pipeline

The application operates on a dual-phase execution pipeline combining an asynchronous frame-polling thread with deterministic color-space transformation matrices.

---

## 1. Real-Time Viewport Pipeline

- **Ingestion:** OpenCV handles raw hardware webcam frames via `cv2.VideoCapture(0)` operating in a native BGR color profile.
- **Matrix Transformation:** Frames are passed directly into the active vector-optimized NumPy film simulation recipe.
- **Tkinter Interface Sync:** The modified array is mirrored, color-converted to standard RGB format, wrapped into a PIL Image matrix, and dynamically rescaled via a 60 FPS update cycle using:

```python
self.after(15, ...)
```

---

## 2. Automated Photostrip Generation Sequence

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
```

---

# ✨ Core Features

## 🎥 Real-Time Previews
Instantly test film simulation lookup matrices directly on your live video stream.

## 💥 Automated Photostrip Sequence
Emulates a real booth experience with a visual screen flash and automatic 3-second countdown per shot.

## 📁 Smart File Management
Automatically generates an isolated `/captures` folder inside your project directory to prevent file clutter.

---

# 🎨 Film Simulation Recipes

| Recipe | Aesthetic Profile | Technical Breakdown |
|---|---|---|
| **Classic Chrome** | Deep, dramatic tonal slide film | High-contrast emulation with rich, saturated shadows |
| **Superia Warm** | Nostalgic consumer film stock | Elevated red/green gains paired with desaturated blues |
| **Fuji ACROS B&W** | Punchy, sharp black-and-white print | Custom parabolic contrast curve modification with fine grain |
| **1970s Sepia** | Aged, degraded vintage photo | Matrix transformations optimized with an added white-wash canvas layer |
| **Expired Slide** | Harsh, cross-processed look | Severe green-channel suppression with strong blue/red clipping |

---

# 🚀 Getting Started

Follow these steps to set up and run the Vintage Photo Booth locally on your machine.

---

## 1. Prerequisites

Make sure you have **Python 3.10 or higher** installed.

---

## 2. Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/ankitadasdk/vintage_photobooth.git
cd vintage_photobooth
```

### Set Up a Virtual Environment (Recommended)

#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Running the App

Launch the graphical interface by executing:

```bash
python vintage_booth_gui.py
```

---

# 🛠️ Stack Architecture

| Technology | Purpose |
|---|---|
| **CustomTkinter** | Modernized UI widget toolkit and styling framework |
| **OpenCV** | Computer vision engine handling webcam arrays and matrix buffering |
| **Pillow (PIL)** | High-level canvas layout architecture and image array translation |
| **NumPy** | High-performance vector math lookups for real-time color processing |

---

# 📸 Output Example

The application exports a vertically stitched 3-frame vintage photostrip styled to emulate classic analog booth prints.

---

# 📂 Project Structure

```text
vintage_photobooth/
│
├── captures/
│   └── photostrips + exported frames
│
├── vintage_booth_gui.py
├── requirements.txt
├── README.md
│
└── assets/
    └── overlays, fonts, textures
```

---

# 💡 Future Improvements

- Custom LUT imports
- VHS-style video mode
- Animated grain simulation
- Polaroid frame templates
- Direct social media export
- DSLR camera support

---

# 📜 License

This project is licensed under the MIT License.

---
