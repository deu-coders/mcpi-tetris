from typing import List, Optional

from .basic import Block, Color, Position


class DisplayAdapter:
    """
    다양한 디스플레이를 지원하기 위한 어답터 클래스
    """

    width: int
    height: int

    def __init__(self):
        pass

    def preinitialize(self, width: int, height: int):
        self.width = width
        self.height = height

        self.initialize()

    def initialize(self):
        """
        처음 게임을 시작할 때, 지정된 크기로 게임 보드를 초기화하기 위해 호출되는 함수
        """
        pass

    def onblockchange(self, position: Position, block: Optional[Block]):
        """
        특정 픽셀에 변화가 생길 때 호출되는 함수. 블록이 없어진 경우 None으로 주어짐.
        """
        pass
    
    def onlinecompleted(self, destroyed_lines: int):
        """
        라인이 파괴되었을 때 호출되는 함수
        """
        pass

    def ongameover(self):
        """
        게임 오버되었을 때 호출되는 함수
        """
        pass

    def requestnextframe(self):
        """
        다음 화면을 그릴 때 호출되는 함수
        """
        pass

    def close(self):
        """
        게임이 종료될 때 호출되는 함수
        """
        pass


class ConsoleDisplayAdapter(DisplayAdapter):

    pixels: List[List[Optional[Color]]]

    def initialize(self):
        self.pixels = [[None for x in range(self.width)] for y in range(self.height)]
    
    def onblockchange(self, position: Position, block: Optional[Block]):
        self.pixels[position.y][position.x] = None if block is None else block.color

    def requestnextframe(self):
        for y in reversed(range(self.height)):
            for x in range(self.width):
                print('□' if self.pixels[y][x] is None else '■', end='')
            
            print()

        print('\n\n', end='')
