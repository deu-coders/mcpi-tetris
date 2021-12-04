from copy import deepcopy
from typing import List, Tuple

from .basic import Block, Color, Position


TetrominoState = Tuple[Block, Block, Block, Block]


class TetrominoDefinition:
    """테트로미노 모양 정의. (작대기, 사각형 등)"""
    
    states: List[TetrominoState]
    """테트로미노를 구성하는 블록들. 중심 좌표로부터 상대적인 좌표로 블록 구성"""

    width: int = 0
    """테트로미노의 가로 길이"""

    height: int = 0
    """테트로미노의 세로 길이"""
    
    def __init__(self, color: Color, states_str: List[str]):
        """문자열로 부터 테트로미노를 생성"""
        self.states = []

        for state_str in states_str:
            state = []
            x, y = 0, 0

            for ch in state_str.strip():
                if ch == '■':
                    state.append(Block(Position(x, y), color))
                    # 가로, 세로 길이 갱신
                    self.width = max(self.width, x)
                    self.height = max(self.height, y)
                    x += 1

                elif ch == '□':
                    x += 1

                elif ch == '\n':
                    x = 0
                    y -= 1

            self.states.append(tuple(state))
    
    def get_state(self, rotation: int):
        return deepcopy(self.states[rotation % len(self.states)])


class Tetromino:

    position: Position
    """테트로미노의 중심점이 되는 좌표"""

    definition: TetrominoDefinition

    state: TetrominoState
    """현재 테트로미노. 위치 정보까지 포함되어 있음"""

    rotation: int = 0
    """현재 테트로미노의 회전상태에 따른 인덱스 번호. state = states[rotation]"""

    def __init__(self, definition: TetrominoDefinition, position: Position):
        self.definition = definition
        self.position = position
        self.state = self.definition.get_state(self.rotation)

    def fall(self):
        self.position.y -= 1
    
    def rise(self):
        self.position.y += 1

    def left(self):
        self.position.x -= 1
    
    def right(self):
        self.position.x += 1

    def rotate(self):
        self.rotation -= 1
        self.state = self.definition.get_state(self.rotation)
 
    def rotate_reverse(self):
        self.rotation += 1
        self.state = self.definition.get_state(self.rotation)

    def get_blocks(self):
        """현재 테트로미노의 위치 오프셋까지 포함한 블록들을 반환"""
        return tuple(Block(block.position + self.position, block.color) for block in self.state)


class DefaultTetrominoDefinitions:
    SHAPE_I = TetrominoDefinition(Color.LIGHT_BLUE, [
        """
        □■□□
        □■□□
        □■□□
        □■□□
        """,
        """
        □□□□
        ■■■■
        □□□□
        □□□□
        """,
    ])
    SHAPE_J = TetrominoDefinition(Color.DARK_BLUE, [
        """
        □■□
        □■□
        ■■□
        """,
        """
        ■□□
        ■■■
        □□□
        """,
        """
        ■■□
        ■□□
        ■□□
        """,
        """
        ■■■
        □□■
        □□□
        """,
    ])
    SHAPE_L = TetrominoDefinition(Color.ORANGE, [
        """
        ■□□
        ■□□
        ■■□
        """,
        """
        ■■■
        ■□□
        □□□
        """,
        """
        ■■□
        □■□
        □■□
        """,
        """
        □□■
        ■■■
        □□□
        """,
    ])
    SHAPE_O = TetrominoDefinition(Color.YELLOW, [
        """
        ■■
        ■■
        """,
    ])
    SHAPE_S = TetrominoDefinition(Color.GREEN, [
        """
        □■■
        ■■□
        □□□
        """,
        """
        ■□□
        ■■□
        □■□
        """,
    ])
    SHAPE_Z = TetrominoDefinition(Color.RED, [
        """
        ■■□
        □■■
        □□□
        """,
        """
        □■□
        ■■□
        ■□□
        """,
    ])
    SHAPE_T = TetrominoDefinition(Color.MAGENTA, [
        """
        □■□
        ■■■
        □□□
        """,
        """
        ■□□
        ■■□
        ■□□
        """,
        """
        ■■■
        □■□
        □□□
        """,
        """
        □■□
        ■■□
        □■□
        """,
    ])

DefaultTetrominoDefinitions = DefaultTetrominoDefinitions()