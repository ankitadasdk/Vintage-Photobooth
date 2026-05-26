from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps
import io
import filters

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/filmstrip")
async def create_filmstrip(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    file3: UploadFile = File(...),
    filter_type: str = Form(...)
):
    # 1. Read all 3 uploaded images
    images = [
        Image.open(io.BytesIO(await file1.read())),
        Image.open(io.BytesIO(await file2.read())),
        Image.open(io.BytesIO(await file3.read()))
    ]
    
    processed_images = []
    
    # 2. Apply filters and resize them to be uniform (e.g., 400x300)
    target_size = (400, 300)
    for img in images:
        img_resized = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)
        
        if filter_type == "classic_mono":
            proc = filters.apply_monochrome(img_resized)
        elif filter_type == "warm_nostalgia":
            proc = filters.apply_warm_nostalgia(img_resized)
        elif filter_type == "disposable":
            proc = filters.apply_disposable(img_resized)
        else:
            proc = img_resized
            
        processed_images.append(proc)

    # 3. Design the vertical film strip layout
    margin = 20        # Outer borders and spacing between frames
    bottom_logo_space = 60 # Extra space at the bottom for that authentic look
    
    strip_width = target_size[0] + (margin * 2)
    strip_height = (target_size[1] * 3) + (margin * 4) + bottom_logo_space
    
    # Create a solid canvas (White or Black depending on your vibe, let's go with classic White)
    film_strip = Image.new("RGB", (strip_width, strip_height), color="white")
    
    # 4. Paste the images sequentially down the canvas
    current_y = margin
    for proc_img in processed_images:
        film_strip.paste(proc_img, (margin, current_y))
        current_y += target_size[1] + margin
        
    # 5. Convert the final combined strip to bytes
    img_byte_arr = io.BytesIO()
    film_strip.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")