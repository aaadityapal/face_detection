import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import time
import os

class FaceDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("900x700")
        self.window.configure(bg="#f0f0f0")
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        
        # Initialize variables
        self.cap = None
        self.is_webcam_active = False
        self.processing_thread = None
        self.stop_event = threading.Event()
        
        # Create GUI elements
        self.create_widgets()
        
        # Set window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # Create frames
        self.control_frame = ttk.Frame(self.window, padding=10)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.video_frame = ttk.Frame(self.window, padding=10)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create buttons
        self.webcam_btn = ttk.Button(self.control_frame, text="Start Webcam", command=self.toggle_webcam)
        self.webcam_btn.pack(side=tk.LEFT, padx=5)
        
        self.image_btn = ttk.Button(self.control_frame, text="Open Image", command=self.open_image)
        self.image_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(self.control_frame, text="Save Image", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn.config(state=tk.DISABLED)
        
        # Create video display
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a black canvas initially
        black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        self.display_image(black_img)
    
    def toggle_webcam(self):
        if self.is_webcam_active:
            # Stop webcam
            self.stop_event.set()
            if self.processing_thread:
                self.processing_thread.join()
            if self.cap:
                self.cap.release()
            self.cap = None
            self.is_webcam_active = False
            self.webcam_btn.config(text="Start Webcam")
            self.status_var.set("Webcam stopped")
            self.save_btn.config(state=tk.DISABLED)
        else:
            # Start webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_var.set("Error: Could not open webcam")
                return
            
            self.is_webcam_active = True
            self.webcam_btn.config(text="Stop Webcam")
            self.status_var.set("Webcam started")
            self.save_btn.config(state=tk.NORMAL)
            
            # Reset stop event
            self.stop_event.clear()
            
            # Start processing in a separate thread
            self.processing_thread = threading.Thread(target=self.process_webcam)
            self.processing_thread.daemon = True
            self.processing_thread.start()
    
    def process_webcam(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                self.status_var.set("Error: Failed to capture image")
                break
            
            # Process the frame
            processed_frame = self.detect_faces(frame)
            
            # Display the frame
            self.display_image(processed_frame)
            
            # Small delay to reduce CPU usage
            time.sleep(0.01)
    
    def detect_faces(self, frame):
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image with MediaPipe Face Detection
        results = self.face_detection.process(rgb_frame)
        
        # Draw face detections
        if results.detections:
            for detection in results.detections:
                # Draw the face detection box
                self.mp_drawing.draw_detection(frame, detection)
                
                # Get bounding box coordinates
                bbox = detection.location_data.relative_bounding_box
                h, w, c = frame.shape
                x, y, width, height = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                
                # Display confidence score
                confidence = round(detection.score[0] * 100, 1)
                cv2.putText(frame, f"Confidence: {confidence}%", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def open_image(self):
        # Stop webcam if active
        if self.is_webcam_active:
            self.toggle_webcam()
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Read and process the image
            image = cv2.imread(file_path)
            if image is not None:
                processed_image = self.detect_faces(image)
                self.display_image(processed_image)
                self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
                self.save_btn.config(state=tk.NORMAL)
                self.current_image = processed_image
            else:
                self.status_var.set("Error: Could not open image")
    
    def save_image(self):
        if hasattr(self, 'current_image') or self.is_webcam_active:
            # Get current image
            if self.is_webcam_active:
                ret, frame = self.cap.read()
                if not ret:
                    self.status_var.set("Error: Failed to capture image")
                    return
                self.current_image = self.detect_faces(frame)
            
            # Open save file dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                # Save the image
                cv2.imwrite(file_path, self.current_image)
                self.status_var.set(f"Image saved: {os.path.basename(file_path)}")
    
    def display_image(self, image):
        # Convert to RGB for display
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # Resize to fit the window
        w, h = pil_image.size
        max_w = self.video_frame.winfo_width() - 20
        max_h = self.video_frame.winfo_height() - 20
        
        if max_w > 0 and max_h > 0:  # Ensure window is initialized
            # Calculate scaling factor to fit within the frame
            scale = min(max_w / w, max_h / h)
            new_size = (int(w * scale), int(h * scale))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(image=pil_image)
        
        # Update the label
        self.video_label.config(image=self.photo)
        self.video_label.image = self.photo  # Keep a reference
    
    def on_closing(self):
        # Stop webcam if active
        if self.is_webcam_active:
            self.stop_event.set()
            if self.processing_thread:
                self.processing_thread.join()
            if self.cap:
                self.cap.release()
        
        # Close window
        self.window.destroy()

def main():
    # Create main window
    root = tk.Tk()
    app = FaceDetectionApp(root, "Face Detection App")
    root.mainloop()

if __name__ == "__main__":
    main() 