import argparse
from dotenv import load_dotenv

from mcpi_tetris.minecraft.nametools import get_username, set_username
from mcpi_tetris.core.controller import Controller
from mcpi_tetris.hardware.hardware import Hardware
from music import play_music

parser = argparse.ArgumentParser(description='Tetris over the mcpi!')
parser.add_argument('mode',
    default='stdio',
    choices=(
        'getusername',
        'setusername',
        'host',
        'stdio-keyboard-arrow',
        'stdio-keyboard-wasd',
        'stdio-joystick',
        'stdio-stdin',
        'client-keyboard-arrow',
        'client-keyboard-wasd',
        'client-joystick',
        'client-stdin',
        'music',
    ),
    help='테트리스 동작 모드를 설정합니다.'
)
parser.add_argument('--hardware', action='store_true', help='하드웨어를 활성화합니다.')
parser.add_argument('--music', action='store_true', help='BGM 음악을 재생합니다. --hardware 옵션이 필요합니다.')

args = parser.parse_args()

load_dotenv()

if args.hardware or args.mode.endswith('-joystick'):
    Hardware.enable_hardwares()

def get_controller(controller_name: str, player_id: int) -> Controller:
    if controller_name == 'keyboard-arrow':
        from mcpi_tetris.core.controller import KeyboardArrowController
        return KeyboardArrowController(player_id)

    elif controller_name == 'keyboard-wasd':
        from mcpi_tetris.core.controller import KeyboardWASDController
        return KeyboardWASDController(player_id)

    elif controller_name == 'joystick':
        from mcpi_tetris.hardware.controller import RPiGPIOJoystickController
        return RPiGPIOJoystickController(player_id)

    elif controller_name == 'stdin':
        from mcpi_tetris.core.controller import StdinController
        return StdinController(player_id)


if args.mode == 'getusername':
    print(f'Your username is "{get_username()}"')

elif args.mode == 'setusername':
    username = input('Input your new username (1-7): ')
    set_username(username)

elif args.mode == 'host':
    print('You have selected host mode')

    from mcpi.minecraft import Minecraft
    from mcpi_tetris.minecraft.game import McpiTetrisGame

    if args.music:
        play_music()

    minecraft = Minecraft.create()
    game = McpiTetrisGame(minecraft)
    # run() method will take infinity loop (to break, keyboard interrupt need)
    game.run()

elif args.mode == 'music':
    from mcpi_tetris.hardware.buzzer import Buzzer
    buzzer = Buzzer()
    buzzer.play_tetris_bgm_loop()

elif args.mode.startswith('stdio-'):
    print(f'You have selected {args.mode}')
    controller_name = args.mode.split('stdio-')[1]

    from mcpi_tetris.core.game import ConsoleTetrisGame
    game = ConsoleTetrisGame()

    single_player_id = 1

    controller = get_controller(controller_name, single_player_id)
    game.add_controller(controller)
    game.join(single_player_id)
    game.start()
    game.run()

elif args.mode.startswith('client-'):
    print(f'You have selected {args.mode}')
    controller_name = args.mode.split('client-')[1]

    from mcpi.minecraft import Minecraft
    minecraft = Minecraft.create()

    username = get_username()
    print(f'Your username is "{username}".')

    address = input('Please input controller server ip address: ')

    # flush all block events
    minecraft.events.pollBlockHits()

    minecraft.postToChat(f'{username}, please touch any block using sword')
    minecraft.postToChat('for identify your id!')

    player_id = None
    while player_id is None:
        for event in minecraft.events.pollBlockHits():
            player_id = event.entityId
            break

    minecraft.postToChat(f'Good job, {username}. your id is {player_id}!')

    controller = get_controller(controller_name, player_id)

    from mcpi_tetris.minecraft.remote import McpiRemoteControl
    McpiRemoteControl(minecraft, controller, address).run()


# Cleanup all hardwares
Hardware.cleanup_hardwares()