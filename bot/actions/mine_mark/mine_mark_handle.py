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
def get_list_location_mine(adb):
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

    go_list = adb.find_all("assets/template/go.png")

    return found_coords, go_list


# Đánh dấu mỏ gem vào list trong game (star)
def set_mine_into_list(adb, list_mine):
    # Kiểm tra xem mỏ đã được mark chưa (Sửa lại check_is_marked như tôi đã nói ở câu trước)
    if check_is_marked(adb) is not None:
        print("Mỏ này đã được đánh dấu trước đó rồi!")
        return False

    # Thử click nút Mark (hình ngôi sao)
    mark_mine_loc = None
    for _ in range(5):
        mark_mine_loc = adb.find(mark_mine_template_path, mark_mine=True)
        if mark_mine_loc:
            adb.click(*mark_mine_loc)
            time.sleep(1.0)
            break

    if not mark_mine_loc:
        print("[-] Không tìm thấy nút để Mark mỏ.")
        return False

    # Lấy tọa độ từ OCR để lưu vào list local
    mine_loc = get_location_mine(get_screen_adb(), x=620, y=190, w=100, h=25)
    if mine_loc:
        list_mine.append(ResourcePoint(*mine_loc))

    # Click Confirm để xác nhận lưu vào Star List trong game
    for _ in range(10):  # Thử tìm nút Confirm trong 10 lần (~8-10 giây)
        confirm_loc = adb.find(confirm_template_path)
        if confirm_loc:
            adb.click(*confirm_loc)
            time.sleep(1.0)
            print("[+] Đánh dấu mỏ thành công!")
            return True
        time.sleep(0.8)

    print("[-] Đã mở menu Mark nhưng không tìm thấy nút Confirm (có thể bị lag).")


# Open mine marked
def open_mine_marked(adb):
    for _ in range(5):  # Thử tối đa 5 lần
        star_loc = adb.find(star_template_path)
        if star_loc:
            adb.click(*star_loc)
            time.sleep(0.5)
            # Tìm tab đặc biệt bên trong
            for _ in range(10):
                star_special_loc = adb.find(star_special_template_path, threshold=0.7)
                if star_special_loc:
                    adb.click(*star_special_loc)
                    return True  # Thoát khi thành công
                time.sleep(0.5)
    return False


# Hàm util check đã mark chưa
def check_is_marked(adb):
    is_marked_loc = adb.find(is_marked_template_path)
    if is_marked_loc is not None:  # Sửa ở đây
        return is_marked_loc
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
