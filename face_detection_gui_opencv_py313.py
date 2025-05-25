import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize variables
        self.cap = None
        self.is_webcam_active = False
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.current_image = None
        
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
        self.webcam_btn = ttk.Button(self.control_frame, text="Try Webcam", command=self.toggle_webcam)
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
        self.status_var.set("Ready - Please open an image file to detect faces")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a black canvas initially
        black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(black_img, "Please open an image file to detect faces", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
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
            self.webcam_btn.config(text="Try Webcam")
            self.status_var.set("Webcam stopped")
            self.save_btn.config(state=tk.DISABLED)
        else:
            try:
                # Start webcam
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    messagebox.showerror("Webcam Error", "Could not open webcam. Please check your camera permissions or try using image files instead.")
                    self.status_var.set("Error: Could not open webcam. Try using image files.")
                    return
                
                # Try to read a frame to verify webcam works
                ret, frame = self.cap.read()
                if not ret:
                    messagebox.showerror("Webcam Error", "Failed to capture image from webcam. Please try using image files instead.")
                    self.status_var.set("Error: Failed to capture image from webcam")
                    self.cap.release()
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
            except Exception as e:
                messagebox.showerror("Webcam Error", f"Error accessing webcam: {str(e)}\nPlease try using image files instead.")
                self.status_var.set("Error accessing webcam. Try using image files.")
    
    def process_webcam(self):
        frame_count = 0
        error_count = 0
        max_errors = 5
        
        while not self.stop_event.is_set():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    error_count += 1
                    if error_count >= max_errors:
                        self.status_var.set("Too many webcam errors. Stopping webcam.")
                        self.window.after(0, self.toggle_webcam)  # Stop webcam from main thread
                        break
                    time.sleep(0.1)
                    continue
                
                # Reset error count on successful frame
                error_count = 0
                frame_count += 1
                
                # Process every other frame to reduce CPU load
                if frame_count % 2 == 0:
                    # Process the frame
                    processed_frame = self.detect_faces(frame)
                    
                    # Display the frame
                    self.display_image(processed_frame)
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
            except Exception as e:
                self.status_var.set(f"Error processing webcam frame: {str(e)}")
                time.sleep(0.1)
    
    def detect_faces(self, frame):
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Process each face
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Display face label
                cv2.putText(frame, f"Face detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display the total face count
            cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return frame
        except Exception as e:
            self.status_var.set(f"Error detecting faces: {str(e)}")
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
            try:
                # Read and process the image
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("Error", f"Could not open image file: {file_path}")
                    self.status_var.set("Error: Could not open image")
                    return
                    
                processed_image = self.detect_faces(image)
                self.display_image(processed_image)
                self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
                self.save_btn.config(state=tk.NORMAL)
                self.current_image = processed_image
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
                self.status_var.set(f"Error processing image: {str(e)}")
    
    def save_image(self):
        if self.current_image is not None:
            # Open save file dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                try:
                    # Save the image
                    cv2.imwrite(file_path, self.current_image)
                    self.status_var.set(f"Image saved: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error saving image: {str(e)}")
                    self.status_var.set(f"Error saving image: {str(e)}")
    
    def display_image(self, image):
        try:
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
        except Exception as e:
            self.status_var.set(f"Error displaying image: {str(e)}")
    
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