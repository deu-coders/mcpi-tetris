from typing import List, Optional, Tuple
import random
import time

from .controller import Controller, TetrisKey
from .display import DisplayAdapter
from .basic import Block, Position
from .tetromino import Tetromino, TetrominoDefinition, DefaultTetrominoDefinitions


class TetrisBoard:
    """테트리스 2차원 구조에 대한 클래스"""

    width: int
    height: int
    blocks: List[List[Optional[Block]]]
    dirty_blocks: List[List[Optional[Block]]]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.blocks = [[None for x in range(width)] for y in range(height)]
        self.dirty_blocks = [[None for x in range(width)] for y in range(height)]

    def get(self, position: Position) -> Optional[Block]:
        return self.dirty_blocks[position.y][position.x]

    def set(self, position: Position, block: Optional[Block]):
        if block is not None:
            block.position = position

        self.dirty_blocks[position.y][position.x] = block

    def set_tetromino(self, tetromino: Tetromino):
        for block in tetromino.get_blocks():
            self.set(block.position, block)

    def remove_tetromino(self, tetromino: Tetromino):
        for block in tetromino.get_blocks():
            self.set(block.position, None)

    def get_dirty(self) -> List[Tuple[Position, Optional[Block]]]:
        collected_dirty = []

        for y in range(self.height):
            for x in range(self.width):
                if self.blocks[y][x] == self.dirty_blocks[y][x]:
                    continue

                self.blocks[y][x] = self.dirty_blocks[y][x]
                collected_dirty.append((Position(x, y), self.blocks[y][x]))

        return collected_dirty

    def has_collision(self, tetromino: Tetromino) -> bool:
        for block in tetromino.get_blocks():
            # check out of bounds
            if block.position.x < 0 or block.position.y < 0 or block.position.x >= self.width or block.position.y >= self.height:
                return True

            # check collision with other blocks
            if self.get(block.position) is not None:
                return True

        return False
    
    def line_completed(self, y: int) -> bool:
        return all(map(lambda x: self.get(Position(x, y)) is not None, range(self.width)))

    def destroy_completed_lines(self) -> int:
        """파괴할 수 있는 라인을 확인하고, 파괴한 후 파괴된 라인의 수를 반환함"""
        destroyed_lines = 0
        new_y = 0

        # scanning lines and destroy
        for y in range(self.height):
            if self.line_completed(y):
                destroyed_lines += 1
                continue

            if new_y != y:
                for x in range(self.width):
                    new_block = self.get(Position(x, y))
                    self.set(Position(x, new_y), new_block)

            new_y += 1

        # clear upside
        for y in range(new_y, self.height):
            for x in range(self.width):
                self.set(Position(x, y), None)
        
        return destroyed_lines


class Tetris:
    """테트리스 게임에 대한 클래스"""

    width: int = 10
    height: int = 20
    display_adapter: DisplayAdapter
    controller: Controller

    tetromino_definitions: List[TetrominoDefinition]
    """정의된 테트로미노 목록"""

    tetromino: Tetromino
    """현재 조작중인 테트로미노"""

    board: TetrisBoard
    """블록 2차원 자료구조. None일 경우 비어있다는 뜻"""

    running: bool = False
    """게임이 진행중인지 여부"""

    tick_rate: int = 20
    """1초당 tick을 실행할 횟수"""

    tick_counter: int = 0
    """게임 내 시간 흐름을 나타내는 단위. 1초당 tick_rate틱"""

    tick_timestamp: int = 0
    """가장 최근의 tick이 실행되었던 시간"""

    speed: int = 1
    """테트로미노가 떨어지는 속도"""

    def __init__(
        self,
        width: int,
        height: int,
        display_adapter: DisplayAdapter,
        controller: Controller,
        tetromino_definitions: Optional[List[TetrominoDefinition]] = None
    ):
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
        self.board.set_tetromino(self.tetromino)

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

    def sleep_until_next_tick(self):
        tick_duration = 1 / self.tick_rate

        previous_tick_elapsed = time.time() - self.tick_timestamp
        sleep_duration = tick_duration - previous_tick_elapsed

        if sleep_duration > 0:
            time.sleep(sleep_duration)

    def get_tetromino_fall_ticks(self) -> int:
        return self.tick_rate - self.speed

    def tick(self):
        self.tick_timestamp = time.time()

        # 키 이벤트 확인
        key = self.controller.pop()

        if key is not None:
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