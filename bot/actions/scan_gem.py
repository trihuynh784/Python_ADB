import time
from bot.actions.check_someone_gathering import check_someone_gathering
from services.util_service import check_out_map


def scan_gem(adb_obj, gem_images_list):
    before_scan(adb_obj)
    print("--- Quét Xoắn Vuông Diện Rộng ---")

    # 1. Xác định tọa độ trung tâm màn hình (ví dụ 1280x720)
    # Bạn nên thay bằng adb_obj.get_screen_size() nếu có
    center_x, center_y = 640, 360

    # Độ dài một "bước" vuốt (tính bằng pixel)
    # Tùy độ zoom của game, bạn có thể chỉnh từ 200-400
    swipe_distance = 300

    # Hướng di chuyển (dx, dy)
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    step_size = 1
    dir_idx = 0

    for i in range(10):  # Chạy 10 cạnh xoắn
        dx, dy = directions[dir_idx]

        if dx == 0 and dy == 1:
            swipe_distance = 200
        else:
            swipe_distance = 300

        for s in range(step_size):
            # --- BƯỚC 1: QUÉT TÌM GEM ---
            for gem_path in gem_images_list:
                loc = adb_obj.find(gem_path, threshold=0.85)
                if loc:
                    # Kiểm tra xem có ai đang đào không (giả định hàm này bạn đã có)
                    someone_gathering = check_someone_gathering(adb_obj)
                    if someone_gathering == "gatherable":
                        print(f"Tìm thấy Gem tại: {loc}")
                        return loc

            # --- BƯỚC 2: DI CHUYỂN CAMERA BẰNG DRAGANDDROP ---
            # Để kéo camera sang PHẢI, ta phải vuốt từ PHẢI sang TRÁI
            # Do đó ta đảo ngược dấu của dx và dy
            x_start = center_x
            y_start = center_y
            x_end = center_x - (dx * swipe_distance)
            y_end = center_y - (dy * swipe_distance)

            # Gọi hàm draganddrop của bạn
            # dur=500 giúp thao tác kéo mượt hơn, tránh bị khựng map
            adb_obj.draganddrop(x_start, y_start, x_end, y_end, 150)

            # Đợi map load tài nguyên
            time.sleep(1.2)

        # Tăng kích thước cạnh sau mỗi 2 hướng
        if i % 2 == 1:
            step_size += 1

        dir_idx = (dir_idx + 1) % 4

    return None


def before_scan(adb):
    outed_map = check_out_map(adb)
    if outed_map == "outed_map":
        for i in range(3):
            home_loc = adb.find("assets/template/home_location.png")
            if home_loc is not None:
                adb.click(*home_loc)
                time.sleep(0.8)
                return
