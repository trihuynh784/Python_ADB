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
            time.sleep(0.5)
            if is_full_payload(adb):
                return "full_payload"

            for i in range(5):
                march_continue_loc = adb.find(march_continue_template_path)
                if march_continue_loc is not None:
                    adb.click(*march_continue_loc)
                    time.sleep(0.5)
                    print("Returning army is continue farming!")
                    return "success"

            new_army(adb)

    new_army(adb)


def is_full_payload(adb):
    full_payload = adb.find_with_color("assets/template/is_full_payload.png")
    if full_payload:
        return True
    return False
