class Position:
    def __init__(self, x: int, y: int, angle: float = 0):
        self.x: int = x
        self.y: int = y
        self.angle: float = angle

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.angle

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.angle)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self):
        return f"({self.x}, {self.y}), angle is {self.angle}"

    def dist(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
