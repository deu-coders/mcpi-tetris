import sys
import argparse
from mcpi_tetris.config import config
from mcpi_tetris.core.controller import KeyboardArrowController, KeyboardWASDController, StdinController
from mcpi_tetris.core.game import ConsoleTetrisGame


parser = argparse.ArgumentParser(description='Play tetris in terminal. (Single play only)')
parser.add_argument('--controller', default='wasd', choices=(
    'wasd', 'arrow', 'stdin', 'joystick', 'record',
))
parser.add_argument('--record', action='store_true', help='Record player\'s key inputs to file. (will saved into logs folder.)')
parser.add_argument('--play-recorded', help='File to play recorded keys.')

config.load_from_parser(parser)

need_hardwares = config.get('joystick')

if need_hardwares:
    from mcpi_tetris.hardware.hardware import Hardware
    Hardware.enable_hardwares()

player_id = 1

controller = None
if config.get('controller') == 'wasd':
    from mcpi_tetris.core.controller import KeyboardWASDController
    controller = KeyboardWASDController(player_id)
elif config.get('controller') == 'arrow':
    from mcpi_tetris.core.controller import KeyboardArrowController
    controller = KeyboardArrowController(player_id)
elif config.get('controller') == 'stdin':
    from mcpi_tetris.core.controller import StdinController
    controller = StdinController(player_id)
elif config.get('controller') == 'joystick':
    from mcpi_tetris.hardware.controller import RPiGPIOJoystickController
    controller = RPiGPIOJoystickController(player_id)
elif config.get('controller') == 'record':
    if config.get('play_recorded') is None:
        print('You should give --play-recorded option!! (e.x. --play-recorded 1639161407)')
        sys.exit(1)

    from mcpi_tetris.record.controller import RecordedController
    controller = RecordedController(player_id)

game = ConsoleTetrisGame()
game.add_controller(controller)
game.join(player_id)
game.start()
game.run()

if need_hardwares:
    Hardware.cleanup_hardwares()