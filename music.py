import subprocess


def play_music() -> bool:
    play_music_successed = False

    for python_binary in ['python3', 'python']:
        try:
            subprocess.Popen([python_binary, 'play.py', 'music'])
            print(f'python binary found: {python_binary}')
            play_music_successed = True
            break
        except FileNotFoundError:
            print(f'python binary not found: {python_binary}')

    if not play_music_successed:
        print('Failed to find python binary, halt play music.')
        return False

    return True

def play_music_loop():
    from mcpi_tetris.hardware.buzzer import Buzzer
    buzzer = Buzzer()
    buzzer.play_tetris_bgm_loop()


if __name__ == '__main__':
    from mcpi_tetris.hardware.hardware import Hardware
    Hardware.enable_hardwares()
    play_music_loop()
    Hardware.cleanup_hardwares()