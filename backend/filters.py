import cv2
import numpy as np
from PIL import Image

def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Helper function to convert a PIL Image to OpenCV BGR format."""
    # Convert RGB (PIL default) to RGBA if needed, then to BGR
    img_rgb = pil_image.convert("RGB")
    img_np = np.array(img_rgb)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_bgr

def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Helper function to convert an OpenCV BGR image back to PIL RGB."""
    img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

# -------------------------------------------------------------------------
# VINTAGE FILTER RECIPES
# -------------------------------------------------------------------------

def apply_monochrome(input_pil: Image.Image) -> Image.Image:
    """Applies a high-contrast, dramatic retro black & white film look."""
    # 1. Convert to OpenCV
    img = pil_to_cv2(input_pil)
    
    # 2. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Boost contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    high_contrast = clahe.apply(gray)
    
    # 4. Add a subtle film grain noise
    noise = np.zeros(high_contrast.shape, dtype=np.int16)
    cv2.randn(noise, 0, 15)  # Gaussian noise
    grained = cv2.add(high_contrast.astype(np.int16), noise)
    grained = np.clip(grained, 0, 255).astype(np.uint8)
    
    # 5. Convert back to BGR format so our helper can read it
    result_cv2 = cv2.cvtColor(grained, cv2.COLOR_GRAY2BGR)
    
    return cv2_to_pil(result_cv2)


def apply_warm_nostalgia(input_pil: Image.Image) -> Image.Image:
    """Applies a warm, faded golden-hour tint reminiscent of old polaroids."""
    img = pil_to_cv2(input_pil)
    
    # Split channels to manipulate tones
    b, g, r = cv2.split(img)
    
    # Boost reds and yellows (warmth) and pull back blues
    # Using look-up tables or simple scaling
    r = cv2.addWeighted(r, 1.1, np.zeros(r.shape, dtype=r.dtype), 0, 10)
    g = cv2.addWeighted(g, 1.05, np.zeros(g.shape, dtype=g.dtype), 0, 5)
    b = cv2.addWeighted(b, 0.85, np.zeros(b.shape, dtype=b.dtype), 0, 0)
    
    warmed = cv2.merge((b, g, r))
    
    # Add a slight vintage vignette (darkened edges)
    rows, cols = warmed.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols/2)
    kernel_y = cv2.getGaussianKernel(rows, rows/2)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = np.zeros_like(warmed)
    
    for i in range(3):
        vignette[:, :, i] = warmed[:, :, i] * (mask / np.max(mask))
        
    # Blend the vignette slightly with the original warmed image so it's not too harsh
    result_cv2 = cv2.addWeighted(warmed, 0.4, vignette, 0.6, 0)
    
    return cv2_to_pil(result_cv2)


def apply_disposable(input_pil: Image.Image) -> Image.Image:
    """Simulates a cheap 90s disposable camera with slight color shifts and low dynamic range."""
    img = pil_to_cv2(input_pil)
    
    # 1. Raise the black levels slightly to get that "faded/washed out" look
    # We map 0-255 to 20-255
    lut = np.array([max(20, i) for i in range(256)]).astype("uint8")
    img_faded = cv2.LUT(img, lut)
    
    # 2. Add a slight chromatic aberration / color shift vibe
    b, g, r = cv2.split(img_faded)
    
    # Shift the red channel by a few pixels to simulate low-quality lenses
    rows, cols = r.shape
    M = np.float32([[1, 0, 3], [0, 1, 3]])  # shift 3 pixels right and down
    r_shifted = cv2.warpAffine(r, M, (cols, rows))
    
    result_cv2 = cv2.merge((b, g, r_shifted))
    
    # 3. Add heavy color saturation boost
    hsv = cv2.cvtColor(result_cv2, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 30) # Boost saturation
    hsv_boosted = cv2.merge((h, s, v))
    result_cv2 = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2BGR)
    
    return cv2_to_pil(result_cv2)