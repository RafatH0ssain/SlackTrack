# SlackTrack

SlackTrack is a desktop application designed to help you stay focused by providing real-time alerts when certain behaviors are detected, such as looking away from the screen or closing your eyes for too long. It integrates with your webcam to track your eye movements and alerts you with a beep sound when necessary. The app also offers a window tracking feature to alert you when you switch between active windows.

## Features

- **Camera-based eye-tracking**:
  - Detects if you are looking away from the screen or if your eyes are closed.
  - Triggers an alert sound after a set time of inactivity or closed eyes.
  
- **Window tracking**:
  - Monitors active window changes and alerts you with a beep sound when you switch windows.

- **Sound alerts**:
  - Choose from multiple pre-configured beep sounds to alert you when certain conditions are met.
  - Preview the beep sound before use.

- **System tray integration**:
  - Minimize the app to the system tray for easy access.
  - Easily bring the app back into view by clicking the system tray icon.

## Installation

1. **Clone the repository**:
   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/RafatH0ssain/SlackTrack

2. **Running the Application**:

    Inside the `src` folder, there is a `dist` folder containing the `slacktrack.exe` file. Follow these steps to run the application:

a. Navigate to the `dist` folder:

    ```bash
    cd src/dist
    ```

b. Run the `slacktrack.exe` file: Simply double-click the `slacktrack.exe` file to launch the application.

## Requirements

Python: The app is built with Python and uses several libraries:

- `pygame` (for sound playback)
- `opencv-python` (for webcam and image processing)
- `pygetwindow` (for window tracking)
- `pystray` (for system tray functionality)
- `Pillow` (for system tray icon creation)
- `tkinter` (for the graphical user interface)

You can install these dependencies with the following command:

    ```bash
    pip install pygame opencv-python pygetwindow pystray Pillow tkinter
    ```

## Usage

### Camera-based Eye Tracking:
- The app will start the webcam and look for face and eye detection using Haar cascades.
- It will track if you look away or close your eyes for more than the specified threshold time.
- You can configure the threshold (in seconds) via the GUI.

### Window Tracking:
- The app can also track window switches. If you switch to a new window, it will alert you with a beep sound.
- This feature can be started or stopped via the GUI.

### Customization:
- Choose a beep sound from a list of options.
- Preview the beep sound before starting the tracking.

## Application Interface

- **Look Away Threshold (seconds)**: Set the number of seconds to wait before triggering the alert when you look away from the screen.
- **Select Beep Sound**: Choose from various beep sound options to notify you during eye or window tracking.
- **Preview Beep**: Play the selected beep sound to ensure it suits your preferences.
- **Start Camera**: Start the webcam for eye tracking.
- **Start Window Tracking**: Start tracking window changes to alert you when switching between applications.
- **Stop Window Tracking**: Stop the window tracking feature.
