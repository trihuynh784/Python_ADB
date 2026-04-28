import time

new_army_template_path = "assets/template/new_army.png"
slots_template_path = [
    "assets/template/slot_1.png",
    "assets/template/slot_2.png",
    "assets/template/slot_3.png",
    "assets/template/slot_4.png",
    "assets/template/slot_5.png",
    "assets/template/slot_6.png",
    "assets/template/slot_7.png",
]
march_template_path = "assets/template/march.png"


def new_army(adb):
    for i in range(5):
        new_army_loc = adb.find(new_army_template_path, threshold=0.8)
        if new_army_loc is not None:
            adb.click(*new_army_loc)
            time.sleep(0.5)
            for index in range(len(slots_template_path)):
                slot_loc = adb.find(slots_template_path[index], threshold=0.8)
                if slot_loc is not None:
                    adb.click(*slot_loc)
                    time.sleep(0.5)
            while True:
                march_loc = adb.find(march_template_path, threshold=0.8)
                if march_loc is not None:
                    adb.click(*march_loc)
                    time.sleep(0.5)
                    print("Take new army to farm success!")
                    return
    
    adb.click(600, 360)
    time.sleep(0.6)
