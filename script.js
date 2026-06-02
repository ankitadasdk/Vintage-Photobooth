const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startSessionBtn = document.getElementById('startSessionBtn');
const countdownOverlay = document.getElementById('countdown');
const crankWheel = document.getElementById('crankWheel');
const intervalLabel = document.getElementById('intervalLabel');

const thumbs = [
    document.getElementById('thumb1'),
    document.getElementById('thumb2'),
    document.getElementById('thumb3')
];

let capturedImages = []; 
let activeFilter = "fuji_acros"; 
let selectedInterval = 5;

// 1. Setup Mechanical Filter Buttons
document.querySelectorAll('.mech-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.mech-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        activeFilter = e.target.getAttribute('data-vibe');
    });
});

// 2. Setup Rotating Crank Wheel for Intervals
const intervals = [5, 7, 10];
let currentIntervalIdx = 0;
crankWheel.addEventListener('click', () => {
    currentIntervalIdx = (currentIntervalIdx + 1) % intervals.length;
    selectedInterval = intervals[currentIntervalIdx];
    const rotations = [0, 120, 240];
    crankWheel.style.transform = `rotate(${rotations[currentIntervalIdx]}deg)`;
    intervalLabel.innerText = `${selectedInterval} SECONDS`;
});

// 3. Mount Webcam Stream
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
        video.srcObject = stream;
    } catch (err) {
        console.error("Camera configuration failed:", err);
        alert("Please authorize camera connection!");
    }
}

const delay = ms => new Promise(res => setTimeout(res, ms));

// 4. Master Session Loop Pipeline
async function startPhotoboothSession() {
    startSessionBtn.disabled = true;
    capturedImages = []; 
    
    thumbs.forEach(thumb => {
        thumb.src = "";
    });

    for (let i = 0; i < 3; i++) {
        await runCountdown(selectedInterval);
        
        // Lens shutter execution visual flash
        video.style.opacity = 0;
        setTimeout(() => video.style.opacity = 1, 150);
        
        await captureFrameBrowser(i);
        startSessionBtn.innerText = `SHOT ${i+1}/3 COMPLETED`;
    }

    startSessionBtn.innerText = "PRINTING STRIP... 🎞️";
    await delay(600); 
    generateServerlessStrip();

    startSessionBtn.innerText = "click to take a snap !!";
    startSessionBtn.disabled = false;
}

async function runCountdown(seconds) {
    countdownOverlay.classList.add('active');
    for (let i = seconds; i > 0; i--) {
        countdownOverlay.innerText = i;
        await delay(1000);
    }
    countdownOverlay.classList.remove('active');
}

function captureFrameBrowser(index) {
    return new Promise((resolve) => {
        const context = canvas.getContext('2d');
        canvas.width = 640;
        canvas.height = 480;
        
        context.translate(canvas.width, 0);
        context.scale(-1, 1);
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        context.setTransform(1, 0, 0, 1, 0, 0); 
        
        applyAdvancedFilmEngine(context, 0, 0, canvas.width, canvas.height, activeFilter);
        
        const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
        
        const img = new Image();
        img.onload = () => {
            capturedImages.push(img);
            thumbs[index].src = dataUrl;
            resolve();
        };
        img.src = dataUrl;
    });
}


