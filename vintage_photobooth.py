import cv2
import numpy as np
import time
import sys
import os


sys.stdout.reconfigure(encoding='utf-8')


def recipe_fuji_chrome(img):
    """Muted, cinematic, low saturation with deep shadows."""
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    
    # Compress tones
    r = np.clip(r * 1.02, 0, 1)
    g = np.clip(g * 0.95, 0, 1)
    b = np.clip(b * 0.90, 0, 1)
    
    # Subtle S-Curve contrast boost
    for ch in [r, g, b]:
        ch[:] = 0.5 * (1 - np.cos(np.pi * ch))
        
    out = (cv2.merge((b, g, r)) * 255).astype(np.uint8)
    # Light subtle grain
    grain = np.random.normal(0, 4, out.shape).astype(np.int16)
    return np.clip(cv2.add(out.astype(np.int16), grain), 0, 255).astype(np.uint8)

def recipe_warm_vintage(img):
    """Superia/Gold 200 style. Warm golden highlights, faded matte shadows."""
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    
    # Heavy warm shift
    r = np.clip(r * 1.20, 0, 1)
    g = np.clip(g * 1.08, 0, 1)
    b = np.clip(b * 0.80, 0, 1)
    
    # Lift the black floor for a matte look
    r = 0.08 + 0.92 * r
    g = 0.05 + 0.95 * g
    b = 0.04 + 0.96 * b
    
    out = (cv2.merge((b, g, r)) * 255).astype(np.uint8)
    grain = np.random.normal(0, 7, out.shape).astype(np.int16)
    return np.clip(cv2.add(out.astype(np.int16), grain), 0, 255).astype(np.uint8)

def recipe_acros_bw(img):
    # 1. Denoise FIRST. This stops the webcam grain from turning into harsh shadows.
    # Bilateral filter is magic—it blurs skin/flat areas but keeps facial features sharp.
    smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    
    # 2. Convert to plain grayscale
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    
    # 3. Force the contrast to be flat and soft. 
    # alpha=0.6 lowers contrast, beta=60 lifts the blacks to a dreamy dark grey.
    flat_gray = cv2.convertScaleAbs(gray, alpha=0.6, beta=60)
    
    # 4. Convert back to 3-channel so we can add the vintage tint
    gray_3ch = cv2.cvtColor(flat_gray, cv2.COLOR_GRAY2BGR)
    
    # 5. The Kendall Jenner warm tint (done safely without breaking pixel math)
    # We create a solid block of warm brown-ish color and gently overlay it.
    # BGR format: mostly red and green, low blue.
    warm_overlay = np.full(gray_3ch.shape, (20, 35, 50), dtype=np.uint8)
    tinted = cv2.addWeighted(gray_3ch, 0.85, warm_overlay, 0.25, 0)
    
    # 6. Add the final "Pro-Mist" glow effect to blur away any remaining harshness
    blur = cv2.GaussianBlur(tinted, (15, 15), 0)
    final = cv2.addWeighted(tinted, 0.75, blur, 0.25, 0)
    
    return final

def recipe_retro_sepia(img):
    """1970s faded, aged-paper Polaroid look."""
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, sepia_matrix)
    # Wash it out slightly
    sepia = cv2.addWeighted(sepia, 0.85, np.full(img.shape, 255, dtype=np.uint8), 0.15, 0)
    return np.clip(sepia, 0, 255).astype(np.uint8)

def recipe_expired_slide(img):
    """Cross-processed neon/cool look. Heavy blue/red, compressed greens."""
    img_f = img.astype(float) / 255.0
    b, g, r = cv2.split(img_f)
    
    r = np.clip(r * 1.10, 0, 1)
    g = np.clip(g * 0.85, 0, 1)
    b = np.clip(b * 1.25, 0, 1)
    
    return (cv2.merge((b, g, r)) * 255).astype(np.uint8)


def main():
    # Capture webcam loop
    cap = cv2.VideoCapture(0)
    
    # Register recipes and menus
    filters = [recipe_fuji_chrome, recipe_warm_vintage, recipe_acros_bw, recipe_retro_sepia, recipe_expired_slide]
    filter_names = ["Classic Chrome", "Superia Warm", "Fuji ACROS B&W", "1970s Sepia", "Expired Slide"]
    current_idx = 0
    
    print(" Vintage Photo Booth is Online!")
    print(" -> Press [C] to cycle through film recipes.")
    print(" -> Press [SPACEBAR] to capture your photostrip.")
    print(" -> Press [ESC] to safely terminate setup.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Flip frame horizontally to create mirror effect
        frame = cv2.flip(frame, 1)
        
        # Apply the current active film simulation
        active_recipe = filters[current_idx]
        preview = active_recipe(frame)
        
        # Draw UI text indicators
        cv2.putText(preview, f"Recipe: {filter_names[current_idx]} [C to Change]", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(preview, "Press SPACE to Shoot", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
        
        cv2.imshow("Vintage Camera Monitor", preview)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Cycle through filters if 'c' is hit
        if key == ord('c') or key == ord('C'):
            current_idx = (current_idx + 1) % len(filters)
            print(f" Swapped filter to: {filter_names[current_idx]}")
            
        # Trigger Booth session loop if Spacebar is hit
        elif key == ord(' '):
            captured_photos = []
            
            for photo_num in range(3):
                countdown = 3
                while countdown > 0:
                    start_time = time.time()
                    while time.time() - start_time < 1.0:
                        ret, frame = cap.read()
                        frame = cv2.flip(frame, 1)
                        live_view = active_recipe(frame)
                        
                        # Large countdown overlay text
                        cv2.putText(live_view, f"Get Ready! {photo_num+1}/3", (40, 200), 
                                    cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(live_view, str(countdown), (180, 320), 
                                    cv2.FONT_HERSHEY_DUPLEX, 3.0, (255, 255, 255), 5, cv2.LINE_AA)
                        
                        cv2.imshow("Vintage Camera Monitor", live_view)
                        cv2.waitKey(1)
                    countdown -= 1
                
                # Render hardware screen flash matrix simulation
                flash = np.full(frame.shape, 255, dtype=np.uint8)
                cv2.imshow("Vintage Camera Monitor", flash)
                cv2.waitKey(120)
                
                # Fetch fresh clean matrix, compute recipe, and register to strip collection
                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)
                final_capture = active_recipe(frame)
                captured_photos.append(final_capture)
            
            # Post Processing: Generate the Vertical Photostrip
            h, w, _ = captured_photos[0].shape
            border_px = 25
            bordered_photos = []
            
            for img in captured_photos:
                # Add vintage off-white cardstock paper margins
                bordered = cv2.copyMakeBorder(img, border_px, border_px, border_px, border_px, 
                                             cv2.BORDER_CONSTANT, value=[240, 242, 242])
                bordered_photos.append(bordered)
            
            # Concatenate images vertically to output full physical strip format
            photostrip = cv2.vconcat(bordered_photos)
            
            # Save file output to local workspace
            filename = f"strip_{filter_names[current_idx].replace(' ', '_')}_{int(time.time())}.jpg"
            cv2.imwrite(filename, photostrip)
            print(f"✨ Success! Saved: {filename} ✨")
            
            # Preview output strip render frame briefly on display layout
            cv2.imshow("Your Photostrip Output", cv2.resize(photostrip, (int(w/2), int(h*1.3))))
            cv2.waitKey(4000)
            cv2.destroyWindow("Your Photostrip Output")
            
        elif key == 27: # Key 27 corresponds to ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
