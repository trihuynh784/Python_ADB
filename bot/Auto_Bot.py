from bot.actions.open_game import open_game
from bot.actions.map_zoom import map_zoomout
from bot.actions.check_status_army import check_status_army
from bot.actions.scan_gem import scan_gem
from bot.actions.gather.new_army import new_army
from bot.actions.gather.return_army import return_army
from bot.actions.close_popup import close_popup
from bot.actions.mine_mark.mine_mark_handle import (
    get_list_location_mine,
    set_mine_into_list,
    open_mine_marked,
)
import time


class AutoBot:

    def __init__(self, deviceId, adb):
        self.deviceId = deviceId
        self.adb = adb
        self.list_marked_mines = []
        self.list_go_location = []

    def open_game(self):
        open_game(
            self.adb, "assets/template/rok_logo.png", "assets/template/out_city.png"
        )

    def map_zoomout(self):
        map_zoomout(self.adb)

    def check_status_army(self):
        return check_status_army(self.adb)

    def scan_gem(self):
        close_popup(self.adb)
        template_gem_list = [
            "assets/template/gem_1.png",
            "assets/template/gem_1_light_variant.png",
            "assets/template/gem_1_ver_2.png",
            # "assets/template/gem_2.png",
            # "assets/template/gem_3.png",
        ]
        loc = scan_gem(self.adb, template_gem_list)
        if loc is None:
            return None
        return [loc[0], loc[1] - 10]

    def gather(self, gather_type="not_full_army"):
        while True:  # Chạy cho đến khi nào đi quân thành công thì thôi
            loc_big_gem = self.adb.find("assets/template/big_gem.png")

            if loc_big_gem is None:
                print("Không thấy big_gem, đang di chuyển vùng khác để tìm...")
                self.map_zoomout()
                self.adb.swipe_escape_area()

                # Gọi scan_gem để tìm tọa độ mỏ mới
                gem_loc = self.scan_gem()

                # Nếu scan_gem cũng không thấy, tiếp tục thoát xác sang vùng xa hơn
                while gem_loc is None:
                    self.adb.swipe_escape_area()
                    gem_loc = self.scan_gem()

                # Sau khi scan_gem đã đưa camera tới chỗ có mỏ,
                # vòng lặp 'while True' sẽ quay lại bước tìm 'big_gem' ở đầu.
                continue

            # --- Bước Click và Đi quân ---
            print(f"Click vào mỏ Gem tại: {loc_big_gem}")
            self.adb.click(*loc_big_gem)
            time.sleep(1.2)

            claim_loc = None
            for temp in [
                "assets/template/claim.png",
                "assets/template/claim_2.png",
                "assets/template/claim_3.png",
            ]:
                claim_loc = self.adb.find(temp, threshold=0.8)
                if claim_loc:
                    break

            if claim_loc:
                self.adb.click(*claim_loc)
                time.sleep(1.0)

                if gather_type == "returning":
                    return_army(self.adb)
                else:
                    new_army(self.adb)

                self.map_zoomout()
                self.adb.swipe_escape_area()
                return  # <--- QUAN TRỌNG: Thoát hàm khi đã đi quân THÀNH CÔNG
            else:
                print("Mỏ lỗi hoặc đã bị chiếm, tìm mỏ khác...")
                self.adb.swipe_escape_area()  # Vuốt đi chỗ khác để tránh kẹt ở mỏ này
                continue  # Quay lại đầu vòng lặp để tìm mỏ khác
