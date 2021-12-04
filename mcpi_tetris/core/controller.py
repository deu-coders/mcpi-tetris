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

    JOIN = 'join'
    LEAVE = 'leave'
    START = 'start'


class Controller:
    """
    입력 장치를 나타내는 추상 클래스
    """

    player_id: int
    queue: deque

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.queue = deque()

    def get_description(self):
        return """
        비어있는 컨트롤러입니다. 구현이 필요합니다.
        """

    def preinitialize(self):
        self.queue = deque()
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
    """
    클라이언트 측에서 화살표를 사용한 키보드 입력을 받을 때 사용하는 Controller
    """

    def get_description(self):
        return """
        ↑: 테트로미노 회전
        ←, →: 테트로미노 이동
        ↓: 테트로미노 아래로 이동
        SPACE: 테트로미노 바로 설치

        j: 게임 참여
        k: 게임 나가기
        l: 게임 시작
        """

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

        elif key == 'j':
            self.push(TetrisKey.JOIN)
        elif key == 'k':
            self.push(TetrisKey.LEAVE)
        elif key == 'l':
            self.push(TetrisKey.START)

    def initialize(self):
        self.handler = keyboard.on_press(lambda event: self.onkeypress(event.name))

    def close(self):
        keyboard.unhook(self.handler)


class KeyboardWASDController(Controller):
    """
    클라이언트 측에서 WASD를 사용한 키보드 입력을 받을 때 사용하는 Controller
    """

    def get_description(self):
        return """
        w: 테트로미노 회전
        a, d: 테트로미노 이동
        s: 테트로미노 아래로 이동
        f: 테트로미노 바로 설치

        e: 게임 참여
        r: 게임 나가기
        t: 게임 시작
        """

    def onkeypress(self, key: str):
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

        elif key == 'e':
            self.push(TetrisKey.JOIN)
        elif key == 'r':
            self.push(TetrisKey.LEAVE)
        elif key == 't':
            self.push(TetrisKey.START)
    
    def initialize(self):
        self.handler = keyboard.on_press(lambda event: self.onkeypress(event.name))
    
    def close(self):
        keyboard.unhook(self.handler)


class StdinController(Controller):
    """
    파이썬 표준입력을 통해 조작하는 Controller입니다.
    표준 입력을 받는동안 쓰레드가 Blocking되기 때문에, 게임 실행과 동시에 사용하면 안됩니다.
    """

    def get_description(self):
        return """
        w: 테트로미노 회전
        a, d: 테트로미노 이동
        s: 테트로미노 아래로 이동
        f: 테트로미노 바로 설치

        e: 게임 참여
        r: 게임 나가기
        t: 게임 시작
        """

    def str_to_key(self, key: str) -> Optional[TetrisKey]:
        key = key.strip()

        if key == 'w':
            return TetrisKey.UP
        elif key == 's':
            return TetrisKey.DOWN
        elif key =='a':
            return TetrisKey.LEFT
        elif key == 'd':
            return TetrisKey.RIGHT
        elif key == 'f':
            return TetrisKey.LAND

        elif key == 'e':
            return TetrisKey.JOIN
        elif key == 'r':
            return TetrisKey.LEAVE
        elif key == 't':
            return TetrisKey.START

        else:
            print(f'Unknown input: {key}')

        return None

    def pop(self) -> Optional[TetrisKey]:
        print(self.get_description())
        key = input('Your input: ')

        return self.str_to_key(key)