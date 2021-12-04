import time
from mcpi.minecraft import Minecraft
from mcpi_tetris.core.network import ControllerNetwork
from mcpi_tetris.core.controller import Controller, TetrisKey


class McpiRemoteControl:

    minecraft: Minecraft
    controller: Controller
    network: ControllerNetwork

    def __init__(self, minecraft: Minecraft, controller: Controller, address: str):
        self.minecraft = minecraft
        self.controller = controller
        self.controller.preinitialize()

        self.network = ControllerNetwork()
        self.network.connect(address)

    def send_key(self, key: TetrisKey):
        self.network.send(self.controller.player_id, key)

    def run(self):
        while True:
            try:
                key = self.controller.pop()
                if key is None:
                    time.sleep(0.05)
                    continue

                self.send_key(key)

            except KeyboardInterrupt:
                print('Shutdown ...')
                self.network.close()
                break
