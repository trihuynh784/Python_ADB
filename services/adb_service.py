import subprocess
import cv2
import numpy as np
import random
import time
from pathlib import Path


class ADB:
    def __init__(self, deviceId):
        self.deviceId = deviceId
        self.width = 1280
        self.height = 720
        Path("assets").mkdir(exist_ok=True)

    def run_adb(self, args, capture_output=False):
        base_cmd = ["adb", "-s", self.deviceId]
        full_cmd = base_cmd + args

        try:
            if capture_output:
                # Trả về đối tượng CompletedProcess để lấy .stdout
                return subprocess.run(full_cmd, capture_output=True, check=True)
            else:
                # Thực thi lệnh bình thường (như click, swipe)
                subprocess.run(full_cmd, check=True)
                return True
        except subprocess.CalledProcessError as e:
            print(f"Lỗi thực thi ADB: {e}")
            return None
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            return None

    def screen_capture(self, name):
        """Lưu ảnh chụp màn hình trực tiếp vào file"""
        with open(f"assets/{name}.png", "wb") as f:
            # Dùng thẳng subprocess ở đây hoặc tối ưu qua run_adb
            subprocess.run(
                ["adb", "-s", self.deviceId, "exec-out", "screencap", "-p"], stdout=f
            )

    def screenshot(self):
        """Chụp màn hình và chuyển về định dạng OpenCV (numpy array)"""
        process = self.run_adb(["exec-out", "screencap", "-p"], capture_output=True)
        if not process or not process.stdout:
            return None
        # Chuyển đổi bytes từ adb sang mảng numpy để OpenCV đọc được
        return cv2.imdecode(np.frombuffer(process.stdout, np.uint8), cv2.IMREAD_COLOR)

    def click(self, x, y):
        self.run_adb(["shell", "input", "tap", str(x), str(y)])

    def draganddrop(self, x1, y1, x2, y2, dur=100):
        self.run_adb(
            [
                "shell",
                "input",
                "draganddrop",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                str(dur),
            ]
        )

    def swipe(self, x1, y1, x2, y2, duration=1000):
        self.run_adb(
            [
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
        self.run_adb(["shell", "input", "keyevent", str(key_name)])

    def find(self, target_img_path, threshold=0.8, debug=False, mark_mine=False):
        screen_img_full = self.screenshot()
        if screen_img_full is None:
            return None

        screen_img = cv2.cvtColor(screen_img_full, cv2.COLOR_BGR2GRAY)
        target_img = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
        if screen_img is None or target_img is None:
            return None

        result = cv2.matchTemplate(screen_img, target_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = target_img.shape
            center_x = max_loc[0] + (w // 2)
            center_y = max_loc[1] + (h // 2)
            print(f"- Found {target_img_path} (Score: {round(max_val, 2)})")
            return (
                [max_loc[0] + 10, max_loc[1] + 10]
                if mark_mine
                else [center_x, center_y]
            )
        return None

    def find_with_color(self, target_img_path, threshold=0.8, color_tolerance=30):
        """Hàm tìm theo màu sắc - Đã thêm cơ chế ngắt"""
        screen_img = self.screenshot()  # Đã có sẵn run_adb kiểm tra stop bên trong
        target_img = cv2.imread(target_img_path, cv2.IMREAD_COLOR)

        if screen_img is None or target_img is None:
            return None

        h, w, _ = target_img.shape
        screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(screen_gray, target_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        target_avg_color = cv2.mean(target_img)[:3]

        for pt in zip(*loc[::-1]):

            sample_roi = screen_img[pt[1] : pt[1] + h, pt[0] : pt[0] + w]
            sample_avg_color = cv2.mean(sample_roi)[:3]
            color_diff = np.linalg.norm(
                np.array(target_avg_color) - np.array(sample_avg_color)
            )

            if color_diff < color_tolerance:
                return [int(pt[0] + (w // 2)), int(pt[1] + (h // 2))]
        return None

    def find_all(self, target_img_path, threshold=0.8, debug=False):
        screen_img_full = self.screenshot()
        if screen_img_full is None:
            return []

        screen_img = cv2.cvtColor(screen_img_full, cv2.COLOR_BGR2GRAY)
        target_img = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
        if screen_img is None or target_img is None:
            return []

        h, w = target_img.shape
        res = cv2.matchTemplate(screen_img, target_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        results = []
        for pt in zip(*loc[::-1]):
            center_x = int(pt[0] + (w // 2))
            center_y = int(pt[1] + (h // 2))
            is_duplicate = any(
                abs(center_x - rx) < (w // 2) and abs(center_y - ry) < (h // 2)
                for rx, ry in results
            )
            if not is_duplicate:
                results.append([center_x, center_y])
        return results

    def swipe_escape_area(self, dx=None, dy=None, distance=250):
        cx, cy = 640, 360
        repeats = 2
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]
        if dx is None:
            dx, dy = random.choice(directions)

        for i in range(repeats):
            if dx == 0 and dy == 1:
                distance = 150
            offset = random.randint(-20, 20)
            x_end = cx - (dx * distance) + offset
            y_end = cy - (dy * distance) + offset
            self.draganddrop(cx, cy, int(x_end), int(y_end), dur=50)
