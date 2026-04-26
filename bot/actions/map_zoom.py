from services.utils_service import zoom_out
import time


def map_zoomout():
    zoom_out()
    time.sleep(1.5)  # Đợi zoom hoàn thành
    print("✅ Map zoomed out completely!")