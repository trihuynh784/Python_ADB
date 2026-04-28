import os


def map_zoomout(adb):
    adb.draganddrop(60, 655, 236, 566, 1000)
    print("✅ Map zoomed out completely!")
