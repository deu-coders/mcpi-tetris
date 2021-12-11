from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, List
from mcpi_tetris.core.controller import TetrisKey

if TYPE_CHECKING:
    from ..core.player import TetrisPlayer


class KeyLogger:

    player: 'TetrisPlayer'

    def __init__(self, player: 'TetrisPlayer') -> None:
        self.player = player
    
    def onkeypress(self, key: TetrisKey):
        print(f'player_id={self.player.controller.player_id}, key={key}')

    def close(self):
        pass


class FileAttachedKeyLogger(KeyLogger):

    file: TextIOWrapper
    seed: int

    def __init__(self, player: 'TetrisPlayer') -> None:
        super().__init__(player)
        self.seed = player.seed

        Path('logs').mkdir(parents=True, exist_ok=True)
        self.file = open(f'logs/play-{self.seed}.log', 'w', encoding='utf-8')
        self.file.write(f'width={player.width},height={player.height},player_id={player.controller.player_id},seed={player.seed}\n')

    def onkeypress(self, key: TetrisKey):
        super().onkeypress(key)
        self.file.write(f'{self.player.tick_counter}:{key.value}\n')

    def close(self):
        self.file.close()