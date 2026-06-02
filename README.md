# 🎞️ The Vintage Photobooth

A premium, 100% serverless, client-side browser photobooth application designed to emulate authentic analog film chemistry. By combining real-time webcam video layers with high-performance, pixel-level manipulation routines, this application captures, color-grades, textures, and stitches photo strips completely offline with zero server latency.

👉 **[Live Production Deployment](https://ankitadasdk.github.io/Vintage-Photobooth/)**

---

##  Film Engine Presets

Unlike basic digital filters that use flat color overlays, our custom pixel engine (`applyAdvancedFilmEngine`) reads and reconstructs individual RGB data vectors asynchronously to recreate raw film aesthetics:

* **Acros B&W:** A clean, silky, low-contrast studio glam monochrome profile modeled after traditional silver-halide prints. Features velvet shadows and glowing, smooth skin midtones.
* **Mono Film:** A gritty, high-contrast, street-style flash monochrome preset. Utilizes a custom mathematical **S-Curve Gamma Adjustment** to drop shadows into deep charcoal while popping bright, raw highlights masked beneath a heavy, high-density analog grain layer (`grainIntensity = 55`).
* **CineStill 800T:** A Hollywood-grid inspired tungsten cinematic look. Uses **linear interpolation curves** to smoothly blend deep shadows into cold navy/teal spectrums while dynamically isolating and warming up skin highlights. Includes a built-in *halation emulator* that triggers a soft red bleed around extreme exposure borders.
* **Polaroid (Warm Nostalgia):** A rich, 1970s faded chemical profile with heavy golden-yellow/red channel shifts and compressed exposures.
* **Expired Slide & Sepia:** Classic lo-fi cross-processed acid color balancing and antiqued darkroom matte sepia tones.

---

## 🛠️ Architecture & Technical Highlights
[ Webcam Input Stream ] ──> [ HTML5 Canvas Captures ]
│
▼
[ Advanced Film Engine ]
├─ Pixel-Level RGB Mapping
├─ Linear Interpolation Split-Toning
├─ Procedural Noise (High-ISO Grain)
└─ Vignette Drop-off Coordinates
│
▼
[ Offscreen Matrix Canvas ]
├─ Paper Color Background (#f2eedf)
├─ Vertical Concatenation Stitching
└─ Vector Typographic Overlay
│
▼
[ Local Local JPG Download ]
###  Serverless Processing Engine
By shifting image manipulation from a Node.js/Sharp backend over to the **HTML5 Canvas API**, the entire processing stack runs natively in the client's browser. This completely eliminates network payload latency, server resource limits, and API execution bottlenecks.

###  Real-Time Texture Injection
Instead of stacking flat static PNG assets, the engine executes a microscopic looping matrix over raw pixel arrays (`ctx.getImageData`). It injects high-frequency, randomized salt-and-pepper variations into the byte stream, producing genuine structural film noise.

---

##  Core Stack

* **Frontend:** Semantic HTML5, CSS3 Variables, VanillaJS (ES6+)
* **Graphics & Render Pipelines:** HTML5 Canvas Context 2D, Pixel Manipulation API (`ImageData`)
* **Media Capture:** WebRTC Media Capture and Streams API (`navigator.mediaDevices.getUserMedia`)
* **Hosting Architecture:** Static Asset Deployment via GitHub Pages

---

##  Installation & Local Setup

Since this project runs entirely client-side, it has zero dependencies. You can clone and run it instantly:

1. Clone the repository:
   ```bash
   git clone [https://github.com/ankitadasdk/Vintage-Photobooth.git](https://github.com/ankitadasdk/Vintage-Photobooth.git)
Navigate into the root directory:

Bash
cd Vintage-Photobooth
Open index.html directly in any standard modern web browser, or launch it with a local server framework like VS Code's Live Server extension.

📜 License
Distributed under the MIT License. See LICENSE for more information.
