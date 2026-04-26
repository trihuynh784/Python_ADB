def check_status_army(adb):
    # Duyệt qua danh sách ảnh mẫu
    for i in range(3):
        returning_army_loc = adb.find("assets/template/army_returning.png", threshold=0.8)
        if returning_army_loc is not None:
            return [returning_army_loc[0] - 10, returning_army_loc[1] - 10], "returning"

    for i in range(3):
        full_army_loc = adb.find("assets/template/full_army_5.png", threshold=0.95)
        if full_army_loc is not None:
            print("All army farming!")
            return None, "full_army"

    return None, "not_full_army"
