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

    def open_game(self):
        open_game(
            self.adb, "assets/template/rok_logo.png", "assets/template/out_city.png"
        )

    def map_zoomout(self):
        map_zoomout()

    def check_status_army(self):
        return check_status_army(self.adb)

    def scan_gem(self):
        template_gem_list = [
            "assets/template/gem_1.png",
            "assets/template/gem_2.png",
            "assets/template/gem_3.png",
        ]
        x, y = scan_gem(self.adb, template_gem_list, 50)
        return x, y - 10

    def gather(self, loc, type="returning" or "not_full_army"):
        for attempt in range(2):
            if attempt == 0:
                self.adb.click(*loc)
                time.sleep(1.2)
                loc_big_gem = self.adb.find("assets/template/big_gem.png")
                if loc_big_gem is None:
                    # Tìm mỏ chỗ khác
                    return
                self.adb.click(*loc_big_gem)
                time.sleep(1.2)

                set_mine_into_list(self.adb, self.list_marked_mines)
                self.adb.click(*loc_big_gem)
                time.sleep(1.2)
            else:
                loc_big_gem = self.adb.find("assets/template/big_gem.png")
                if loc_big_gem is None:
                    # Tìm mỏ chỗ khác
                    return
                self.adb.click(*loc_big_gem)
                time.sleep(2)
                if type == "returning":
                    # todo: let take the army's return and farm this gem mine
                    return_army(self.adb)
                    self.map_zoomout()
                    self.adb.swipe_escape_area()
                else:
                    # todo: take new army to farm
                    new_army(self.adb)
                    self.map_zoomout()
                    self.adb.swipe_escape_area()

    def process_marked_mines(self, loc, type="returning" or "not_full_army"):
        if type == "not_full_army":
            # Get marked mines
            self.get_list_marked_mine()

            # foreach list
            if len(self.list_marked_mines):
                for mine in self.list_marked_mines:
                    attempt = 0
                    while attempt <= 10:
                        go_loc = self.adb.find("assets/template/go.png")
                        if go_loc is not None:
                            self.adb.click(*go_loc)
                            time.sleep(2.4)
                            gem_loc = self.scan_gem()
                            self.gather(gem_loc, type)
                            # reopen window mine marked
                            open_mine_marked(self.adb)
                            # delete first marked mine
                            self.delete_mine()
                            attempt += 1
                            break
            else:
                close_popup(self.adb)
                gem_loc = self.scan_gem()
                self.gather(gem_loc, type)

        else:
            self.adb.click(*loc)
            time.sleep(1.8)
            gem_loc = self.scan_gem()
            self.gather(gem_loc, type)

    def delete_mine(self):
        while True:
            delete_mine_loc = self.adb.find("assets/template/delete_mine.png")
            if delete_mine_loc is not None:
                self.adb.click(*delete_mine_loc)
                self.list_marked_mines.pop(0)
                time.sleep(1.5)
                break

    # Util function to get list marked
    def get_list_marked_mine(self):
        open_mine_marked(self.adb)
        list = get_list_location_mine()
        if len(list):
            for mine in list:
                if mine in self.list_marked_mines:
                    print("Mine [" + mine.x + ", " + mine.y + "] is exist on list!")
                else:
                    self.list_marked_mines.append(mine)
        print(self.list_marked_mines)
        return
