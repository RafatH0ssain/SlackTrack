import pygame
import time
import cv2
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pygetwindow as gw
import threading  # Import threading for background tasks

# Initialize pygame mixer for sound
pygame.mixer.init()

# Function to play the preview of the selected beep sound
def play_preview_beep():
    beep_file = selected_beep.get()  # Get the selected beep file from the dropdown
    beep_sound = pygame.mixer.Sound(f'sounds/{beep_file}')  # Load the beep sound
    beep_sound.play()  # Play the beep sound once

# Function to launch camera with selected time settings
def launch_camera():
    try:
        # Get values from user input
        # blink_threshold = int(blink_threshold_entry.get())
        look_away_threshold = int(look_away_threshold_entry.get())
        selected_beep_sound = selected_beep.get()  # Get the selected beep sound
        
        # Initialize camera
        cap = cv2.VideoCapture(0)

        # Load Haar Cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        # Timer variables
        # last_blink_time = time.time()
        look_away_time = time.time()
        last_look_away_beep_time = time.time()  # To track when the beep was last played for look away

        # Load the selected beep sound for the camera
        beep_sound = pygame.mixer.Sound(f'sounds/{selected_beep_sound}')

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
                    if time.time() - last_look_away_beep_time > 1:
                        beep_sound.play()
                        last_look_away_beep_time = time.time()
            else:
                # If eyes are detected, reset look away timer
                look_away_time = time.time()

            # Video feed
            cv2.imshow("Camera", frame)

            # Wait for the 'Esc' key to exit
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

# Function to track window switches
def track_window_switch():
    decision = int(window_changed_beep.get())
    selected_beep_sound = selected_beep.get()
    last_window = None  # Store the last active window's title
    beep_sound = pygame.mixer.Sound(f'sounds/{selected_beep_sound}')

    while decision:
        # Get the title of the current active window
        current_window = gw.getActiveWindow()

        # If there's an active window
        if current_window:
            current_window_title = current_window.title

            # If the active window is different from the last one
            if current_window_title != last_window:
                beep_sound.play()
                last_window = current_window_title

        # Sleep for a short time before checking again
        time.sleep(0.5)

# Create the Tkinter window
root = tk.Tk()
root.title("SlackTrack")

# tk.Label(root, text="Blink Threshold (Under Development):").grid(row=0, column=0, padx=10, pady=10)
# blink_threshold_entry = tk.Entry(root)
# blink_threshold_entry.grid(row=0, column=1, padx=10, pady=10)
# blink_threshold_entry.insert(0, "∞")


# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Look Away Threshold (seconds):").grid(row=0, column=0, padx=10, pady=10)
look_away_threshold_entry = tk.Entry(root)
look_away_threshold_entry.grid(row=0, column=1, padx=10, pady=10)
look_away_threshold_entry.insert(0, "10")

# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Beep If Window Changed (0/1):").grid(row=1, column=0, padx=10, pady=10)
window_changed_beep = tk.Entry(root)
window_changed_beep.grid(row=1, column=1, padx=10, pady=10)
window_changed_beep.insert(0, "0")

# Label and ComboBox for beep selection
tk.Label(root, text="Select Beep Sound:").grid(row=2, column=0, padx=10, pady=10)
beep_options = ["beep01.wav", "beep02.wav", "beep03.wav", "beep04.wav", "beep05.wav", "beep06.wav", "beep07.wav"]
selected_beep = ttk.Combobox(root, values=beep_options, state="readonly")
selected_beep.grid(row=2, column=1, padx=10, pady=10)
selected_beep.set(beep_options[0])  # Default value

# Button to play the selected beep sound as a preview
play_button = tk.Button(root, text="Play Preview", command=play_preview_beep)
play_button.grid(row=2, column=2, pady=10, padx=10)

# Button to launch the camera
launch_button = tk.Button(root, text="Launch Camera", command=launch_camera)
launch_button.grid(row=3, columnspan=2, pady=20)

# Start window tracking in a separate thread
def start_window_tracking():
    tracking_thread = threading.Thread(target=track_window_switch, daemon=True)
    tracking_thread.start()

# Start the window tracking as a background thread when the app starts
start_window_tracking()

# Run the Tkinter main loop
root.mainloop()