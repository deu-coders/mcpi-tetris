
from typing import List, Optional, TYPE_CHECKING
from random import Random
import time

from mcpi_tetris.record.logger import KeyLogger

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

    speed_incrementer_tick_rate: int = 200
    """스피드가 올라가는 속도. 기본값=200틱마다 스피드 1씩 증가"""

    speed: int = 1
    """테트로미노가 떨어지는 속도"""

    destroyed_lines: int = 0
    """플레이 중 부순 라인 수"""

    seed: Optional[int]
    """랜덤 함수에 적용되는 시드 값"""

    random: Random
    """플레이어에 독립적인 랜덤 인스턴스"""

    logger: KeyLogger

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
        self.controller = controller

        self.tetromino_definitions = tetromino_definitions if tetromino_definitions is not None else [
            DefaultTetrominoDefinitions.SHAPE_I,
            DefaultTetrominoDefinitions.SHAPE_J,
            DefaultTetrominoDefinitions.SHAPE_L,
            DefaultTetrominoDefinitions.SHAPE_O,
            DefaultTetrominoDefinitions.SHAPE_S,
            DefaultTetrominoDefinitions.SHAPE_Z,
            DefaultTetrominoDefinitions.SHAPE_T,
        ]
        self.board = TetrisBoard(width, height)

        self.seed = 1640170508
        self.random = Random()
        self.random.seed(self.seed)

        self.logger = KeyLogger(self)

        self.display_adapter.preinitialize(self)
        self.controller.preinitialize()

        self.next_tetromino()

    def setlogger(self, logger: KeyLogger):
        self.logger = logger

    def setseed(self, seed: int):
        self.seed = seed
        self.random.seed(seed)

    def next_tetromino(self):
        self.tetromino = Tetromino(
            self.random.choice(self.tetromino_definitions),
            Position(self.width // 2, self.height - 1)
        )

        # Check Game Over
        if self.board.has_collision(self.tetromino):
            self.kill()

        self.board.set_tetromino(self.tetromino)
    
    def kill(self):
        self.playing = False
        self.display_adapter.ongameover()
        self.game.ongameover(self.controller.player_id)

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
                self.onlinecompleted(destroyed_lines)

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
            self.onlinecompleted(destroyed_lines)
        
        self.next_tetromino()

    def onlinecompleted(self, destroyed_lines: int):
        self.destroyed_lines += destroyed_lines
        self.display_adapter.onlinecompleted(destroyed_lines)
        self.game.onlinecompleted(self.controller.player_id, destroyed_lines)

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
        return max(5, 20 - self.speed)

    def tick(self):
        if self.playing:
            # 컨트롤러의 tick_counter값을 업데이트
            self.controller.tick_counter = self.tick_counter

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

                else:
                    continue # 다른 키는 무시

                # 키 입력 기록
                self.logger.onkeypress(key)

            # 테트로미노가 떨어질 타이밍인지 확인
            if self.tick_counter % self.get_tetromino_fall_ticks() == 0:
                self.fall()

            # 테트로미노의 스피드를 점점 증가 (최초엔 skip하기 위해 1을 더함)
            if (self.tick_counter + 1) % self.speed_incrementer_tick_rate == 0:
                self.speed += 1

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
        self.logger.close()