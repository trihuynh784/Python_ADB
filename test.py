import os
import time
import subprocess


def quick_swipe(x1, y1, x2, y2):
    """
    Vuốt cực nhanh để dịch chuyển bản đồ.
    Thời gian 100ms là mức 'vàng' để game không hiểu lầm là click.
    """
    # Lệnh input swipe x1 y1 x2 y2 duration
    os.system(f"adb shell input swipe {x1} {y1} {x2} {y2} 100")


def find_gem_pattern():
    # Giả sử màn hình 1280x720
    start_x, start_y = 1000, 360
    end_x, end_y = 700, 360

    for i in range(5):  # Quét 5 hàng
        # Swipe ngang cực nhanh
        print(f"Đang quét hàng thứ {i+1}...")
        quick_swipe(start_x, start_y, end_x, end_y)

        # Đợi map dừng hẳn rồi mới chụp màn hình scan Gem
        time.sleep(1.5)

        # Gọi hàm OpenCV của bạn ở đây
        # if find_gem(): break

        # Swipe dọc xuống để đổi vùng quét
        quick_swipe(640, 600, 640, 300)
        time.sleep(1.5)


find_gem_pattern()
# draganddrop(60, 655, 60, 655, 1000)
