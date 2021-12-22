from collections import deque
from typing import Deque, List, Optional, Tuple
from mcpi_tetris.core.controller import Controller, TetrisKey
from mcpi_tetris.config import config


class RecordedController(Controller):

    logs: Deque[Tuple[int, TetrisKey]]

    def initialize(self):
        self.logs = deque()

        # Join self
        self.logs.append((0, TetrisKey.JOIN))

        filename = config.get('play_recorded')
        with open(f'logs/play-{filename}.log', 'r', encoding='utf-8') as file:
            lines = file.read().split('\n')

            data = {key: value for key, value in map(lambda token: token.split('='), lines[0].split(','))}
            self.player.setseed(int(data['seed']))

            for line in lines[1:]:
                if len(line.strip()) == 0:
                    continue

                tick, key = line.split(':')
                tick = int(tick)
                self.logs.append((tick, TetrisKey[key]))

    def pop(self) -> Optional[TetrisKey]:
        if len(self.logs) == 0:
            return None

        tick, key = self.logs[0]
        if tick <= self.tick_counter:
            self.logs.popleft()
            return key

        return None
