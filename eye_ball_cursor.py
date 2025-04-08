import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from pynput.mouse import Controller, Button
import time
import os
from plyer import notification

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Initialize mouse controller
mouse = Controller()

# Screen resolution
screen_width, screen_height = 1920, 1080

# Screenshot folder setup
screenshot_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# Blink and wink detection variables
wink_threshold = 0.25
blink_threshold = 0.18
wink_duration = 0.2
last_wink_time = time.time()
left_wink_start = None
right_wink_start = None

# Screenshot detection variables
screenshot_duration = 3.0  # Must blink for 3 seconds
screenshot_start_time = None

# Scroll detection variables
scroll_threshold = 15
scroll_cooldown = 0.5
last_scroll_time = time.time()
prev_eye_y = None

# Gaze click control variables (DISABLED BY DEFAULT)
gaze_click_enabled = False

# EAR (Eye Aspect Ratio) calculation
def eye_aspect_ratio(eye_top, eye_bottom, eye_left, eye_right):
    vertical = abs(eye_top.y - eye_bottom.y)
    horizontal = abs(eye_left.x - eye_right.x)
    return vertical / horizontal if horizontal > 0 else 0

# Capture video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get iris positions
            left_iris = face_landmarks.landmark[468]
            right_iris = face_landmarks.landmark[473]

            # Get eye landmarks for EAR calculation
            left_eye_top = face_landmarks.landmark[159]
            left_eye_bottom = face_landmarks.landmark[145]
            left_eye_left = face_landmarks.landmark[33]
            left_eye_right = face_landmarks.landmark[133]

            right_eye_top = face_landmarks.landmark[386]
            right_eye_bottom = face_landmarks.landmark[374]
            right_eye_left = face_landmarks.landmark[362]
            right_eye_right = face_landmarks.landmark[263]

            # Calculate EAR for both eyes
            left_EAR = eye_aspect_ratio(left_eye_top, left_eye_bottom, left_eye_left, left_eye_right)
            right_EAR = eye_aspect_ratio(right_eye_top, right_eye_bottom, right_eye_left, right_eye_right)

            current_time = time.time()

            # *Detect Left Wink (Left Click)*
            if left_EAR < wink_threshold and right_EAR > wink_threshold + 0.1:
                if left_wink_start is None:
                    left_wink_start = time.time()
                elif time.time() - left_wink_start > wink_duration and (current_time - last_wink_time > 1):
                    mouse.click(Button.left, 1)
                    last_wink_time = current_time
                    left_wink_start = None
            else:
                left_wink_start = None

            # *Detect Right Wink (Right Click)*
            if right_EAR < wink_threshold and left_EAR > wink_threshold + 0.1:
                if right_wink_start is None:
                    right_wink_start = time.time()
                elif time.time() - right_wink_start > wink_duration and (current_time - last_wink_time > 1):
                    mouse.click(Button.right, 1)
                    last_wink_time = current_time
                    right_wink_start = None
            else:
                right_wink_start = None

            # *Detect Blink (Screenshot)*
            if left_EAR < blink_threshold and right_EAR < blink_threshold:
                if screenshot_start_time is None:
                    screenshot_start_time = time.time()
                elif time.time() - screenshot_start_time > screenshot_duration:
                    filename = os.path.join(screenshot_folder, f"screenshot_{int(time.time())}.png")
                    pyautogui.screenshot(filename)
                    print(f"Screenshot saved at: {filename}")

                    # Notification
                    notification.notify(
                        title="Screenshot Taken",
                        message=f"Saved at: {filename}",
                        app_name="Eye Tracker",
                        timeout=5
                    )

                    # Open screenshot folder
                    os.startfile(screenshot_folder)
                    screenshot_start_time = None
            else:
                screenshot_start_time = None

            # *Prevent unintended gaze clicks while watching videos*
            active_window = pyautogui.getActiveWindowTitle()
            if active_window and "youtube" in active_window.lower():
                gaze_click_enabled = False  # Disable gaze clicking
            else:
                gaze_click_enabled = True  # Enable gaze clicking if not watching a video

            # *Calculate cursor movement*
            left_x, left_y = int(left_iris.x * w), int(left_iris.y * h)
            right_x, right_y = int(right_iris.x * w), int(right_iris.y * h)

            # Average eye position
            eye_x, eye_y = (left_x + right_x) // 2, (left_y + right_y) // 2
            cursor_x = int((eye_x / w) * screen_width)
            cursor_y = int((eye_y / h) * screen_height)

            # Move cursor
            mouse.position = (cursor_x, cursor_y)

            # *Scrolling with vertical eye movement*
            eye_y = int(((left_iris.y + right_iris.y) / 2) * h)
            if prev_eye_y is not None:
                vertical_movement = eye_y - prev_eye_y

                if vertical_movement < -scroll_threshold and (time.time() - last_scroll_time > scroll_cooldown):
                    mouse.scroll(0, 10)  # Scroll up
                    last_scroll_time = time.time()

                elif vertical_movement > scroll_threshold and (time.time() - last_scroll_time > scroll_cooldown):
                    mouse.scroll(0, -10)  # Scroll down
                    last_scroll_time = time.time()

            prev_eye_y = eye_y

            # *Draw landmarks*
            cv2.circle(frame, (left_x, left_y), 5, (0, 255, 0), -1)
            cv2.circle(frame, (right_x, right_y), 5, (0, 255, 0), -1)

    # Display tracking
    cv2.imshow("Eye Tracking with Wink, Blink, Screenshot & Scroll", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()


