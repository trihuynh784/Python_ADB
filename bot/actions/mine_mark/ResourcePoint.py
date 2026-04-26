from dataclasses import dataclass


@dataclass
class ResourcePoint:
    x: int
    y: int

    # Hàm này giúp bạn in ra màn hình dễ nhìn hơn khi debug
    def __repr__(self):
        return f"Mỏ(X:{self.x}, Y:{self.y})"
