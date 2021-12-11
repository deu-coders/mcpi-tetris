import argparse
from mcpi.minecraft import Minecraft
from mcpi_tetris.config import config
from mcpi_tetris.minecraft.game import McpiTetrisGame
from music import play_music


parser = argparse.ArgumentParser(description='Run tetris game as host in mcpi.')
parser.add_argument('--lcd', action='store_true', help='LCD 장치를 활성화합니다.')
parser.add_argument('--led', action='store_true', help='LED 장치를 활성화합니다.')
parser.add_argument('--bgm', action='store_true', help='BGM 음악을 재생합니다.')

config.load_from_parser(parser)

need_hardwares = config.get('lcd') or config.get('led') or config.get('bgm')

if need_hardwares:
    from mcpi_tetris.hardware.hardware import Hardware
    Hardware.enable_hardwares()

if config.get('bgm'):
    play_music()

minecraft = Minecraft.create()
game = McpiTetrisGame(minecraft)

# run() method will take infinity loop (to break, keyboard interrupt need)
game.run()

if need_hardwares:
    Hardware.cleanup_hardwares()