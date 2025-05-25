import cv2
import numpy as np
from deepface import DeepFace
import time

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Check if webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Face cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Frame processing rate limiter for DeepFace analysis (once per second)
    last_analysis_time = 0
    analysis_interval = 1.0  # seconds
    
    # Variables to store analysis results
    emotion = "Unknown"
    age = "Unknown"
    
    print("Face Detection App Started. Press 'q' to quit.")
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Current time for analysis rate limiting
        current_time = time.time()
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Perform DeepFace analysis once per second when faces are detected
            if current_time - last_analysis_time > analysis_interval:
                try:
                    # Get face region
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Analyze emotion
                    emotion_analysis = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
                    emotion = emotion_analysis[0]['dominant_emotion']
                    
                    # Analyze age
                    age_analysis = DeepFace.analyze(face_img, actions=['age'], enforce_detection=False)
                    age = age_analysis[0]['age']
                    
                    last_analysis_time = current_time
                except Exception as e:
                    print(f"Analysis error: {e}")
            
            # Display emotion and age
            cv2.putText(frame, f"Emotion: {emotion}", (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Age: {age}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the resulting frame
        cv2.imshow('Face Detection', frame)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 