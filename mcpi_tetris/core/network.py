from collections import deque
from socket import *
from typing import Deque, Iterable, List, Optional

from .controller import TetrisKey


CONTROLLER_SERVER_PORT = 19966

class TetrisPacket:
    player_id: int
    key: TetrisKey

    def __init__(self, player_id: str, key: TetrisKey):
        self.player_id = player_id
        self.key = key

    @staticmethod
    def deserialize(raw: str) -> 'TetrisPacket':
        player_id, key = raw.split('-')
        return TetrisPacket(int(player_id), TetrisKey[key])

    def serialize(self) -> str:
        return f'{self.player_id}-{self.key.value}'


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
        except error:
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
        try:
            self.sock.shutdown(SHUT_RDWR)
        except Exception as e:
            print('Error occured while shutdown socket.')
            print(e)
            pass
        finally:
            self.sock.close()
