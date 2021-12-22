from typing import Dict
import time

from mcpi_tetris.record.logger import FileAttachedKeyLogger

from .player import TetrisPlayer
from .controller import Controller, KeyboardArrowController, TetrisKey
from .display import ConsoleDisplayAdapter
from mcpi_tetris.config import config


class TetrisGame:

    controllers: Dict[str, Controller]
    """키 입력을 담당하는 객체들"""

    players: Dict[str, TetrisPlayer]
    """테트리스 게임에 참여한 플레이어들"""

    playing: bool = False
    """테트리스 게임이 플레이중인지 여부"""

    tick_rate: int = 20
    """1초당 tick을 실행할 횟수"""

    tick_counter: int = 0
    """게임 내 시간 흐름을 나타내는 단위. 1초당 tick_rate틱"""

    tick_timestamp: int = 0
    """가장 최근의 tick이 실행되었던 시간"""

    def __init__(self):
        self.controllers = {}
        self.players = {}

    def add_controller(self, controller: Controller):
        self.controllers[controller.player_id] = controller
    
    def get_controller(self, player_id: int):
        return self.controllers[player_id]

    def remove_controller(self, player_id: int):
        if self.is_joined(player_id):
            self.leave(player_id)

        del self.controllers[player_id]

    def create_player(self, player_id: int) -> TetrisPlayer:
        return TetrisPlayer(
            game=self,
            width=10,
            height=20,
            controller=KeyboardArrowController(),
            display_adapter=ConsoleDisplayAdapter(),
        )
    
    def print_message(self, message: str):
        print(f'[Tetris] {message}')

    def is_joined(self, player_id: int):
        return player_id in self.players

    def join(self, player_id: int):
        if self.is_joined(player_id):
            self.print_message(f'Player {player_id} is already joined tetris.')
            return

        player = self.create_player(player_id)
        if config.get('record'):
            player.setlogger(FileAttachedKeyLogger(player))

        self.players[player_id] = player
        self.print_message(f'Player {player_id} joined tetris.')

    def leave(self, player_id: int):
        if not self.is_joined(player_id):
            self.print_message(f'Player {player_id} is not in tetris.')
            return

        self.players[player_id].close()
        del self.players[player_id]
        self.print_message(f'Player {player_id} leave tetris.')

    def start(self):
        if self.playing:
            self.print_message('Tetris is already playing.')
            return

        self.playing = True
        self.print_message(f'Start tetris game!!')

    def stop(self):
        self.prestop()
        if not self.playing:
            self.print_message(f'Tetris is not playing.')
            return

        for player_id in list(self.players):
            self.leave(player_id)

        self.playing = False
        self.poststop()
        self.print_message('Tetris game end!!')

    def prestop(self):
        pass

    def poststop(self):
        pass

    def run(self):
        while True:
            try:
                self.tick()
            except KeyboardInterrupt:
                # Force shutdown game (Ctrl+c)
                self.print_message('Shutdown game ...')
                self.stop()
                break

    def sleep_until_next_tick(self):
        tick_duration = 1 / self.tick_rate

        previous_tick_elapsed = time.time() - self.tick_timestamp
        sleep_duration = tick_duration - previous_tick_elapsed

        if sleep_duration > 0:
            time.sleep(sleep_duration)

    def tick(self):
        self.tick_timestamp = time.time()
        self.pretick()

        # not playing (waiting)
        if not self.playing:
            # 모든 컨트롤러에 대한 입력을 확인하고,
            # 게임 참여 또는 나가기 확인
            for controller in self.controllers.values():
                while True:
                    key = controller.pop()
                    if key is None:
                        break

                    if key == TetrisKey.JOIN:
                        self.join(controller.player_id)
                    elif key == TetrisKey.LEAVE:
                        self.leave(controller.player_id)
                    elif key == TetrisKey.START:
                        self.start()

        # playing
        if self.playing:
            for player_id in self.players:
                self.players[player_id].tick()

            all_gameover = all(map(lambda player_id: self.players[player_id].playing == False, self.players))
            if all_gameover:
                self.stop()

        self.posttick()
        self.sleep_until_next_tick()
        self.tick_counter += 1

    def pretick(self):
        pass

    def posttick(self):
        pass

    def ongameover(self, player_id: int):
        self.print_message(f'Player {player_id} game over!!!')
        self.print_message(f'total destroyed lines={self.players[player_id].destroyed_lines}')

    def onlinecompleted(self, player_id: int, destroyed_lines: int):
        pass


class ConsoleTetrisGame(TetrisGame):

    width: int
    height: int

    def __init__(self, width: int = 10, height: int = 20):
        super().__init__()
        self.width = width
        self.height = height

    def create_player(self, player_id: int) -> TetrisPlayer:
        return TetrisPlayer(
            game=self,
            width=self.width,
            height=self.height,
            controller=self.get_controller(player_id),
            display_adapter=ConsoleDisplayAdapter(),
        )
