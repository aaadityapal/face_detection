import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time

class SimpleFaceDetectionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Simple Face Detection App")
        self.window.geometry("800x600")
        
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
        
        ttk.Label(self.results_frame, text="Faces Detected:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.faces_var = tk.StringVar(value="0")
        ttk.Label(self.results_frame, textvariable=self.faces_var, font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2)
        
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
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Update faces count
        self.faces_var.set(str(len(faces)))
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Get region of interest for face
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Detect smiles
            smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=20)
            
            # Determine expression
            expression = "Neutral"
            if len(smiles) > 0:
                expression = "Smiling"
            
            # Update expression
            self.expression_var.set(expression)
            
            # Display expression on frame
            cv2.putText(frame, f"Expression: {expression}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display count of faces detected
        cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def on_close(self):
        self.stop_video()
        self.window.destroy()

def main():
    # Create the main window
    root = tk.Tk()
    app = SimpleFaceDetectionApp(root)
    
    # Set up close handler
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 