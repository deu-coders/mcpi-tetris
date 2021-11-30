from enum import Enum


class Position:
    """게임 내에서 블록의 좌표 값을 다루기 위한 클래스"""
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        
        return False
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __str__(self):
        return f'(x={self.x}, y={self.y})'


class Color(Enum):
    """블록의 색깔들을 열거형으로 표현하기 위한 클래스"""
    LIGHT_BLUE = 1
    DARK_BLUE = 2
    ORANGE = 3
    YELLOW = 4
    GREEN = 5
    RED = 6
    MAGENTA = 7


class Block:
    """테트로미노 또는 픽셀을 구성하는 블록 클래스"""
    position: Position
    color: Color

    def __init__(self, position: Position, color: Color):
        self.position = position
        self.color = color
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Block):
            return self.position == other.position and self.color == other.color
        
        return False