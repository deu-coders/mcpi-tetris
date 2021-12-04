from collections import deque
from socket import *
from typing import Deque, Iterable, List, Optional

from .controller import TetrisKey


CONTROLLER_SERVER_PORT = 19966

class TetrisPacket:
    player_id: int
    key: TetrisKey

    @staticmethod
    def key_to_raw(key: TetrisKey) -> Optional[str]:
        if key == TetrisKey.UP:
            return 'up'
        elif key == TetrisKey.DOWN:
            return 'down'
        elif key == TetrisKey.LEFT:
            return 'left'
        elif key == TetrisKey.RIGHT:
            return 'right'
        elif key == TetrisKey.LAND:
            return 'land'

        elif key == TetrisKey.JOIN:
            return 'join'
        elif key == TetrisKey.LEAVE:
            return 'leave'
        elif key == TetrisKey.START:
            return 'start'

        return None

    @staticmethod
    def raw_to_key(token: str) -> Optional[TetrisKey]:
        if token == 'up':
            return TetrisKey.UP
        elif token == 'down':
            return TetrisKey.DOWN
        elif token == 'left':
            return TetrisKey.LEFT
        elif token == 'right':
            return TetrisKey.RIGHT
        elif token == 'land':
            return TetrisKey.LAND

        elif token == 'join':
            return TetrisKey.JOIN
        elif token == 'leave':
            return TetrisKey.LEAVE
        elif token == 'start':
            return TetrisKey.START

        return None

    def __init__(self, player_id: int, key: TetrisKey):
        self.player_id = player_id
        self.key = key

    @staticmethod
    def deserialize(raw: str) -> 'TetrisPacket':
        player_id, key = raw.split('-')
        player_id = int(player_id)
        key = TetrisPacket.raw_to_key(key)

        return TetrisPacket(player_id, key)

    def serialize(self) -> str:
        return f'{self.player_id}-{TetrisPacket.key_to_raw(self.key)}'


class ControllerNetwork:
    sock: socket
    tokens: Deque[str]
    buffer: str

    clients: List['ControllerNetwork']

    def __init__(self, sock: Optional[socket] = None):
        if sock is None:
            sock = socket(AF_INET, SOCK_STREAM)

        self.sock = sock
        self.sock.setblocking(False)
        self.tokens = deque()
        self.buffer = ''
        self.clients = []

    def serve(self):
        self.sock.bind(('0.0.0.0', CONTROLLER_SERVER_PORT))
        self.sock.listen()

    def flush(self):
        tokens = self.buffer.split(':')
        if len(tokens) <= 1: # nothing to flush
            return

        for token in tokens[:-1]:
            self.tokens.appendleft(token)

        self.buffer = tokens[-1]

    def _accept(self) -> Optional[socket]:
        try:
            conn, addr = self.sock.accept()
            conn.setblocking(False)
            print(f'new socket connection from {addr}')
            return conn
        except BlockingIOError:
            return None

    # message format:
    # "49.right:34.land:96.join ..."
    def recv(self) -> Iterable[TetrisPacket]:
        # accept new clients
        conn = self._accept()
        if conn is not None:
            self.clients.append(ControllerNetwork(conn))

        tokens = []

        # receive data from client
        for client in self.clients:
            try:
                client.buffer += client.sock.recv(100).decode('utf-8')
            except BlockingIOError:
                pass

            client.flush()
            tokens += client.tokens
            client.tokens.clear()

        return map(TetrisPacket.deserialize, tokens)

    def connect(self, address) -> bool:
        try:
            self.sock.connect((address, CONTROLLER_SERVER_PORT))
        except BlockingIOError:
            return False

        return True

    def send(self, player_id: int, key: TetrisKey):
        raw = TetrisPacket(player_id, key).serialize() + ':'
        self.sock.send(raw.encode())

    def close(self):
        self.sock.shutdown()
        self.sock.close()