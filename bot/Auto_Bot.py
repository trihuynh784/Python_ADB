from bot.actions.open_game import open_game
from bot.actions.map_zoom import map_zoomout
from bot.actions.check_status_army import check_status_army
from bot.actions.scan_gem import scan_gem
from bot.actions.gather.new_army import new_army
from bot.actions.gather.return_army import return_army
from bot.actions.close_popup import close_popup
from services.util_service import check_safe_distance
import time, subprocess


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
            "assets/template/gems/gem_1.png",
            "assets/template/gems/gem_2.png",
            # "assets/template/gems/gem_3.png",
        ]
        loc = scan_gem(self.adb, template_gem_list)
        if loc is None:
            return None
        return [loc[0], loc[1] - 10]

    def gather(self, gather_type="not_full_army"):
        while True:
            loc_big_gem = self.adb.find("assets/template/big_gem.png")

            while loc_big_gem is None:
                print("Không thấy big_gem, đang di chuyển vùng khác để tìm...")
                self.map_zoomout()
                safe_distance = check_safe_distance(self.adb)
                if safe_distance is not None:
                    self.adb.swipe_escape_area(*safe_distance)
                else:
                    self.adb.swipe_escape_area()

                # Gọi scan_gem để tìm tọa độ mỏ mới
                gem_loc = self.scan_gem()

                # Nếu scan_gem cũng không thấy, tiếp tục thoát xác sang vùng xa hơn
                while gem_loc is None:
                    safe_distance = check_safe_distance(self.adb)
                    if safe_distance is not None:
                        self.adb.swipe_escape_area(*safe_distance)
                    else:
                        self.adb.swipe_escape_area()
                    gem_loc = self.scan_gem()

                self.adb.click(*gem_loc)
                time.sleep(1.5)

                loc_big_gem = self.adb.find("assets/template/big_gem.png")

            # --- Bước Click và Đi quân ---
            print(f"Click vào mỏ Gem tại: {loc_big_gem}")
            self.adb.click(*loc_big_gem)
            time.sleep(1)

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
                    is_full_payload = return_army(self.adb)
                    if is_full_payload == "full_payload":
                        self.adb.click(*loc_big_gem)
                        time.sleep(0.6)
                else:
                    new_army(self.adb)

                self.map_zoomout()
                safe_distance = check_safe_distance(self.adb)
                if safe_distance is not None:
                    self.adb.swipe_escape_area(*safe_distance)
                else:
                    self.adb.swipe_escape_area()
                return
            else:
                print("Mỏ lỗi hoặc đã bị chiếm, tìm mỏ khác...")
                self.map_zoomout()

                safe_distance = check_safe_distance(self.adb)
                if safe_distance is not None:
                    self.adb.swipe_escape_area(*safe_distance)
                else:
                    self.adb.swipe_escape_area()
