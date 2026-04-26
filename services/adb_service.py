import subprocess
import cv2
import numpy as np
from pathlib import Path
import random
import time


class ADB:
    def __init__(self, deviceId):
        self.deviceId = deviceId
        self.width = 1280
        self.height = 720
        Path("assets").mkdir(exist_ok=True)

    def screen_capture(self, name):
        with open(f"assets/{name}.png", "wb") as f:
            subprocess.run(
                ["adb", "-s", self.deviceId, "exec-out", "screencap", "-p"], stdout=f
            )

    def click(self, x, y):
        subprocess.run(
            ["adb", "-s", self.deviceId, "shell", "input", "tap", str(x), str(y)]
        )

    def swipe(self, x1, y1, x2, y2, duration=1000):
        subprocess.run(
            [
                "adb",
                "-s",
                self.deviceId,
                "shell",
                "input",
                "swipe",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                str(duration),
            ]
        )

    def keyevent(self, key_name):
        subprocess.run(
            ["adb", "-s", self.deviceId, "shell", "input", "keyevent", key_name]
        )

    def find(self, target_img_path, threshold=0.8, debug=False, mark_mine=False):
        command = ["adb", "-s", self.deviceId, "exec-out", "screencap", "-p"]
        process = subprocess.run(command, capture_output=True)

        if not process.stdout:
            print("!!! Lỗi: ADB không phản hồi")
            return None

        # Fix: Use imdecode for bytes, not imread
        screen_img = cv2.imdecode(
            np.frombuffer(process.stdout, np.uint8), cv2.IMREAD_GRAYSCALE
        )
        target_img = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)

        if screen_img is None or target_img is None:
            print(f"Error loading images: screen or {target_img_path}")
            return None

        result = cv2.matchTemplate(screen_img, target_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if (max_val >= threshold) & debug:
            h, w = target_img.shape
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            cv2.rectangle(screen_img, top_left, bottom_right, (0, 0, 255), 2)
            cv2.putText(
                screen_img,
                f"Score: {round(max_val, 2)}",
                (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )

            cv2.imshow("Debug Bot View", screen_img)
            cv2.waitKey(0)

        if max_val >= threshold:
            h, w = target_img.shape
            center_x = max_loc[0] + (w // 2)
            center_y = max_loc[1] + (h // 2)
            print(f"- Found {target_img_path} (Score: {round(max_val, 2)})")
            if mark_mine:
                return [max_loc[0] + 10, max_loc[1] + 10]
            return [center_x, center_y]

        return None

    def swipe_escape_area(self):
        """
        Hàm vuốt 3 lần liên tiếp về một hướng ngẫu nhiên
        để rời khỏi khu vực hiện tại sau khi đã gửi quân.
        """
        # 1. Thông số theo yêu cầu
        distance = 300
        duration = 1200
        repeats = 8

        cx = self.width // 2
        cy = self.height // 2

        # 2. Chọn hướng ngẫu nhiên (chỉ chọn 1 lần duy nhất)
        # (dx, dy): 1 là đi theo chiều dương, -1 là chiều âm
        possible_directions = [
            (1, 0),  # Phải
            (-1, 0),  # Trái
            (0, 1),  # Lên
            (0, -1),  # Xuống
        ]
        dx, dy = random.choice(possible_directions)

        print(f"[*] Đã gửi quân! Bắt đầu vuốt 'thoát xác' 3 lần về hướng ({dx}, {dy})")

        # 3. Lặp lại 3 lần
        for i in range(repeats):
            if dx == 0 and dy == 1:
                repeats = 5

            # Tính toán điểm kết thúc cho mỗi lần vuốt
            ex = cx + (dx * distance)
            ey = cy + (dy * distance)

            print(f"   - Lần {i+1}/{repeats}: Vuốt từ ({cx}, {cy}) đến ({ex}, {ey})")

            # Thực hiện lệnh swipe
            self.swipe(cx, cy, ex, ey, duration=duration)

            # Đợi một chút ngắn giữa các lần vuốt để game nhận lệnh mượt hơn
            # Nếu vuốt quá dồn dập, game đôi khi chỉ nhận thành 1 cú vuốt dài
            time.sleep(0.5)

        # 4. Sau khi xong 3 lần, đợi map dừng hẳn rồi mới làm việc khác
        print("[V] Đã rời khỏi khu vực cũ.")
        time.sleep(1.5)
