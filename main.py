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
    # autoBot.map_zoomout()

    while True:
        loc, status = autoBot.check_status_army()
        if status == "not_full_army":
            print("Ready to gather gem!")
            autoBot.process_marked_mines(loc, status)
        elif status == "returning":
            print("Ready to gather gem!")
            autoBot.process_marked_mines(loc, status)
        else:
            print("All done!")

        time.sleep(5)


if __name__ == "__main__":
    main()
