import time
from bot.actions.check_someone_gathering import check_someone_gathering

import time


def scan_gem(adb, gem_images_list):
    cx, cy = adb.width // 2, adb.height // 2

    dist = 250
    duration = 100

    path = [
        (1, 0, 1),
        (0, 1, 1),
        (-1, 0, 2),
        (0, -1, 2),
        (1, 0, 2),
    ]

    print("--- Bắt đầu quét Gem (Fast Swipe Mode) ---")

    for dx, dy, steps in path:
        for s in range(steps):
            for gem_path in gem_images_list:
                loc = adb.find(gem_path, threshold=0.82)
                if loc:
                    isGathering = check_someone_gathering(adb)
                    if isGathering == "gatherable":
                        print(f"Thấy Gem! Tọa độ: {loc}")
                        return loc
                    else:
                        print("Mỏ đã có người hoặc không thể khai thác.")
                        continue

            ex = cx - (dx * dist)
            ey = cy - (dy * dist)

            adb.swipe(cx, cy, ex, ey, duration=duration)

            time.sleep(1.5)

    print("Kết thúc 1 vòng quét, không tìm thấy Gem.")
    return None
