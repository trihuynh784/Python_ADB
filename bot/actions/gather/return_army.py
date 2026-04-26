import time
from bot.actions.gather.new_army import new_army

return_army_template_path = "assets/template/army_returning.png"
march_continue_template_path = "assets/template/march_continue.png"


def return_army(adb):
    attempt = 0
    while attempt < 5:
        attempt += 1
        army_returning_loc = adb.find(return_army_template_path)
        if army_returning_loc is not None:
            adb.click(*army_returning_loc)
            time.sleep(0.8)
            while True:
                march_continue_loc = adb.find(march_continue_template_path)
                if march_continue_loc is not None:
                    adb.click(*march_continue_loc)
                    time.sleep(0.8)
                    print("Returning army is continue farming!")
                    return

    new_army(adb)
