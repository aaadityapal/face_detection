# Face Detection Application

A real-time face detection application that analyzes facial expressions and estimates age using OpenCV.

![Face Detection Demo](https://github.com/username/face-detection/raw/main/demo.png)

## Features

- Real-time face detection using webcam
- Facial expression recognition (neutral, smiling, winking, eyes closed)
- Eye detection
- Simple age estimation
- Available in both command-line and GUI versions

## Versions

### Basic Version

Simple face detection with basic expression recognition.

### Enhanced Version

Advanced face detection with more accurate expression detection and age estimation.

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

### Quick Start (Windows)

Run one of the batch files:
- `run_simple_app.bat` - For the basic version
- `run_enhanced_app.bat` - For the enhanced version

## Requirements

- Python 3.7+
- OpenCV
- Pillow (PIL)
- NumPy
- Webcam

## How It Works

The application uses OpenCV's Haar Cascade classifiers to detect faces, eyes, and smiles in real-time video frames. The enhanced version includes:

1. Face detection using Haar Cascade classifier
2. Eye detection for determining if eyes are open, closed, or winking
3. Smile detection for expression recognition
4. Age estimation based on face size (a simple heuristic approach)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 