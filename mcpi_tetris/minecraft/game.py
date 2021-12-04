from typing import Dict
from mcpi.minecraft import Minecraft
from mcpi_tetris.core.network import ControllerNetwork, CONTROLLER_SERVER_PORT
from mcpi_tetris.core.controller import Controller
from mcpi_tetris.core.game import TetrisGame, TetrisPlayer

from .display import McpiDisplayAdapter


class McpiTetrisGame(TetrisGame):

    minecraft: Minecraft
    controllers: Dict[str, Controller]
    network: ControllerNetwork

    def __init__(self, minecraft: Minecraft):
        super().__init__()
        self.minecraft = minecraft
        self.print_message('Tetris game open!')

        self.network = ControllerNetwork()
        self.network.serve()
        self.print_message(f'Also accepts controller input via socket (PORT={CONTROLLER_SERVER_PORT})!')

    def create_controller(self, player_id: int) -> Controller:
        return Controller(player_id) # 빈 컨트롤러 사용

    def create_player(self, player_id: int) -> TetrisPlayer:
        return TetrisPlayer(
            width=10,
            height=20,
            controller=self.get_controller(player_id),
            display_adapter=McpiDisplayAdapter(self.minecraft, player_id)
        )

    def print_message(self, message: str):
        print(f'[Tetris] {message}')
        self.minecraft.postToChat(f'[Tetris] {message}')

    def pretick(self):
        # 소켓으로부터 데이터를 받은 후 controller에 push
        for packet in self.network.recv():
            player_id = packet.player_id
            key = packet.key

            if player_id in self.controllers:
                self.controllers[player_id].push(key)

        # join, leave 감지하여 상태 업데이트
        old_players = set(self.controllers.keys())
        new_players = set(self.minecraft.getPlayerEntityIds())

        # 떠난 플레이어 감지
        for player_id in old_players:
            # Player leave detection
            if player_id not in new_players:
                self.print_message(f'Player {player_id} leave the world')
                self.remove_controller(player_id)

        # 새로운 플레이어 감지
        for player_id in new_players:
            # Player join detection
            if player_id not in old_players:
                self.print_message(f'Player {player_id} join the world')
                self.add_controller(self.create_controller(player_id))

    def poststop(self):
        self.network.close()