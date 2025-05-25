# Face Detection Application

A real-time face detection application that analyzes facial expressions and estimates age using OpenCV.

![Face Detection Demo](https://github.com/username/face-detection/raw/main/demo.png)

## Features

- Real-time face detection using webcam
- Facial expression recognition (neutral, smiling, winking, eyes closed)
- Eye detection
- Simple age estimation
- Available in both command-line, GUI, and web versions

## Versions

### Basic Version

Simple face detection with basic expression recognition.

### Enhanced Version

Advanced face detection with more accurate expression detection and age estimation.

### Web Version

Browser-based version using face-api.js that can be deployed to Netlify.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/username/face-detection.git
   cd face-detection
   ```

2. Install dependencies:
   ```
   pip install opencv-python pillow numpy
   ```

## Usage

### Basic Version

1. Command Line Version:
   ```
   python simple_face_detection.py
   ```
   Press 'q' to quit the application when running.

2. GUI Version:
   ```
   python simple_face_detection_gui.py
   ```
   Use the Start/Stop buttons to control the application.

### Enhanced Version

1. Command Line Version:
   ```
   python enhanced_face_detection.py
   ```
   Press 'q' to quit the application when running.

2. GUI Version:
   ```
   python enhanced_face_detection_gui.py
   ```
   Use the Start/Stop buttons and adjust detection parameters as needed.

### Web Version

1. Start the local server:
   ```
   npm start
   ```

2. Open your browser and navigate to http://localhost:5000

Note: The application now loads face-api.js models from a CDN, so no local model download is needed.

### Quick Start (Windows)

Run one of the batch files:
- `run_simple_app.bat` - For the basic version
- `run_enhanced_app.bat` - For the enhanced version

## Deploying to Netlify

1. Create a Netlify account at [netlify.com](https://www.netlify.com/)

2. Install Netlify CLI:
   ```
   npm install -g netlify-cli
   ```

3. Login to Netlify:
   ```
   netlify login
   ```

4. Deploy the site:
   ```
   netlify deploy --prod
   ```
   
   When prompted, specify the publish directory as `.` (current directory)

5. Alternatively, you can connect your GitHub repository to Netlify for automatic deployments.

## Requirements

- Python 3.7+ (for desktop versions)
- OpenCV
- Pillow (PIL)
- NumPy
- Webcam
- Node.js (for web version)

## How It Works

The application uses OpenCV's Haar Cascade classifiers for the desktop versions and face-api.js for the web version to detect faces, eyes, and expressions in real-time video frames.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 