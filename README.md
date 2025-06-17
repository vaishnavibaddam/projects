# 👁️ Eye Tracking System Using MediaPipe and Python

This project is a real-time **eye tracking system** using Python, MediaPipe, and OpenCV. It enables **hands-free mouse control**, **screenshot capture**, **scrolling**, and **tab closing** using only your eye movements, blinks, and winks.

---

## 🚀 Features

- 🖱️ **Cursor Movement**: Follows your eye (iris) position in real-time.
- 👁️ **Left Click**: Wink with your **left eye**.
- 👁️ **Right Click**: Wink with your **right eye**.
- 👀 **Screenshot**: Blink both eyes for more than 3 seconds.
- 📜 **Scrolling**: Scroll up/down by moving your eyes vertically.
- ❌ **Close Tab**: Move your eye to the **bottom-left corner** to close the current browser tab.
- 🔊 **Beep Alert**: Plays a beep sound once when the face is detected for the first time.
- 📂 **Screenshot Auto Save**: Captures and saves screenshots in the `Pictures/Screenshots` folder.

---

## 🛠️ Requirements

Install the following Python packages before running the app:

```bash
pip install opencv-python mediapipe pyautogui pynput plyer
