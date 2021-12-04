def get_username() -> str:
    # Get the player name (7 chars) for Minecraft PI Edition
    # Written by Richard Garsthagen - richard@coderdojo-zoetermeer.nl
    #
    # Use at own risk. Please make a backup of minecraft-pi first!
    namestart = 1026250
    username = None

    with open("/opt/minecraft-pi/minecraft-pi", "rb") as file:
        file.seek(namestart)
        username = file.read(7).decode('utf-8')

    return username


def set_username(username: str):
    # Set the player name (7 chars) for Minecraft PI Edition
    # Written by Richard Garsthagen - richard@coderdojo-zoetermeer.nl
    #
    # Use at own risk. Please make a backup of minecraft-pi first!
    namestart = 1026250

    if len(username) < 1 or len(username) > 7:
        raise 'username should be greater than 0 or lesser than 8.'

    with open("/opt/minecraft-pi/minecraft-pi", "r+b") as file:
        file.seek(namestart)
        print('Current name: {} '.format(file.read(7)))

        # encode player's name to ascii bytes
        username = username.encode('ascii')
        username = username[:7]

        if len(username) < 7:
            extraspaces = 7 - len(username)
            for x in range(0, extraspaces):
                username = username + b' '

            assert len(username) == 7

            file.seek(namestart)
            file.write(username)
            print (f'Change name to: {username} ({len(username)})')
