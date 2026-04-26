import time
from bot.actions.check_someone_gathering import check_someone_gathering

def scan_gem(adb, gem_images_list, max_steps=20):
    # Tọa độ tâm màn hình (Điểm đặt tay để vuốt)
    cx, cy = adb.width // 2, adb.height // 2

    # Khoảng cách vuốt mỗi lần (Tăng lên để camera đi xa hơn)
    # Nếu để 500 mà camera vẫn quanh quẩn, hãy thử tăng lên 600-700
    swipe_dist = 300

    # Hướng di chuyển camera (Dùng để tính toán end_x, end_y)
    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]  # Phải, Xuống, Trái, Lên
    current_dir = 0
    steps_to_move = 1

    print("--- Bắt đầu hành trình rời xa nhà tìm Gem ---")

    for cycle in range(max_steps):
        for _ in range(2):  # Mỗi chiều dài bước đi 2 hướng
            dx, dy = directions[current_dir]

            if dx == 0 and dy == 1:
                swipe_dist = 250

            for _ in range(steps_to_move):
                for gem_path in gem_images_list:
                    loc = adb.find(gem_path, threshold=0.9)
                    if loc:
                        isGathering = check_someone_gathering(adb)
                        if isGathering == "gatherable":
                            print(f"Thấy Gem rồi! Tọa độ: {loc}")
                            return loc

                # 2. Thực hiện SWIPE để di chuyển sang vùng hoàn toàn mới
                # Để camera đi sang PHẢI, ta vuốt từ TRÁI sang PHẢI (hoặc ngược lại tùy bạn muốn)
                # Công thức: Vuốt từ Tâm (cx, cy) tới cạnh màn hình
                ex = cx - (dx * swipe_dist)
                ey = cy - (dy * swipe_dist)

                # Dùng duration dài một chút (800-1000ms) để swipe "đầm" hơn, tránh bị bật lại
                adb.swipe(cx, cy, ex, ey, duration=1200)
                time.sleep(1.0)
                adb.swipe(cx, cy, ex, ey, duration=1200)
                time.sleep(1.0)

            # Đổi hướng
            current_dir = (current_dir + 1) % 4

        # Sau mỗi 2 hướng, tăng số bước để vòng xoáy to dần ra
        steps_to_move += 1
