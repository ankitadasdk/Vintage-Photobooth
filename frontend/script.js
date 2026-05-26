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

const backendUrl = "http://127.0.0.1:8000/filmstrip"; 
let capturedBlobs = []; 
let activeFilter = "classic_mono"; 
let selectedInterval = 5;

// 1. Setup Mechanical Filter Buttons
document.querySelectorAll('.mech-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.mech-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        activeFilter = e.target.getAttribute('data-vibe');
    });
});

// 2. Setup Rotating Crank Wheel for Intervals (Cycles 5s -> 7s -> 10s)
const intervals = [5, 7, 10];
let currentIntervalIdx = 0;
crankWheel.addEventListener('click', () => {
    currentIntervalIdx = (currentIntervalIdx + 1) % intervals.length;
    selectedInterval = intervals[currentIntervalIdx];
    
    // Rotate mechanical wheel visually based on setting
    const rotations = [0, 120, 240];
    crankWheel.style.transform = `rotate(${rotations[currentIntervalIdx]}deg)`;
    intervalLabel.innerText = `${selectedInterval} SECONDS`;
});

// 3. Mount Webcam Stream
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = stream;
    } catch (err) {
        console.error("Camera layout configuration failed:", err);
    }
}

const delay = ms => new Promise(res => setTimeout(res, ms));

// 4. Session Loop Pipeline
async function startPhotoboothSession() {
    startSessionBtn.disabled = true;
    capturedBlobs = []; 
    
    thumbs.forEach(thumb => {
        thumb.src = "";
        thumb.style.filter = "none";
    });

    for (let i = 0; i < 3; i++) {
        await runCountdown(selectedInterval);
        
        // Lens shutter execution visual flash
        video.style.opacity = 0;
        setTimeout(() => video.style.opacity = 1, 150);
        
        startSessionBtn.innerText = `SHOT ${i+1}/3 COMPLETED`;
        await captureFrameLocal();
    }

    startSessionBtn.innerText = "PRINTING STRIP... 🎞️";
    await compileAndDownloadStrip();

    startSessionBtn.innerText = "ENGAGE MACHINE ⚡";
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

function captureFrameLocal() {
    return new Promise((resolve) => {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
            if (blob) {
                capturedBlobs.push(blob);
                const currentThumb = thumbs[capturedBlobs.length - 1];
                currentThumb.src = URL.createObjectURL(blob);
                
                // Keep the live dashboard filter preview matches
                applyInstantCssFilter(currentThumb, activeFilter);
            }
            resolve();
        }, 'image/jpeg');
    });
}

function applyInstantCssFilter(element, filter) {
    element.style.filter = "none";
    if (filter === "classic_mono") {
        element.style.filter = "grayscale(100%) contrast(130%) sepia(20%)";
    } else if (filter === "warm_nostalgia") {
        element.style.filter = "sepia(60%) saturate(120%) brightness(102%)";
    } else if (filter === "disposable") {
        element.style.filter = "saturate(160%) contrast(110%) brightness(98%)";
    }
}

async function compileAndDownloadStrip() {
    if (capturedBlobs.length < 3) return;

    const formData = new FormData();
    formData.append("file1", capturedBlobs[0], "shot1.jpg");
    formData.append("file2", capturedBlobs[1], "shot2.jpg");
    formData.append("file3", capturedBlobs[2], "shot3.jpg");
    formData.append("filter_type", activeFilter);

    try {
        const response = await fetch(backendUrl, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("API Execution error");

        const stripBlob = await response.blob();
        triggerLocalDownload(stripBlob, `vintage_printstrip_${Date.now()}.jpg`);

    } catch (error) {
        console.error("Machine malfunction:", error);
        alert("Stitching mechanism failed.");
    }
}

function triggerLocalDownload(blob, filename) {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

startSessionBtn.addEventListener('click', startPhotoboothSession);
window.addEventListener('DOMContentLoaded', startWebcam);