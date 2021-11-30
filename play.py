from tetris.controller import KeyboardWASDController
from tetris.display import ConsoleDisplayAdapter
from tetris.game import Tetris


tetris = Tetris(
    width=10,
    height=20,
    display_adapter=ConsoleDisplayAdapter(),
    controller=KeyboardWASDController(),
)

while True:
    tetris.tick()
    tetris.sleep_until_next_tick()