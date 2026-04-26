import time
from bot.actions.close_popup import close_popup


def open_game(adb, logo_game_path, out_city_template):
    """Open game + tự động zoom out map khi ra ngoài thành phố"""
    print("🎮 Opening game...")

    attempt = 0
    while True:
        try:
            # Tìm và mở game
            loc = adb.find(logo_game_path)
            if loc is not None:
                adb.click(*loc)
                time.sleep(10)  # Đợi load game
                while attempt <= 10:
                    rok_logo_2_loc = adb.find("assets/template/rok_logo_2.png")
                    if rok_logo_2_loc is not None:
                        time.sleep(2)
                        adb.click(*rok_logo_2_loc)
                        time.sleep(10)
                        attempt += 1
                        break

                print("✅ Open game successfully!")

                # Close popup when first open game
                close_popup(adb)

                # Kiểm tra nút ra ngoài thành phố
                print("🔍 Checking out-city button...")
                while True:
                    out_city_loc = adb.find(out_city_template)
                    if out_city_loc is not None:
                        adb.click(*out_city_loc)
                        time.sleep(2)
                        print("✅ Ready to find!")
                        return True

            time.sleep(2)

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
