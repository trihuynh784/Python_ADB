from bot.Auto_Bot import AutoBot
from services.adb_service import ADB
from services.util_service import check_safe_distance
import time
from bot.actions.close_popup import close_popup

from config import DEVICE_NAME


def initBot():
    # Khoi tao ADB_Service, Bot
    adb = ADB(DEVICE_NAME)
    autoBot = AutoBot(
        DEVICE_NAME,
        adb,
    )

    # Run the game
    # autoBot.open_game()
    autoBot.map_zoomout()

    while True:
        return_army_loc, status = autoBot.check_status_army()

        if status == "not_full_army":
            # ve gan nha
            home_loc = adb.find("assets/template/home_location.png")
            if home_loc is not None:
                adb.click(*home_loc)
                time.sleep(0.6)

            loc = autoBot.scan_gem()
            while loc is None:
                safe_distance = check_safe_distance(adb)
                if safe_distance is not None:
                    adb.swipe_escape_area(*safe_distance)
                else:
                    adb.swipe_escape_area()
                loc = autoBot.scan_gem()
            adb.click(*loc)
            time.sleep(1.5)
            close_popup(adb)
            autoBot.gather(status)
        elif status == "returning":
            adb.click(*return_army_loc)
            time.sleep(0.8)
            loc = autoBot.scan_gem()
            while loc is None:
                safe_distance = check_safe_distance(adb)
                if safe_distance is not None:
                    adb.swipe_escape_area(*safe_distance)
                else:
                    adb.swipe_escape_area()
                loc = autoBot.scan_gem()
            adb.click(*loc)
            time.sleep(1.5)
            close_popup(adb)
            autoBot.gather(status)

        time.sleep(5)


if __name__ == "__main__":
    initBot()
