import win32gui # type: ignore
import win32con # type: ignore
import time

def zoom_out(window_title="LDPlayer"):
    # 1. Tìm cửa sổ mẹ
    hwnd_main = win32gui.FindWindow(None, window_title)

    if not hwnd_main:
        print(f"Không tìm thấy cửa sổ: {window_title}")
        return

    # 2. Tìm cửa sổ con thực sự nhận tín hiệu phím (RenderWindow)
    # LDPlayer thường dùng một cửa sổ con để render game
    hwnd_child = win32gui.FindWindowEx(hwnd_main, None, "RenderWindow", None)

    # Nếu không tìm thấy RenderWindow, thử gửi trực tiếp vào main hoặc tìm tiếp
    target_hwnd = hwnd_child if hwnd_child else hwnd_main

    print(f"Đang gửi lệnh tới Handle: {target_hwnd}")

    # 3. Gửi lệnh nhấn giữ (A: 0x41, D: 0x44)
    # Dùng PostMessage sẽ "nhẹ" và ít bị treo hơn SendMessage khi chạy ngầm
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, 0x41, 0)
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, 0x44, 0)

    time.sleep(1.5)  # Thời gian zoom

    # 4. Giải phóng phím
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, 0x41, 0)
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, 0x44, 0)
