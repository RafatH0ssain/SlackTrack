import pygame
import time
import cv2
import tkinter as tk
from tkinter import messagebox, ttk

import pygetwindow as gw
import threading  # Import threading for background tasks
import os
import sys

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

def create_image():
    # Create an image to represent the app in the system tray
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(0, 0, 0))

    # Create a drawing context for the image
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width, height], fill="black")

    return image

def on_quit(icon, item):
    icon.stop()
    root.quit()  # Exit Tkinter

def on_show(icon, item):
    # If the icon is clicked, show the Tkinter window
    root.deiconify()
    icon.stop()

def system_tray():
    # Create the icon and menu
    icon = pystray.Icon("SlackTrack", create_image(), menu=(
        item("Show", on_show),
        item("Quit", on_quit)
    ))

    # This is necessary to run the system tray icon in the background
    icon.run()

# Initial window setup
root = tk.Tk()
root.title("SlackTrack")
root.config(bg="black")

# Hide the window on start
# root.withdraw()
def on_show(icon, item):
    root.deiconify()  # Restore the window
    icon.stop()  # Stop the tray icon thread

def on_minimize(event=None):
    root.withdraw()  # Hide the main window
    system_tray()  # Start the system tray icon (this is already done once)
    
root.protocol("WM_DELETE_WINDOW", on_minimize)  # To handle the minimize event

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

# Example function to play a beep sound using pygame.mixer.music for mp3 files
def play_beep_sound(beep_file):
    beep_path = get_sound_path(beep_file)
    print(f"Beep path: {beep_path}")
    pygame.mixer.music.load(beep_path)  # For .mp3 or .ogg
    pygame.mixer.music.play()

# Initialize pygame mixer for sound
pygame.mixer.init()

# Global variable to control window tracking
window_tracking_active = False

# Function to play the preview of the selected beep sound
def play_preview_beep():
    beep_file = selected_beep.get()  # Get the selected beep file from the dropdown
    beep_sound = pygame.mixer.Sound(f'sounds/{beep_file}')  # Load the beep sound
    beep_sound.play()  # Play the beep sound once

def get_cascade_path(cascade_file):
    # Get the absolute path of the directory where the current script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Directory of the current script
    
    # If the script is frozen (packaged), we use _MEIPASS for accessing bundled files
    if getattr(sys, 'frozen', False):  # Running as a bundled executable
        path = os.path.join(sys._MEIPASS, cascade_file)  # Don't add 'src' here
    else:  # Running as a script
        path = os.path.join(script_dir,  cascade_file)  # Ensure 'src' is only added here
    
    # Check if the path exists
    if not os.path.exists(path):
        print(f"File not found: {path}")
    
    return path

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
        beep_path = get_sound_path(selected_beep_sound)  # Get correct path based on execution type
        beep_sound = pygame.mixer.Sound(beep_path)  # Load sound from the correct path

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
    window_tracking_active = True  # Set flag to True to start tracking
    tracking_thread = threading.Thread(target=track_window_switch, daemon=True)
    tracking_thread.start()

# Function to stop window change tracking
def stop_window_tracking():
    global window_tracking_active
    window_tracking_active = False  # Set flag to False to stop tracking
    messagebox.showinfo("Info", "Window tracking has been stopped.")

# Set the background color for the main window
root.config(bg="black")

try:
    root.iconbitmap("icons8-widgetsmith.ico")
except Exception as e:
    print(f"Error setting application icon: {e}")

# Create and place the labels, entries, and button for the GUI
tk.Label(root, text="Look Away Threshold (seconds):", fg="white", bg="black").grid(row=0, column=0, padx=10, pady=10)
look_away_threshold_entry = tk.Entry(root, fg="white", bg="black", insertbackground='black')  # White text and cursor
look_away_threshold_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=10)
look_away_threshold_entry.insert(0, "5")

# Label and ComboBox for beep selection
tk.Label(root, text="Select Beep Sound:", fg="white", bg="black").grid(row=1, column=0, padx=0, pady=0)

# Create a ttk Style to customize the Combobox appearance
style = ttk.Style()
style.configure("TCombobox",
                foreground="white",  # Set text color to white
                background="black",  # Set background color to black
                fieldbackground="black",  # Set the dropdown field color to black
                darkcolor="black")  # Set the dark mode background for the combobox

beep_options = ["beep01.mp3", "beep02.mp3", "beep03.mp3", "beep04.mp3", "beep05.mp3", "beep06.mp3", "beep07.mp3"]
selected_beep = ttk.Combobox(root, values=beep_options, state="readonly", style="TCombobox")
selected_beep.grid(row=1, column=1, padx=10, pady=10)
selected_beep.set(beep_options[0])  # Set a default option

# Button to preview beep sound
preview_button = tk.Button(root, text="Preview Beep", fg="white", bg="black", command=play_preview_beep)
preview_button.grid(row=2, column=0, padx=10, pady=10)

# Button to start camera
camera_button = tk.Button(root, text="Start Camera", fg="white", bg="black", command=launch_camera)
camera_button.grid(row=2, column=1, padx=10, pady=10)

# Button to start window tracking
start_tracking_button = tk.Button(root, text="Start Window Tracking", fg="white", bg="black", command=start_window_tracking)
start_tracking_button.grid(row=3, column=0, padx=10, pady=10)

# Button to stop window tracking
stop_tracking_button = tk.Button(root, text="Stop Window Tracking", fg="white", bg="black", command=stop_window_tracking)
stop_tracking_button.grid(row=3, column=1, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()