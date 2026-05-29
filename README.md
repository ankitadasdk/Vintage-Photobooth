# 🎞️ The Vintage Photobooth

A full-stack web application that transforms live webcam captures into authentic, stitched analog print strips. Inspired by historical newspaper mastheads and industrial steampunk machinery, this project pairs an immersive, brass-and-copper frontend with a powerful digital film emulation engine.

---

## 🛠️ System Architecture

The application is built using a modern decoupled architecture to handle real-time streaming and heavy image matrix transformations seamlessly:

* **Frontend User Interface:** Built with pure semantic HTML5, custom  CSS gradients/box-shadows, and asynchronous JavaScript. It uses Google Fonts (`UnifrakturMaguntia` for the Gothic masthead) to create an authentic tactile experience.
* **Backend Film Engine:** Powered by **FastAPI** and **Uvicorn** in Python. It handles multi-part form data processing, algorithmic color channel manipulation, and image stitching via **OpenCV (Open Source Computer Vision Library)** and **Pillow**.

---

## 🎨 Immersive Design & Film Recipes

### Skeuomorphic Interface Elements
* **Copper Piping Framework:** Wraps the live video viewport to mimic vintage machinery lenses.
* **Mechanical Toggle Switches:** Custom-styled control nodes for selecting active film emulsions.
* **Heavy Crank Wheel:** An interactive timing selector that allows users to cycle through execution intervals (5s, 7s, and 10s) using CSS transforms.

### Core Analog Emulation Math
The backend processes raw image arrays through mathematical matrix operations to emulate chemical film stocks:
* **Classic Chrome:** Alters color curves using cosine-based wave mapping (`0.5 * (1 - cos(pi * ch))`) to expand midtone contrast while injecting high-frequency Gaussian grain distribution.
* **Superia Warm:** Shifts the red channel ceiling while flattening blue baselines to mimic organic chemical degradation.
* **Fuji ACROS B&W:** Runs a non-linear bilateral filter loop (`d=9`, `sigmaColor=75`) to achieve a glamorous skin-smoothing effect, converts to grayscale, and applies a soft Gaussian blur overlay blend for a vintage glow.

---

## 🚀 Live Deployments

* **Frontend Interface:** Hosted on **Vercel** for lightning-fast global delivery.
* **Image Processing Engine:** Hosted on **Render** (Python Linux Container environment running Uvicorn).

---

## 📦 Local Installation & Setup

### Prerequisites
* Python 3.10+
* A modern web browser with webcam permissions enabled
* direct link: https://vintage-photobooth-ten.vercel.app/

### 1. Spin Up the Backend Server
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
