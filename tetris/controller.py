from collections import deque
from enum import Enum
from typing import Optional
import keyboard


class TetrisKey(Enum):
    DOWN = 'down'
    UP = 'up'
    LEFT = 'left'
    RIGHT = 'right'
    LAND = 'land'


class Controller:

    queue: deque

    def __init__(self):
        self.queue = deque()

    def preinitialize(self):
        self.initialize()

    def initialize(self):
        pass

    def push(self, key: TetrisKey):
        self.queue.appendleft(key)

    def pop(self) -> Optional[TetrisKey]:
        if len(self.queue) == 0:
            return None

        return self.queue.pop()

    def close(self):
        pass


class KeyboardArrowController(Controller):

    def onkeypress(self, key: str):
        if key == 'up':
            self.push(TetrisKey.UP)
        elif key == 'down':
            self.push(TetrisKey.DOWN)
        elif key == 'left':
            self.push(TetrisKey.LEFT)
        elif key == 'right':
            self.push(TetrisKey.RIGHT)
        elif key == 'space':
            self.push(TetrisKey.LAND)

    def initialize(self):
        self.handler = keyboard.on_press(lambda event: self.onkeypress(event.name))

    def close(self):
        keyboard.unhook(self.handler)


class KeyboardWASDController(Controller):

    def onkeypress(self, key:  str):
        if key == 'w':
            self.push(TetrisKey.UP)
        elif key == 's':
            self.push(TetrisKey.DOWN)
        elif key == 'a':
            self.push(TetrisKey.LEFT)
        elif key == 'd':
            self.push(TetrisKey.RIGHT)
        elif key == 'f':
            self.push(TetrisKey.LAND)
    
    def initialize(self):
        self.handler = keyboard.on_press(lambda event: self.onkeypress(event.name))
    
    def close(self):
        keyboard.unhook(self.handler)