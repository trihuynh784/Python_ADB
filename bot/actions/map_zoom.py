import time


def map_zoomout(adb):
    adb.draganddrop(60, 655, 60, 655, 1000)
    adb.click(255, 560)
    time.sleep(0.4)
    print("✅ Map zoomed out completely!")
