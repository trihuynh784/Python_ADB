import pytesseract
import re
import cv2
import numpy as np
import subprocess

pytesseract.pytesseract.tesseract_cmd = (
    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)


def check_safe_distance(adb_obj, threshold=0.8):
    home_loc = adb_obj.find("assets/template/home_location.png", threshold=threshold)

    if not home_loc:
        print("[-] Không tìm thấy găng tay trên màn hình.")
        return None

    gx, gy = home_loc

    command = ["adb", "-s", adb_obj.deviceId, "exec-out", "screencap", "-p"]
    process = subprocess.run(command, capture_output=True)
    screen_img = cv2.imdecode(np.frombuffer(process.stdout, np.uint8), cv2.IMREAD_COLOR)

    roi_y1, roi_y2 = max(0, gy - 120), min(screen_img.shape[0], gy + 80)
    roi_x1, roi_x2 = max(0, gx - 100), min(screen_img.shape[1], gx + 100)
    roi = screen_img[roi_y1:roi_y2, roi_x1:roi_x2]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh_roi = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY_INV)

    text = pytesseract.image_to_string(
        thresh_roi, config="--psm 7 -c tessedit_char_whitelist=0123456789KMkm"
    )

    match = re.search(r"(\d+)", text)

    if match:
        distance = int(match.group(1))
        print(f"[+] Khoảng cách phát hiện: {distance} KM")

        if distance > 70:
            center_screen_x, center_screen_y = 640, 360

            diff_x = gx - center_screen_x
            diff_y = gy - center_screen_y

            norm = np.sqrt(diff_x**2 + diff_y**2)
            dx = round(diff_x / norm, 2) if norm != 0 else 0
            dy = round(diff_y / norm, 2) if norm != 0 else 0

            return dx, dy, 300

    print("[-] Không đọc được khoảng cách hoặc khoảng cách an toàn.")
    return None


def check_out_map(adb):
    outed_map_templates = [
        "assets/template/out_map_1.png",
        "assets/template/out_map_2.png",
    ]

    for path in outed_map_templates:
        outed_map_loc = adb.find_with_color(path)
        if outed_map_loc is not None:
            return "outed_map"

    return "in_map"


def get_online_devices():
    devices = []
    try:
        output = subprocess.check_output("adb devices", shell=True).decode("utf-8")

        lines = output.strip().split("\n")

        for line in lines[1:]:
            if "device" in line and "\toffline" not in line:
                device_id = line.split("\t")[0]
                devices.append(device_id)

    except Exception as e:
        print(f"Lỗi khi lấy danh sách device: {e}")

    return devices


def get_current_package(device_id):
    try:
        # Lệnh này lấy tên ứng dụng đang hiện trên màn hình
        cmd = f"adb -s {device_id} shell dumpsys window | findstr mCurrentFocus"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # Output mẫu: mCurrentFocus=Window{... com.lilithgame.roc.gp/...}
        if "/" in output:
            package = output.split(" ")[-1].split("/")[0].split("{")[-1]
            return package
    except:
        return None
    return None
