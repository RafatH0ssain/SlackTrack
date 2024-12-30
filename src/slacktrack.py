import pygame
import time
import cv2
import tkinter as tk
from tkinter import messagebox, ttk

import pygetwindow as gw
import threading  # Import threading for background tasks
import os
import sys
import pygame

# Initialize pygame mixer for sound
pygame.mixer.init()

# Function to get the correct path to the beep sound
def get_sound_path(beep_file):
    if getattr(sys, 'frozen', False):  # Check if running as a bundled executable
        # If frozen (packaged executable), use the path from _MEIPASS
        return os.path.join(sys._MEIPASS, 'sounds', beep_file)
    else:
        # If not frozen (running as a script), use the local path
        return os.path.join('sounds', beep_file)

# Example function to play a beep sound
def play_beep_sound(beep_file):
    beep_path = get_sound_path(beep_file)
    beep_sound = pygame.mixer.Sound(beep_path)
    beep_sound.play()

# Initialize pygame mixer for sound
pygame.mixer.init()

# Global variable to control window tracking
window_tracking_active = False

# Function to play the preview of the selected beep sound
def play_preview_beep():
    beep_file = selected_beep.get()  # Get the selected beep file from the dropdown
    beep_sound = pygame.mixer.Sound(f'sounds/{beep_file}')  # Load the beep sound
    beep_sound.play()  # Play the beep sound once

# Function to launch camera with selected time settings
def get_cascade_path(cascade_file):
    if getattr(sys, 'frozen', False):  # Check if running as a bundled executable
        return os.path.join(sys._MEIPASS, cascade_file)
    else:
        return os.path.join('src', cascade_file)

def launch_camera():
    try:
        # Get values from user input
        look_away_threshold = int(look_away_threshold_entry.get())
        selected_beep_sound = selected_beep.get()  # Get the selected beep sound
        
        # Initialize camera
        cap = cv2.VideoCapture(0)

        # Load Haar Cascades (use the correct path)
        face_cascade_path = get_cascade_path('haarcascade_frontalface_default.xml')
        eye_cascade_path = get_cascade_path('haarcascade_eye.xml')

        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        if face_cascade.empty() or eye_cascade.empty():
            raise Exception("Haar Cascade files not loaded correctly.")

        # Timer variables
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
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)  # White for face
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 2)  # Green for eyes
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
    global window_tracking_active
    last_window = None
    beep_sound = pygame.mixer.Sound(f'sounds/{selected_beep.get()}')

    while window_tracking_active:  # Check the global flag
        current_window = gw.getActiveWindow()

        if current_window:
            current_window_title = current_window.title

            if current_window_title != last_window:
                beep_sound.play()
                last_window = current_window_title

        time.sleep(0.5)

# Function to start window change tracking based on user input
def start_window_tracking():
    global window_tracking_active
    window_tracking_enabled = bool(int(window_changed_beep.get()))  # Convert to boolean
    
    if window_tracking_enabled:
        window_tracking_active = True  # Set flag to True to start tracking
        tracking_thread = threading.Thread(target=track_window_switch, daemon=True)
        tracking_thread.start()
    else:
        messagebox.showinfo("Info", "Window tracking is disabled. Set 'Beep If Window Changed' to 1 to enable tracking.")

# Function to stop window change tracking
def stop_window_tracking():
    global window_tracking_active
    window_tracking_active = False  # Set flag to False to stop tracking
    messagebox.showinfo("Info", "Window tracking has been stopped.")

# Create the Tkinter window
root = tk.Tk()
root.title("SlackTrack")

# tk.Label(root, text="Blink Threshold (Under Development):").grid(row=0, column=0, padx=10, pady=10)
# blink_threshold_entry = tk.Entry(root)
# blink_threshold_entry.grid(row=0, column=1, padx=10, pady=10)
# blink_threshold_entry.insert(0, "∞")

# Set application icon (for .ico files)
try:
    root.iconbitmap("icons8-widgetsmith.ico")
except Exception as e:
    print(f"Error setting application icon: {e}")

# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Look Away Threshold (seconds):", fg="white", bg="black").grid(row=0, column=0, padx=10, pady=10)
look_away_threshold_entry = tk.Entry(root, fg="white", bg="black", insertbackground='white')  # White text and cursor
look_away_threshold_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=10)
look_away_threshold_entry.insert(0, "5")

# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Beep If Window Changed (0/1):", fg="white", bg="black").grid(row=1, column=0, padx=10, pady=10)
window_changed_beep = tk.Entry(root, fg="white", bg="black", insertbackground='white')
window_changed_beep.grid(row=1, column=1, columnspan=3, padx=10, pady=10)
window_changed_beep.insert(0, "0")

# Label and ComboBox for beep selection
tk.Label(root, text="Select Beep Sound:", fg="white", bg="black").grid(row=2, column=0, padx=0, pady=0)

# Create a ttk Style to customize the Combobox appearance
style = ttk.Style()
style.configure("TCombobox",
                foreground="white",  # Set text color to white
                background="black",  # Set background color to black
                fieldbackground="black",  # Set the dropdown field color to black
                darkcolor="black")  # Set the dark mode background for the combobox

beep_options = ["beep01.wav", "beep02.wav", "beep03.wav", "beep04.wav", "beep05.wav", "beep06.wav", "beep07.wav"]
selected_beep = ttk.Combobox(root, values=beep_options, state="readonly", style="TCombobox")
selected_beep.grid(row=2, column=1, padx=10, pady=10)
selected_beep.set(beep_options[0])  # Default value

# Button to play the selected beep sound as a preview
play_button = tk.Button(root, text="Play Preview", command=play_preview_beep, fg="white", bg="black")
play_button.grid(row=2, column=2, pady=10, padx=10)

# Button to launch the camera
launch_button = tk.Button(root, text="Launch Camera", command=launch_camera, fg="white", bg="black")
launch_button.grid(row=3, pady=20)

# Button to start window change tracking
start_tracking_button = tk.Button(root, text="Start Window Tracking", command=start_window_tracking, fg="white", bg="black")
start_tracking_button.grid(row=4, column=0, pady=10)

# Button to stop window change tracking
stop_tracking_button = tk.Button(root, text="Stop Window Tracking", command=stop_window_tracking, fg="white", bg="black")
stop_tracking_button.grid(row=4, column=1, pady=10)

# Set background color of the entire window to black
root.configure(bg='black')

# Run the Tkinter main loop
root.mainloop()