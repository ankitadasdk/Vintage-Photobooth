import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ==========================================
# 🎞️ THE FUJI & VINTAGE FILM RECIPES 🎞️
# ==========================================

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
    # Pure soft glam look
    smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    flat_gray = cv2.convertScaleAbs(gray, alpha=0.6, beta=60)
    gray_3ch = cv2.cvtColor(flat_gray, cv2.COLOR_GRAY2BGR)
    
    warm_overlay = np.full(gray_3ch.shape, (20, 35, 50), dtype=np.uint8)
    tinted = cv2.addWeighted(gray_3ch, 0.85, warm_overlay, 0.25, 0)
    
    blur = cv2.GaussianBlur(tinted, (15, 15), 0)
    return cv2.addWeighted(tinted, 0.75, blur, 0.25, 0)

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
# 🛠️ STRIP GENERATOR 🛠️
# ==========================================

def generate_proper_strip(photos):
    paper_color = [245, 245, 242] 
    border_px = 30
    bottom_margin = 120 

    bordered_photos = []
    for img in photos:
        bordered = cv2.copyMakeBorder(img, border_px, border_px, border_px, border_px, cv2.BORDER_CONSTANT, value=paper_color)
        bordered_photos.append(bordered)
    
    photostrip = cv2.vconcat(bordered_photos)
    photostrip = cv2.copyMakeBorder(photostrip, 0, bottom_margin, 0, 0, cv2.BORDER_CONSTANT, value=paper_color)
    
    text = "ANALOG BOOTH"
    font = cv2.FONT_HERSHEY_DUPLEX
    text_size = cv2.getTextSize(text, font, 1.2, 2)[0]
    text_x = (photostrip.shape[1] - text_size[0]) // 2
    text_y = photostrip.shape[0] - 45
    cv2.putText(photostrip, text, (text_x, text_y), font, 1.2, (40, 40, 40), 2, cv2.LINE_AA)

    return photostrip

# ==========================================
# 💻 STREAMLIT WEB APP UI 💻
# ==========================================

st.set_page_config(page_title="Analog Engine", layout="centered", initial_sidebar_state="expanded")

# Setup safe state containers
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'last_processed_id' not in st.session_state:
    st.session_state.last_processed_id = None

st.title("🎞️ ANALOG ENGINE")
st.markdown("*digital film lab.*")

# Sidebar mapping all 5 filters
with st.sidebar:
    st.header("Film Roll")
    
    filter_choice = st.radio(
        "Select your aesthetic:", 
        ["Classic Chrome", "Superia Warm", "Fuji ACROS B&W", "1970s Sepia", "Expired Slide"]
    )
    
    st.divider()
    st.write(f"**Photos captured:** {len(st.session_state.photos)} / 3")
    
    if st.button("🗑️ Reset Booth"):
        st.session_state.photos = []
        st.session_state.last_processed_id = None
        st.rerun()

filter_map = {
    "Classic Chrome": recipe_fuji_chrome,
    "Superia Warm": recipe_warm_vintage,
    "Fuji ACROS B&W": recipe_acros_bw,
    "1970s Sepia": recipe_retro_sepia,
    "Expired Slide": recipe_expired_slide
}
active_recipe = filter_map[filter_choice]

# App Layout
if len(st.session_state.photos) < 3:
    current_count = len(st.session_state.photos)
    st.write(f"### Snap Poses to Print! (Current Step: {current_count + 1}/3)")
    
    camera_image = st.camera_input(key=f"cam_input_{current_count}", label=f"Capture Pose {current_count + 1}")
    
    if camera_image is not None:
        # Use image ID to prevent double processing triggers loops
        img_id = camera_image.id
        if st.session_state.last_processed_id != img_id:
            image = Image.open(camera_image)
            img_array = np.array(image)
            cv2_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # IMMEDIATELY apply and save the processed image state
            processed_img = active_recipe(cv2_img)
            st.session_state.photos.append(processed_img)
            st.session_state.last_processed_id = img_id
            st.rerun()

    # Darkroom display area
    if len(st.session_state.photos) > 0:
        st.divider()
        st.markdown(f"### 🎞️ Developed Frames (Using: {filter_choice})")
        cols = st.columns(3)
        for idx, img in enumerate(st.session_state.photos):
            with cols[idx]:
                display_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                st.image(display_img, use_container_width=True, caption=f"Frame {idx+1}")

else:
    st.success("Film fully developed! Vibes are immaculate.")
    
    with st.spinner("Assembling your physical photostrip..."):
        final_strip_bgr = generate_proper_strip(st.session_state.photos)
        final_strip_rgb = cv2.cvtColor(final_strip_bgr, cv2.COLOR_BGR2RGB)
        
        st.image(final_strip_rgb, caption="Your Analog Strip Preview", use_container_width=True)
        
        pil_strip = Image.fromarray(final_strip_rgb)
        buf = io.BytesIO()
        pil_strip.save(buf, format="JPEG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 DOWNLOAD STRIP",
            data=byte_im,
            file_name=f"analog_strip_{filter_choice.replace(' ', '_')}.jpg",
            mime="image/jpeg",
            type="primary"
        )