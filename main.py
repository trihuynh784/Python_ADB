from bot.Auto_Bot import AutoBot
from services.adb_service import ADB
from config import DEVICE_NAME
import time


def main():
    # Khoi tao ADB_Service, Bot
    adb = ADB(DEVICE_NAME)
    autoBot = AutoBot(DEVICE_NAME, adb)

    # Run the game
    # autoBot.open_game()
    # Map zoom out
    autoBot.map_zoomout()

    while True:
        return_army_loc, status = autoBot.check_status_army()

        if status == "not_full_army":
            loc = autoBot.scan_gem()
            while loc is None:
                adb.swipe_escape_area()
                loc = autoBot.scan_gem()
            adb.click(*loc)
            time.sleep(1.5)
            autoBot.gather(status)
        elif status == "returning":
            adb.click(*return_army_loc)
            time.sleep(0.8)
            loc = autoBot.scan_gem()
            while loc is None:
                adb.swipe_escape_area()
                loc = autoBot.scan_gem()
            adb.click(*loc)
            time.sleep(1.5)
            autoBot.gather(status)

        time.sleep(5)


if __name__ == "__main__":
    main()
