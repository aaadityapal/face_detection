// DOM Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const expressionResult = document.getElementById('expressionResult');
const ageResult = document.getElementById('ageResult');
const facesResult = document.getElementById('facesResult');
const scaleFactorSlider = document.getElementById('scaleFactor');
const scaleFactorValue = document.getElementById('scaleFactorValue');
const minNeighborsSlider = document.getElementById('minNeighbors');
const minNeighborsValue = document.getElementById('minNeighborsValue');

// Canvas context
const ctx = canvas.getContext('2d');

// Stream and detection variables
let stream = null;
let isRunning = false;
let detectionInterval = null;

// Settings
let detectionSettings = {
    scaleFactor: 1.1,
    minNeighbors: 5
};

// Update settings display
scaleFactorSlider.addEventListener('input', function() {
    detectionSettings.scaleFactor = parseFloat(this.value);
    scaleFactorValue.textContent = detectionSettings.scaleFactor.toFixed(2);
});

minNeighborsSlider.addEventListener('input', function() {
    detectionSettings.minNeighbors = parseInt(this.value);
    minNeighborsValue.textContent = detectionSettings.minNeighbors;
});

// Start camera
startButton.addEventListener('click', startCamera);
stopButton.addEventListener('click', stopCamera);

// Initialize face-api.js
async function initFaceAPI() {
    try {
        // Use CDN for models instead of local files
        const modelUrl = 'https://justadudewhohacks.github.io/face-api.js/models';
        await faceapi.nets.tinyFaceDetector.loadFromUri(modelUrl);
        await faceapi.nets.faceLandmark68Net.loadFromUri(modelUrl);
        await faceapi.nets.faceExpressionNet.loadFromUri(modelUrl);
        await faceapi.nets.ageGenderNet.loadFromUri(modelUrl);
        console.log('Face API models loaded from CDN');
    } catch (error) {
        console.error('Error loading Face API models:', error);
    }
}

// Start camera function
async function startCamera() {
    try {
        // Load models first
        await initFaceAPI();
        
        // Get camera stream
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        
        // Set video source
        video.srcObject = stream;
        
        // Update UI
        startButton.disabled = true;
        stopButton.disabled = false;
        isRunning = true;
        
        // Set canvas size after video metadata is loaded
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };
        
        // Start detection loop
        detectionInterval = setInterval(detectFaces, 100);
        
    } catch (error) {
        console.error('Error starting camera:', error);
        alert('Error accessing camera. Please make sure you have granted camera permissions.');
    }
}

// Stop camera function
function stopCamera() {
    if (stream) {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        
        // Clear detection interval
        clearInterval(detectionInterval);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update UI
        startButton.disabled = false;
        stopButton.disabled = true;
        isRunning = false;
        
        // Reset results
        expressionResult.textContent = 'Unknown';
        ageResult.textContent = 'Unknown';
        facesResult.textContent = '0';
    }
}

// Estimate age based on face size
function estimateAgeFromSize(faceWidth, faceHeight) {
    const faceSize = (faceWidth + faceHeight) / 2;
    
    if (faceSize < 100) {
        return "Child (0-12)";
    } else if (faceSize < 120) {
        return "Teen (13-19)";
    } else if (faceSize < 140) {
        return "Young Adult (20-35)";
    } else if (faceSize < 160) {
        return "Adult (36-50)";
    } else {
        return "Senior (50+)";
    }
}

// Detect faces function
async function detectFaces() {
    if (!isRunning) return;
    
    try {
        // Get detections
        const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceExpressions()
            .withAgeAndGender();
        
        // Clear previous drawings
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update faces count
        facesResult.textContent = detections.length.toString();
        
        // Process each detection
        detections.forEach(detection => {
            const { box } = detection.detection;
            
            // Draw face box
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 2;
            ctx.strokeRect(box.x, box.y, box.width, box.height);
            
            // Get dominant expression
            const expressions = detection.expressions;
            let dominantExpression = 'neutral';
            let maxScore = 0;
            
            for (const [expression, score] of Object.entries(expressions)) {
                if (score > maxScore) {
                    maxScore = score;
                    dominantExpression = expression;
                }
            }
            
            // Format expression text (capitalize first letter)
            const formattedExpression = dominantExpression.charAt(0).toUpperCase() + dominantExpression.slice(1);
            
            // Get age
            const age = Math.round(detection.age);
            const ageText = `${age} years`;
            
            // Update result displays
            expressionResult.textContent = formattedExpression;
            ageResult.textContent = ageText;
            
            // Draw text on canvas
            ctx.fillStyle = 'white';
            ctx.font = '14px Arial';
            ctx.fillText(`Expression: ${formattedExpression}`, box.x, box.y - 20);
            ctx.fillText(`Age: ${ageText}`, box.x, box.y - 5);
        });
        
    } catch (error) {
        console.error('Error in face detection:', error);
    }
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}); 