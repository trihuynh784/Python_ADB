import cv2
import numpy as np
import subprocess
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = (
    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)


def get_screen_adb():
    # Chụp màn hình từ ADB
    command = "adb exec-out screencap -p"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    if not screenshot:
        return None
    return cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)


def get_coords_from_region(screen, x, y, w, h, debug_name="temp"):
    


def scan_all_bookmarks():
    


# list = scan_all_bookmarks()
# print(list)

screenshot = get_screen_adb()
loc = get_coords_from_region(screenshot, x=620, y=190, w=100, h=25)
print(loc)