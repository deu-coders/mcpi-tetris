from typing import List, Optional
from mcpi.event import ChatEvent
from mcpi.minecraft import Minecraft
from mcpi_tetris.core.controller import Controller, TetrisKey


class McpiChatProxyController(Controller):
    """
    서버 사이드에서 클라이언트로 부터 채팅을 통해 입력을 받을 때 사용
    WARNING! Only works in RaspberryJuice!!! Not working with mcpi!
    """

    chat_events: List[ChatEvent] = []
    """클래스 전역으로 사용되는 채팅 이벤트 리스트"""

    minecraft: Minecraft

    def __init__(self, minecraft: Minecraft, player_id: int):
        super().__init__(player_id)
        self.minecraft = minecraft

    def chat_to_key(self, message: str) -> Optional[TetrisKey]:
        if message == '/left':
            return TetrisKey.LEFT
        elif message == '/right':
            return TetrisKey.RIGHT
        elif message == '/up':
            return TetrisKey.UP
        elif message == '/down':
            return TetrisKey.DOWN
        elif message == '/land':
            return TetrisKey.LAND

        elif message == '/join':
            return TetrisKey.JOIN
        elif message == '/leave':
            return TetrisKey.LEAVE
        elif message == '/start':
            return TetrisKey.START
        
        return None

    def pop(self) -> Optional[TetrisKey]:
        # poll all chats and put into static member
        for event in self.minecraft.events.pollChatPosts():
            McpiChatProxyController.chat_events.append(event)

        unused_events = []
        for event in McpiChatProxyController.chat_events:
            entityId = event.entityId
            message = event.message

            if entityId != self.player_id:
                unused_events.append(event)
                continue

            key = self.chat_to_key(message)
            if key is not None:
                self.push(key)
        
        McpiChatProxyController.chat_events = unused_events
        return self.pop()


class McpiPosBasedProxyController(Controller):
    """서버 사이드에서 클라이언트로 부터 Block을 사용하여 입력을 받을 때 사용"""

    @staticmethod
    def key_to_pos(key: TetrisKey) -> Optional[float]:
        if key == TetrisKey.UP:
            return 0.2
        elif key == TetrisKey.DOWN:
            return 0.3
        elif key == TetrisKey.LEFT:
            return 0.4
        elif key == TetrisKey.RIGHT:
            return 0.5
        elif key == TetrisKey.LAND:
            return 0.6

        elif key == TetrisKey.JOIN:
            return 0.7
        elif key == TetrisKey.LEAVE:
            return 0.8
        elif key == TetrisKey.START:
            return 0.9

        return None

    @staticmethod
    def pos_to_key(y: float) -> Optional[TetrisKey]:
        value = int((y * 10) % 10)

        if value == 2:
            return TetrisKey.UP
        elif value == 3:
            return TetrisKey.DOWN
        elif value == 4:
            return TetrisKey.LEFT
        elif value == 5:
            return TetrisKey.RIGHT
        elif value == 6:
            return TetrisKey.LAND

        elif value == 7:
            return TetrisKey.JOIN
        elif value == 8:
            return TetrisKey.LEAVE
        elif value == 9:
            return TetrisKey.START

        return None

    minecraft: Minecraft

    def __init__(self, minecraft: Minecraft, player_id: int):
        super().__init__(player_id)
        self.minecraft = minecraft

        x, y, z = self.minecraft.entity.getPos(self.player_id)
        self.minecraft.entity.setPos(self.player_id, x, int(y), z)

    def pop(self) -> Optional[TetrisKey]:
        x, y, z = self.minecraft.entity.getPos(self.player_id)

        self.minecraft.entity.setPos(self.player_id, x, int(y), z)
        return McpiPosBasedProxyController.pos_to_key(y)
