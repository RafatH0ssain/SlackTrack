import pygame
import time
import cv2
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Initialize pygame mixer for sound
pygame.mixer.init()

# Load the beep sound (make sure to have a .wav or .ogg file)
beep_sound = pygame.mixer.Sound('sounds/beep.wav')

# Function to launch camera with selected time settings
def launch_camera():
    try:
        # Get values from user input
        blink_threshold = int(blink_threshold_entry.get())
        look_away_threshold = int(look_away_threshold_entry.get())

        # Initialize camera
        cap = cv2.VideoCapture(0)

        # Load Haar Cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        # Timer variables
        last_blink_time = time.time()
        look_away_time = time.time()
        last_look_away_beep_time = time.time()  # To track when the beep was last played for look away

        # Camera loop
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Check if eyes are closed or person is looking away
            eyes_detected = False

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)

                # Draw rectangle around face and eyes
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue for face
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)  # Green for eyes
                    eyes_detected = True

            if not eyes_detected:
                # If eyes are not detected (look away or closed)
                if time.time() - look_away_time > look_away_threshold:
                    if time.time() - last_look_away_beep_time > 1:  # To avoid multiple beeps in a short period
                        beep_sound.play()  # Play the beep sound
                        last_look_away_beep_time = time.time()  # Update beep time to prevent repeated beeping
            else:
                # If eyes are detected, reset look away timer
                look_away_time = time.time()

            # Display the video feed
            cv2.imshow("Camera", frame)

            # Wait for the 'Esc' key to exit, or handle window close event
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # 'Esc' key to exit
                break

            # Check if the window was closed
            if cv2.getWindowProperty('Camera', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the Tkinter window
root = tk.Tk()
root.title("Camera Monitoring App")

# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Blink Threshold (seconds):").grid(row=0, column=0, padx=10, pady=10)
blink_threshold_entry = tk.Entry(root)
blink_threshold_entry.grid(row=0, column=1, padx=10, pady=10)
blink_threshold_entry.insert(0, "5")  # Default value

tk.Label(root, text="Look Away Threshold (seconds):").grid(row=1, column=0, padx=10, pady=10)
look_away_threshold_entry = tk.Entry(root)
look_away_threshold_entry.grid(row=1, column=1, padx=10, pady=10)
look_away_threshold_entry.insert(0, "10")  # Default value

# Button to launch the camera
launch_button = tk.Button(root, text="Launch Camera", command=launch_camera)
launch_button.grid(row=2, columnspan=2, pady=20)

# Run the GUI loop
root.mainloop()