
from typing import List, Optional, TYPE_CHECKING
import random

from .basic import Position
from .controller import Controller, TetrisKey
from .display import DisplayAdapter
from .board import TetrisBoard
from .tetromino import DefaultTetrominoDefinitions, Tetromino, TetrominoDefinition

if TYPE_CHECKING:
    from .game import TetrisGame


class TetrisPlayer:
    """테트리스 게임에 대한 클래스"""

    game: 'TetrisGame'
    """테트리스 게임 인스턴스"""

    width: int = 10
    """테트리스의 가로 크기"""

    height: int = 20
    """테트리스의 세로 크기"""

    display_adapter: DisplayAdapter
    """진행중인 내용이 표시될 디스플레이"""

    controller: Controller
    """플레이어를 조작중인 Controller"""

    tetromino_definitions: List[TetrominoDefinition]
    """정의된 테트로미노 목록"""

    tetromino: Tetromino
    """현재 조작중인 테트로미노"""

    board: TetrisBoard
    """블록 2차원 자료구조. None일 경우 비어있다는 뜻"""

    playing: bool = True
    """게임 진행 중인지 여부"""

    tick_counter: int = 0
    """게임 내 시간 흐름을 나타내는 단위. 1초당 tick_rate틱"""

    speed: int = 1
    """테트로미노가 떨어지는 속도"""

    destroyed_lines: int = 0
    """플레이 중 부순 라인 수"""

    def __init__(
        self,
        game: 'TetrisGame',
        width: int,
        height: int,
        display_adapter: DisplayAdapter,
        controller: Controller,
        tetromino_definitions: Optional[List[TetrominoDefinition]] = None,
    ):
        self.game = game

        self.width = width
        self.height = height

        self.display_adapter = display_adapter
        self.display_adapter.preinitialize(width, height)

        self.controller = controller
        self.controller.preinitialize()

        if tetromino_definitions is None:
            tetromino_definitions = [
                DefaultTetrominoDefinitions.SHAPE_I,
                DefaultTetrominoDefinitions.SHAPE_J,
                DefaultTetrominoDefinitions.SHAPE_L,
                DefaultTetrominoDefinitions.SHAPE_O,
                DefaultTetrominoDefinitions.SHAPE_S,
                DefaultTetrominoDefinitions.SHAPE_Z,
                DefaultTetrominoDefinitions.SHAPE_T,
            ]
        
        self.tetromino_definitions = tetromino_definitions
        self.board = TetrisBoard(width, height)

        self.next_tetromino()
    
    def next_tetromino(self):
        self.tetromino = Tetromino(
            random.choice(self.tetromino_definitions),
            Position(self.width // 2, self.height - 1)
        )

        # Check Game Over
        if self.board.has_collision(self.tetromino):
            self.kill()

        self.board.set_tetromino(self.tetromino)
    
    def kill(self):
        self.playing = False
        self.display_adapter.ongameover()

    def fall(self):
        """테트로미노가 떨어짐"""
        self.board.remove_tetromino(self.tetromino)
        self.tetromino.fall()

        has_collision = self.board.has_collision(self.tetromino)
        if has_collision:
            self.tetromino.rise() # undo fall

        self.board.set_tetromino(self.tetromino)

        if has_collision:
            # 테트로미노 설치 시 라인 스캐닝 후 파괴
            destroyed_lines = self.board.destroy_completed_lines()
            if destroyed_lines > 0:
                self.display_adapter.onlinecompleted(destroyed_lines)
                self.game.onlinecompleted()
                self.destroyed_lines += destroyed_lines

            # 다음 테트로미노 생성
            self.next_tetromino()
    
    def land(self):
        """테트로미노를 즉각 떨어트리는 함수"""
        self.board.remove_tetromino(self.tetromino)

        while not self.board.has_collision(self.tetromino):
            self.tetromino.fall()

        self.tetromino.rise() # 충돌이 된 후 한번 올려주기
        self.board.set_tetromino(self.tetromino)

        destroyed_lines = self.board.destroy_completed_lines()
        if destroyed_lines > 0:
            self.display_adapter.onlinecompleted(destroyed_lines)
        
        self.next_tetromino()

    def rotate(self):
        """테트로미노를 회전함"""
        self.board.remove_tetromino(self.tetromino)
        self.tetromino.rotate()

        if self.board.has_collision(self.tetromino):
            self.tetromino.rotate_reverse() # undo rotate

        self.board.set_tetromino(self.tetromino)
    
    def left(self):
        """테트로미노를 왼쪽 방향으로 움직임"""
        self.board.remove_tetromino(self.tetromino)
        self.tetromino.left()

        if self.board.has_collision(self.tetromino):
            self.tetromino.right()
        
        self.board.set_tetromino(self.tetromino)

    def right(self):
        """테트로미노를 오른쪽 방향으로 움직임"""
        self.board.remove_tetromino(self.tetromino)
        self.tetromino.right()

        if self.board.has_collision(self.tetromino):
            self.tetromino.left()

        self.board.set_tetromino(self.tetromino)

    def get_tetromino_fall_ticks(self) -> int:
        return max(1, 20 - self.speed)

    def tick(self):
        if self.playing:
            # 키 이벤트 확인
            while True:
                key = self.controller.pop()
                if key is None:
                    break

                if key == TetrisKey.UP:
                    self.rotate()
                elif key == TetrisKey.DOWN:
                    self.fall()
                elif key == TetrisKey.LEFT:
                    self.left()
                elif key == TetrisKey.RIGHT:
                    self.right()
                elif key == TetrisKey.LAND:
                    self.land()

            # 테트로미노가 떨어질 타이밍인지 확인
            if self.tick_counter % self.get_tetromino_fall_ticks() == 0:
                self.fall()

        # 디스플레이 업데이트
        self.flush_display()
        self.tick_counter += 1

    def flush_display(self):
        dirty = self.board.get_dirty()
        if len(dirty) == 0:
            return # no updates

        for position, block in dirty:
            self.display_adapter.onblockchange(position, block)

        self.display_adapter.requestnextframe()
    
    def close(self):
        # clear resources
        self.display_adapter.close()
        self.controller.close()