function applyAdvancedFilmEngine(ctx, x, y, width, height, filter) {
    const imgData = ctx.getImageData(x, y, width, height);
    const data = imgData.data;

    let grainIntensity = 0;
    let vignetteStrength = 0;

   
    if (filter === "mono_film") { grainIntensity = 55; vignetteStrength = 0.25; } 
    else if (filter === "fuji_acros") { grainIntensity = 8; vignetteStrength = 0.1; }
    else if (filter === "warm_nostalgia") { grainIntensity = 18; vignetteStrength = 0.3; }
    else if (filter === "retro_sepia") { grainIntensity = 20; vignetteStrength = 0.35; }
    else if (filter === "expired_slide") { grainIntensity = 25; vignetteStrength = 0.25; }
    else if (filter === "cinestill_800t") { grainIntensity = 24; vignetteStrength = 0.3; }

    const centerX = width / 2;
    const centerY = height / 2;
    const maxDistance = Math.sqrt(centerX * centerX + centerY * centerY);

    for (let i = 0; i < data.length; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        
        let lum = (r * 0.299 + g * 0.587 + b * 0.114);

        switch(filter) {
            case "fuji_acros": 
                
                r = Math.pow(lum / 255, 0.95) * 235 + 15;
                g = Math.pow(lum / 255, 0.95) * 230 + 10;
                b = Math.pow(lum / 255, 0.95) * 215 + 5;
                break;

            case "mono_film": 
                
                let normalized = lum / 255;
                let highContrastMono;
                
                if (normalized < 0.5) {
                    highContrastMono = Math.pow(normalized * 2, 1.4) * 0.5 * 255; 
                } else {
                    highContrastMono = (1 - Math.pow((1 - normalized) * 2, 1.4) * 0.5) * 255; 
                }
                
                
                r = g = b = highContrastMono * 0.9 + 10;
                break;

            case "cinestill_800t": 
                
                r = r * 1.15 + 10;
                g = g * 0.95;
                b = b * 0.85;

                if (lum < 110) {
                    let shadowFactor = (110 - lum) / 110; 
                    r -= 30 * shadowFactor;
                    g += 15 * shadowFactor;
                    b += 45 * shadowFactor;
                }

                if (lum > 195) {
                    r += 35;
                    g -= 15;
                    b -= 20;
                }
                break;

            case "warm_nostalgia": 
                r = (r * 0.95) + 30; g = (g * 0.85) + 15; b = (b * 0.65) + 5;
                break;

            case "retro_sepia": 
                let trueSepiaR = (r * 0.393) + (g * 0.769) + (b * 0.189);
                let trueSepiaG = (r * 0.349) + (g * 0.686) + (b * 0.168);
                let trueSepiaB = (r * 0.272) + (g * 0.534) + (b * 0.131);
                r = trueSepiaR; g = trueSepiaG; b = trueSepiaB;
                break;

            case "expired_slide": 
                r = r * 1.35; g = g * 0.75; b = (b * 1.5) - 30; 
                break;
        }

       
        if (vignetteStrength > 0) {
            const pixelIdx = i / 4;
            const px = pixelIdx % width;
            const py = Math.floor(pixelIdx / width);
            const dx = px - centerX;
            const dy = py - centerY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            const vignette = 1 - (distance / maxDistance) * vignetteStrength;
            r *= vignette; g *= vignette; b *= vignette;
        }

        
        if (grainIntensity > 0) {
            const noise = (Math.random() - 0.5) * grainIntensity;
            r += noise; g += noise; b += noise;
        }

        data[i]     = Math.min(255, Math.max(0, r));
        data[i + 1] = Math.min(255, Math.max(0, g));
        data[i + 2] = Math.min(255, Math.max(0, b));
    }

    ctx.putImageData(imgData, x, y);
}

function generateServerlessStrip() {
    if (capturedImages.length < 3) return;

    const frameW = 480;
    const frameH = 360;
    const borderPx = 30;
    const bottomMargin = 130;
    
    const canvasW = frameW + (borderPx * 2); 
    const canvasH = (frameH + (borderPx * 2)) * 3 + bottomMargin; 

    const finalCanvas = document.createElement('canvas');
    finalCanvas.width = canvasW;
    finalCanvas.height = canvasH;
    const ctx = finalCanvas.getContext('2d');

    ctx.fillStyle = "#f2eedf";
    ctx.fillRect(0, 0, canvasW, canvasH);

    for (let i = 0; i < 3; i++) {
        const currentY = i * (frameH + (borderPx * 2));
        ctx.drawImage(capturedImages[i], borderPx, currentY + borderPx, frameW, frameH);
    }

    ctx.fillStyle = "#32281e";
    ctx.font = "bold 26px 'Times New Roman', serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.letterSpacing = "2px";
    ctx.fillText("THE VINTAGE PHOTOBOOTH", canvasW / 2, canvasH - (bottomMargin / 2));

    const finalDataUrl = finalCanvas.toDataURL('image/jpeg', 0.95);
    const link = document.createElement('a');
    link.href = finalDataUrl;
    link.download = `vintage_printstrip_${activeFilter}_${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

startSessionBtn.addEventListener('click', startPhotoboothSession);
window.addEventListener('DOMContentLoaded', startWebcam);
