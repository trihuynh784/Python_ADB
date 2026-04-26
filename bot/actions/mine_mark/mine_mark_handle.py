import cv2
import pytesseract
import numpy as np
import re
import time
import subprocess
from bot.actions.mine_mark.ResourcePoint import ResourcePoint

pytesseract.pytesseract.tesseract_cmd = (
    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)

mark_mine_template_path = "assets/template/mark_mine.png"
is_marked_template_path = "assets/template/is_marked.png"
confirm_template_path = "assets/template/confirm.png"
star_template_path = "assets/template/star.png"
star_special_template_path = "assets/template/star_special.png"


# Lấy ra 1 location của mỏ gem
def get_location_mine(screen, x, y, w, h):
    roi = screen[y : y + h, x : x + w]

    if roi.size == 0:
        return None

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_LANCZOS4)

    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(resized, -1, kernel)

    _, thresh = cv2.threshold(sharpened, 150, 255, cv2.THRESH_BINARY_INV)

    custom_config = r"--psm 7 -c tessedit_char_whitelist=0123456789XY: "
    text = pytesseract.image_to_string(thresh, config=custom_config).upper()

    nums = re.findall(r"\d+", text)

    if len(nums) >= 2:
        return int(nums[-2]), int(nums[-1])
    else:
        return None


# Lấy ra 1 list nhiều location của mỏ gem
def get_list_location_mine():
    screen = get_screen_adb()
    if screen is None:
        print("[-] Không thể chụp màn hình ADB")
        return []

    start_x, start_y = 310, 220
    w, h = 100, 25
    row_gap = 61

    found_coords = []

    for i in range(5):
        curr_y = start_y + i * (h + row_gap)
        result = get_location_mine(screen, start_x, curr_y, w, h)

        if result:
            val_x, val_y = result
            found_coords.append(ResourcePoint(val_x, val_y))
            print(f"Hàng {i+1}: Tìm thấy X:{val_x} Y:{val_y}")
        else:
            print(f"Hàng {i+1}: OCR thất bại (Xem ảnh debug_error_row_{i}.png)")

    return found_coords


# Đánh dấu mỏ gem vào list trong game (star)
def set_mine_into_list(adb, list_mine):
    is_marked_loc = check_is_marked(adb)
    if is_marked_loc is None:
        while True:
            mark_mine_loc = adb.find(mark_mine_template_path, mark_mine=True)
            if mark_mine_loc is not None:
                adb.click(*mark_mine_loc)
                time.sleep(0.8)
                while True:
                    mine_loc = get_location_mine(
                        get_screen_adb(), x=620, y=190, w=100, h=25
                    )
                    if mine_loc is not None:
                        rp = ResourcePoint(*mine_loc)
                        # todo: logic check xem khoảng cách giữa các mỏ đã mark có cách nhau tối thiểu (50px) hay ko --- Tránh farm trùng mỏ
                        if is_safe_distance(list_mine, rp.x, rp.y):
                            list_mine.append(rp)

                            while True:
                                confirm_loc = adb.find(confirm_template_path)
                                if confirm_loc is not None:
                                    adb.click(*confirm_loc)
                                    time.sleep(0.8)
                                    print("Marking mine success!")
                        else:
                            print("This mine is not in a safe distance!")
                        return
    print("This mine is marked!")


# Open mine marked
def open_mine_marked(adb):
    while True:
        star_loc = adb.find(star_template_path)
        if star_loc is not None:
            adb.click(*star_loc)
            time.sleep(1.5)
            while True:
                star_special_loc = adb.find(star_special_template_path, threshold=0.8)
                if star_special_loc is not None:
                    adb.click(*star_special_loc)
                    time.sleep(0.8)
                    return


# Hàm util check đã mark chưa
def check_is_marked(adb):
    is_marked_loc = adb.find(is_marked_template_path)
    if is_marked_template_path is not None:
        return is_marked_loc

    print("Mine is marked!")
    return None


# Hàm util chụp ảnh
def get_screen_adb():
    # Chụp màn hình từ ADB
    command = "adb exec-out screencap -p"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    if not screenshot:
        return None
    return cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)


# Hàm check xem khoảng cách giữa các mỏ đã mark có cách nhau tối thiểu (50px) hay ko --- Tránh farm trùng mỏ
def is_safe_distance(mine_list, curr_x, curr_y, threshold=50):
    for mine in mine_list:
        dist_x = abs(mine.x - curr_x)
        dist_y = abs(mine.y - curr_y)

        if dist_x < threshold and dist_y < threshold:
            print("Doesn't have a safe distance!")
            return False
    print("Mine in a safe distance!")
    return True
