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

    def draganddrop(self, x1, y1, x2, y2, dur=100):
        subprocess.run(
            [
                "adb",
                "-s",
                self.deviceId,
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

    def find_all(self, target_img_path, threshold=0.8, debug=False):
        command = ["adb", "-s", self.deviceId, "exec-out", "screencap", "-p"]
        process = subprocess.run(command, capture_output=True)

        if not process.stdout:
            print("!!! Lỗi: ADB không phản hồi")
            return []

        # Decode ảnh từ bộ nhớ đệm
        screen_img = cv2.imdecode(
            np.frombuffer(process.stdout, np.uint8), cv2.IMREAD_GRAYSCALE
        )
        target_img = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)

        if screen_img is None or target_img is None:
            print(f"Error loading images: screen or {target_img_path}")
            return []

        h, w = target_img.shape
        res = cv2.matchTemplate(screen_img, target_img, cv2.TM_CCOEFF_NORMED)

        # Tìm tất cả các vị trí có độ khớp > threshold
        loc = np.where(res >= threshold)

        results = []
        # loc trả về theo dạng (array_y, array_x)
        for pt in zip(*loc[::-1]):
            center_x = int(pt[0] + (w // 2))
            center_y = int(pt[1] + (h // 2))

            # Để tránh việc lấy quá nhiều điểm trùng lặp sát nhau (nhiễu)
            # Chúng ta có thể kiểm tra xem điểm này đã tồn tại trong list chưa
            is_duplicate = False
            for existing_x, existing_y in results:
                if abs(center_x - existing_x) < (w // 2) and abs(
                    center_y - existing_y
                ) < (h // 2):
                    is_duplicate = True
                    break

            if not is_duplicate:
                results.append([center_x, center_y])
                if debug:
                    cv2.rectangle(
                        screen_img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2
                    )

        if debug and len(results) > 0:
            cv2.imshow("Debug Find All", screen_img)
            cv2.waitKey(0)

        # print(f"- Found {len(results)} matches for {target_img_path}")
        return results

    def swipe_escape_area(self):
        distance = 400  # Tăng khoảng cách một chút để bay xa hơn
        duration = 100  # Cực nhanh
        repeats = 2

        cx = self.width // 2
        cy = self.height // 2

        # 2. Chọn hướng ngẫu nhiên
        possible_directions = [
            (1, 0),  # Phải
            (-1, 0),  # Trái
            (0, 1),  # Lên
            (0, -1),  # Xuống
        ]
        dx, dy = random.choice(possible_directions)

        print(f"[*] Thoát xác nhanh: {repeats} lần về hướng {dx, dy}")

        # 3. Thực hiện vuốt dồn dập
        for i in range(repeats):
            ex = cx + (dx * distance)
            ey = cy + (dy * distance)

            # Vuốt không chờ đợi
            self.swipe(cx, cy, ex, ey, duration=duration)

            # Chỉ nghỉ cực ngắn để ADB kịp gửi lệnh tiếp theo
            time.sleep(0.1)

        print("[V] Đã đứng im tại khu vực mới.")
