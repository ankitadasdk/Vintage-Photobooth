import sys
import os
import time
import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

# Force UTF-8 encoding for terminal fallback prints
sys.stdout.reconfigure(encoding='utf-8')

# Set application theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def recipe_fuji_chrome(img):
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    r = np.clip(r * 1.02, 0, 1)
    g = np.clip(g * 0.95, 0, 1)
    b = np.clip(b * 0.90, 0, 1)
    for ch in [r, g, b]:
        ch[:] = 0.5 * (1 - np.cos(np.pi * ch))
    out = (cv2.merge((b, g, r)) * 255).astype(np.uint8)
    grain = np.random.normal(0, 4, out.shape).astype(np.int16)
    return np.clip(cv2.add(out.astype(np.int16), grain), 0, 255).astype(np.uint8)

def recipe_warm_vintage(img):
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    r = np.clip(r * 1.20, 0, 1)
    g = np.clip(g * 1.08, 0, 1)
    b = np.clip(b * 0.80, 0, 1)
    r = 0.08 + 0.92 * r
    g = 0.05 + 0.95 * g
    b = 0.04 + 0.96 * b
    out = (cv2.merge((b, g, r)) * 255).astype(np.uint8)
    grain = np.random.normal(0, 7, out.shape).astype(np.int16)
    return np.clip(cv2.add(out.astype(np.int16), grain), 0, 255).astype(np.uint8)

def recipe_acros_bw(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_f = gray.astype(float) / 255.0
    gray_f = np.where(gray_f < 0.5, 1.2 * (gray_f ** 2), 1 - 1.2 * ((1 - gray_f) ** 2))
    gray_f = np.clip(gray_f, 0, 1)
    bw = (gray_f * 255).astype(np.uint8)
    bw_3ch = cv2.merge((bw, bw, bw))
    grain = np.random.normal(0, 12, bw_3ch.shape).astype(np.int16)
    return np.clip(cv2.add(bw_3ch.astype(np.int16), grain), 0, 255).astype(np.uint8)

def recipe_retro_sepia(img):
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, sepia_matrix)
    sepia = cv2.addWeighted(sepia, 0.85, np.full(img.shape, 255, dtype=np.uint8), 0.15, 0)
    return np.clip(sepia, 0, 255).astype(np.uint8)

def recipe_expired_slide(img):
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    r = np.clip(r * 1.10, 0, 1)
    g = np.clip(g * 0.85, 0, 1)
    b = np.clip(b * 1.25, 0, 1)
    return (cv2.merge((b, g, r)) * 255).astype(np.uint8)


# ==========================================
# 💻 GUI APPLICATION CLASS 💻
# ==========================================

class VintageBoothApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analog Engine - Vintage Photo Booth")
        self.geometry("1050x650")
        self.resizable(False, False)

        # Pipeline data states
        self.recipes = [recipe_fuji_chrome, recipe_warm_vintage, recipe_acros_bw, recipe_retro_sepia, recipe_expired_slide]
        self.recipe_names = ["Classic Chrome", "Superia Warm", "Fuji ACROS B&W", "1970s Sepia", "Expired Slide"]
        self.current_idx = 0
        self.is_capturing = False

        # OpenCV Camera Hook
        self.cap = cv2.VideoCapture(0)

        self.setup_ui_layout()
        self.update_webcam_feed()

    def setup_ui_layout(self):
        # Configure grid weight layout system
        self.grid_columnconfigure(0, weight=7) # Camera panel weight
        self.grid_columnconfigure(1, weight=3) # Controls panel weight
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: CAMERA VIEW ---
        self.view_panel = ctk.CTkFrame(self, corner_radius=15)
        self.view_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_display = ctk.CTkLabel(self.view_panel, text="")
        self.video_display.pack(expand=True, fill="both", padx=10, pady=10)

        # --- RIGHT PANEL: INTERACTIVE CONTROLS ---
        self.control_panel = ctk.CTkFrame(self, width=300, corner_radius=15, fg_color="#1e1e24")
        self.control_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        # Head Title Label
        self.title_lbl = ctk.CTkLabel(self.control_panel, text="ANALOG ENGINE", font=ctk.CTkFont(size=22, weight="bold", family="Courier"))
        self.title_lbl.pack(pady=(30, 10))
        
        self.subtitle_lbl = ctk.CTkLabel(self.control_panel, text="Fuji Film Simulation Lab", font=ctk.CTkFont(size=12, slant="italic"))
        self.subtitle_lbl.pack(pady=(0, 30))

        # Dropdown Selector for Recipes (Fixed from CTkSegmentedButton)
        self.radio_label = ctk.CTkLabel(self.control_panel, text="SELECT RECIPE", font=ctk.CTkFont(size=12, weight="bold"))
        self.radio_label.pack(anchor="w", padx=30, pady=(10, 5))

        self.recipe_selector = ctk.CTkComboBox(
            self.control_panel, 
            values=self.recipe_names, 
            command=self.handle_recipe_switch
        )
        self.recipe_selector.set(self.recipe_names[0])
        self.recipe_selector.pack(fill="x", padx=30, pady=(0, 30))

        # Big Master Shoot Button
        self.shoot_btn = ctk.CTkButton(
            self.control_panel, 
            text=" click to start !", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.trigger_booth_sequence
        )
        self.shoot_btn.pack(fill="x", padx=30, pady=(10, 10))

        # Status Update Box Indicator
        self.status_lbl = ctk.CTkLabel(self.control_panel, text="Status: Ready to Roll", font=ctk.CTkFont(size=12), text_color="#5cb85c")
        self.status_lbl.pack(pady=(20, 0))

    def handle_recipe_switch(self, value):
        self.current_idx = self.recipe_names.index(value)
        self.status_lbl.configure(text=f"Switched to {value}", text_color="#5bc0de")

    def update_webcam_feed(self):
        """Continuously loop running native camera arrays onto Tkinter display frame."""
        if not self.is_capturing:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                processed = self.recipes[self.current_idx](frame)
                
                # Convert frame data matrices into a Tkinter compatible format
                rgb_img = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                
                # Scale image to match frame viewport bounds cleanly
                scaled_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(680, 510))
                
                self.video_display.configure(image=scaled_img)
                self.video_display.image = scaled_img
                
        # Loop back in 15ms (~60 FPS pipeline check)
        self.after(15, self.update_webcam_feed)

    def trigger_booth_sequence(self):
        """Disables navigation arrays and runs automated countdown."""
        self.is_capturing = True
        self.shoot_btn.configure(state="disabled")
        self.recipe_selector.configure(state="disabled")
        
        captured_photos = []
        active_recipe = self.recipes[self.current_idx]

        for photo_num in range(3):
            for countdown in range(3, 0, -1):
                self.status_lbl.configure(text=f"Taking Photo {photo_num+1}/3 in {countdown}s...", text_color="#f0ad4e")
                
                # Fetch fresh camera frame to render numerical visual counts overlay
                start_time = time.time()
                while time.time() - start_time < 1.0:
                    ret, frame = self.cap.read()
                    if ret:
                        frame = cv2.flip(frame, 1)
                        live_view = active_recipe(frame)
                        
                        # Large text overlay directly onto preview feed
                        cv2.putText(live_view, f"Photo {photo_num+1}/3", (50, 150), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(live_view, str(countdown), (250, 320), cv2.FONT_HERSHEY_DUPLEX, 4.0, (255, 255, 255), 6, cv2.LINE_AA)
                        
                        rgb_img = cv2.cvtColor(live_view, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(rgb_img)
                        scaled_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(680, 510))
                        self.video_display.configure(image=scaled_img)
                        self.update()
            
            # Draw simulation white matrix flash overlay
            flash_matrix = np.full((510, 680, 3), 255, dtype=np.uint8)
            pil_flash = Image.fromarray(flash_matrix)
            flash_img = ctk.CTkImage(light_image=pil_flash, dark_image=pil_flash, size=(680, 510))
            self.video_display.configure(image=flash_img)
            self.update()
            time.sleep(0.15)

            # Snap final image frame
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                captured_photos.append(active_recipe(frame))

        # Assemble the Photostrip
        self.status_lbl.configure(text="Processing vintage photostrip...", text_color="#5bc0de")
        self.update()

        h, w, _ = captured_photos[0].shape
        border_px = 25
        bordered_photos = []
        for img in captured_photos:
            bordered = cv2.copyMakeBorder(img, border_px, border_px, border_px, border_px, 
                                         cv2.BORDER_CONSTANT, value=[242, 244, 244])
            bordered_photos.append(bordered)
        
        photostrip = cv2.vconcat(bordered_photos)
        filename = f"strip_{self.recipe_names[self.current_idx].replace(' ', '_')}_{int(time.time())}.jpg"
        cv2.imwrite(filename, photostrip)

        # Show final strip feedback to user
        self.status_lbl.configure(text=f"Saved strip output as {filename}!", text_color="#5cb85c")
        
        # Reset navigation configurations
        self.is_capturing = False
        self.shoot_btn.configure(state="normal")
        self.recipe_selector.configure(state="normal")

    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    app = VintageBoothApp()
    app.mainloop()