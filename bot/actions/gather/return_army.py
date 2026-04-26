import time

claim_template_path = "assets/template/claim.png"
return_army_template_path = "assets/template/army_returning.png"
march_continue_template_path = "assets/template/march_continue.png"


def return_army(adb):
    while True:
        claim_loc = adb.find(claim_template_path, threshold=0.8)
        if claim_loc is not None:
            adb.click(*claim_loc)
            time.sleep(2)
            while True:
                army_returning_loc = adb.find(return_army_template_path)
                if army_returning_loc is not None:
                    adb.click(*army_returning_loc)
                    time.sleep(1.2)
                    while True:
                        march_continue_loc = adb.find(march_continue_template_path)
                        if march_continue_loc is not None:
                            adb.click(*march_continue_loc)
                            time.sleep(2)
                            print("Returning army is continue farming!")
                            return
