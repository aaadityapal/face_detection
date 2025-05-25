import cv2
import numpy as np
import os
import time

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Check if webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Load face detection model
    print("Loading face detection models...")
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load smile detection
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    # Load eye detection
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    # Additional cascades for more expression detection
    lefteye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lefteye_2splits.xml')
    righteye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_righteye_2splits.xml')
    
    print("Enhanced Face Detection App Started. Press 'q' to quit.")
    
    # For age estimation (simple heuristic based on face size)
    def estimate_age(face_width, face_height):
        face_size = (face_width + face_height) / 2
        
        # Very simple heuristic based on face size
        # This is not accurate but gives a rough estimate
        if face_size < 100:
            return "Child (0-12)"
        elif face_size < 120:
            return "Teen (13-19)"
        elif face_size < 140:
            return "Young Adult (20-35)"
        elif face_size < 160:
            return "Adult (36-50)"
        else:
            return "Senior (50+)"
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Make a copy for drawing
        display_frame = frame.copy()
        
        # Convert to grayscale for cascade classifiers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using cascade classifier
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Get face region
            face_roi = frame[y:y+h, x:x+w]
            face_roi_gray = gray[y:y+h, x:x+w]
            
            # Detect smiles
            smiles = smile_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.7, minNeighbors=20)
            
            # Detect eyes
            eyes = eye_cascade.detectMultiScale(face_roi_gray)
            left_eyes = lefteye_cascade.detectMultiScale(face_roi_gray)
            right_eyes = righteye_cascade.detectMultiScale(face_roi_gray)
            
            # Draw rectangles around eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(display_frame[y:y+h, x:x+w], (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Determine expression
            expression = "Neutral"
            if len(smiles) > 0:
                expression = "Smiling"
            
            # Check if eyes are detected
            if len(eyes) > 0 or len(left_eyes) > 0 or len(right_eyes) > 0:
                if len(eyes) == 0:
                    expression = "Winking"
            else:
                expression = "Eyes Closed"
            
            # Estimate age based on face size
            age_text = estimate_age(w, h)
            
            # Display expression and age
            cv2.putText(display_frame, f"Expression: {expression}", (x, y-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Age: {age_text}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display count of faces detected
        cv2.putText(display_frame, f"Faces detected: {len(faces)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display the resulting frame
        cv2.imshow('Enhanced Face Detection', display_frame)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 