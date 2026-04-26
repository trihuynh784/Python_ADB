STATUS_ARMIES = [
    "assets/template/army_returning.png",
    "assets/template/full_army_5.png",
]


def check_status_army(adb):
    # Duyệt qua danh sách ảnh mẫu
    for path in STATUS_ARMIES:
        loc = adb.find(path, threshold=0.95)

        if loc is not None:
            # Nếu tìm thấy ảnh chứa chữ "returning"
            if "returning" in path:
                return loc, "returning"

            # Nếu tìm thấy ảnh chứa chữ "full_army"
            if "full_army" in path:
                print("All army farming!")
                return None, "full_army"  # Đã kéo hết 5/5 đạo ra ngoài

    # Nếu chạy hết vòng lặp mà không tìm thấy 'full_army_5'
    # Nghĩa là số lượng đạo quân đang ở ngoài < 5 (ví dụ 1/5, 2/5...)
    return None, "not_full_army"
