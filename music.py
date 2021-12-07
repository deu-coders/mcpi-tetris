import subprocess


def play_music() -> bool:
    play_music_successed = False

    for python_binary in ['python', 'python3']:
        try:
            subprocess.Popen(['python', 'play.py', 'music'])
            print(f'python binary found: {python_binary}')
            play_music_successed = True
        except FileNotFoundError:
            print(f'python binary not found: {python_binary}')

    if not play_music_successed:
        print('Failed to find python binary, halt play music.')
        return False

    return True