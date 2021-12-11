import argparse
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

config.load_from_parser(parser)

need_hardwares = config.get('joystick')

if need_hardwares:
    from mcpi_tetris.hardware.hardware import Hardware
    Hardware.enable_hardwares()

username = get_username()

minecraft = Minecraft.create()
minecraft.events.pollBlockHits() # flush all block events
minecraft.postToChat(f'{username}, please touch any block using sword')
minecraft.postToChat('for identify your id!')

player_id = None
while player_id is None:
    for event in minecraft.events.pollBlockHits():
        player_id = event.entityId
        break

minecraft.postToChat(f'Good job, {username}. your id is {player_id}!')

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

remote = McpiRemoteControl(minecraft, controller, config.get('ip'))
remote.run()

if need_hardwares:
    Hardware.cleanup_hardwares()