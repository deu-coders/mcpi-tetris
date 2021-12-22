import argparse
import sys
from mcpi.minecraft import Minecraft
from mcpi_tetris.config import config
from mcpi_tetris.minecraft.nametools import get_username
from mcpi_tetris.minecraft.remote import McpiRemoteControl


parser = argparse.ArgumentParser(description='Join tetris game to host in mcpi.')
parser.add_argument('ip', default='127.0.0.1', help='IP Address to connect.')
parser.add_argument('--controller', default='wasd', choices=(
    'wasd', 'arrow', 'stdin', 'joystick',
))
parser.add_argument('--record', action='store_true', help='Record player\'s key inputs to file. (will saved into logs folder.)')
parser.add_argument('--play-recorded', help='File to play recorded keys.')
parser.add_argument('--ai', action='store_true', help='It\'s A.I.')

config.load_from_parser(parser)

need_hardwares = config.get('joystick')

if need_hardwares:
    from mcpi_tetris.hardware.hardware import Hardware
    Hardware.enable_hardwares()

if config.get('ai'):
    config.set('play_recorded', '1640170508')

if config.get('play_recorded') is not None:
    config.set('controller', 'record')

username = get_username()

minecraft = Minecraft.create()
player_id = minecraft.getPlayerEntityIds().pop(0)

print(f'[Client] Username={username}')
print(f'[Client] Player ID={player_id}')
minecraft.postToChat(f'Hello {username}! Your id is {player_id}!')

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

remote = McpiRemoteControl(minecraft, controller, config.get('ip'))
remote.run()

if need_hardwares:
    Hardware.cleanup_hardwares()