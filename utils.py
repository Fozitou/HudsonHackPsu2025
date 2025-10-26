import cv2
import os
from datetime import datetime
import pyautogui

def take_a_photo(output_dir="./Photos", filename=None):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture image")

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.png"

    path = os.path.join(output_dir, filename)
    cv2.imwrite(path, frame)
    return path


def take_a_screenshot(output_dir="./Screenshots", filename=None):
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

    path = os.path.join(output_dir, filename)

    pyautogui.screenshot(path)

    return path