import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import threading
import time

# Age ranges
AGE_RANGES = ['0-2', '4-6', '8-12', '15-20', '25-32', '38-43', '48-53', '60+']

class EnhancedFaceDetectionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Enhanced Face Detection App")
        self.window.geometry("900x700")
        
        # Configure the grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video frame
        self.video_frame = ttk.LabelFrame(self.main_frame, text="Video Feed", padding="10")
        self.video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Video label
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.grid(row=0, column=0)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Detection Results", padding="10")
        self.results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Results labels
        ttk.Label(self.results_frame, text="Expression:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.expression_var = tk.StringVar(value="Unknown")
        ttk.Label(self.results_frame, textvariable=self.expression_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.results_frame, text="Age:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.age_var = tk.StringVar(value="Unknown")
        ttk.Label(self.results_frame, textvariable=self.age_var, font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.results_frame, text="Faces Detected:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.faces_var = tk.StringVar(value="0")
        ttk.Label(self.results_frame, textvariable=self.faces_var, font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Detection settings
        settings_frame = ttk.LabelFrame(self.results_frame, text="Detection Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Scale factor
        ttk.Label(settings_frame, text="Scale Factor:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.scale_factor_var = tk.DoubleVar(value=1.1)
        scale_factor_slider = ttk.Scale(settings_frame, from_=1.05, to=1.5, variable=self.scale_factor_var, 
                                      orient=tk.HORIZONTAL, length=200)
        scale_factor_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(settings_frame, textvariable=self.scale_factor_var).grid(row=0, column=2, padx=5)
        
        # Min neighbors
        ttk.Label(settings_frame, text="Min Neighbors:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.min_neighbors_var = tk.IntVar(value=5)
        min_neighbors_slider = ttk.Scale(settings_frame, from_=1, to=10, variable=self.min_neighbors_var, 
                                      orient=tk.HORIZONTAL, length=200)
        min_neighbors_slider.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(settings_frame, textvariable=self.min_neighbors_var).grid(row=1, column=2, padx=5)
        
        # Control frame
        self.control_frame = ttk.Frame(self.main_frame, padding="10")
        self.control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_video)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_video, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Video capture variables
        self.cap = None
        self.is_running = False
        self.thread = None
        
        # Face detection variables
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        self.lefteye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lefteye_2splits.xml')
        self.righteye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_righteye_2splits.xml')
        
    def estimate_age(self, face_width, face_height):
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
        
    def start_video(self):
        if self.is_running:
            return
            
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            return
            
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running")
        
        # Start video thread
        self.is_running = True
        self.thread = threading.Thread(target=self.video_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_video(self):
        # Stop the video loop
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Release resources
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Stopped")
        self.video_label.config(image="")
        
    def video_loop(self):
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                if not ret:
                    self.status_var.set("Error: Failed to capture image")
                    break
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Convert to PhotoImage
                cv2image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the video label
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
                
                # Process at 30 fps
                time.sleep(0.033)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            if self.is_running:
                self.stop_video()
    
    def process_frame(self, frame):
        # Make a copy for drawing
        display_frame = frame.copy()
        
        # Convert to grayscale for cascade classifiers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get current detection settings
        scale_factor = self.scale_factor_var.get()
        min_neighbors = self.min_neighbors_var.get()
        
        # Detect faces using cascade classifier
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(30, 30)
        )
        
        # Update faces count
        self.faces_var.set(str(len(faces)))
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Get face region
            face_roi = frame[y:y+h, x:x+w]
            face_roi_gray = gray[y:y+h, x:x+w]
            
            # Detect smiles
            smiles = self.smile_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.7, minNeighbors=20)
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray)
            left_eyes = self.lefteye_cascade.detectMultiScale(face_roi_gray)
            right_eyes = self.righteye_cascade.detectMultiScale(face_roi_gray)
            
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
            
            # Update expression in UI
            self.expression_var.set(expression)
            
            # Estimate age based on face size
            age_text = self.estimate_age(w, h)
            
            # Update age in UI
            self.age_var.set(age_text)
            
            # Display expression and age on frame
            cv2.putText(display_frame, f"Expression: {expression}", (x, y-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Age: {age_text}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display count of faces detected
        cv2.putText(display_frame, f"Faces detected: {len(faces)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return display_frame
    
    def on_close(self):
        self.stop_video()
        self.window.destroy()

def main():
    # Create the main window
    root = tk.Tk()
    app = EnhancedFaceDetectionApp(root)
    
    # Set up close handler
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 