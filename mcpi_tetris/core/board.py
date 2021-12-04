from typing import List, Optional, Tuple

from .basic import Block, Position
from .tetromino import Tetromino


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