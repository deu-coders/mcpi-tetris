from typing import List, Optional
import RPi.GPIO as GPIO
from mcpi.event import ChatEvent
from mcpi.minecraft import Minecraft
from mcpi_tetris.core.controller import Controller, TetrisKey


class RPiGPIOJoystickController(Controller):
    """클라이언트 측에서 GPIO를 사용한 입력을 받을 때 사용"""

    pin_up: int
    pin_down: int
    pin_left: int
    pin_right: int
    pin_land: int

    pin_join: int
    pin_leave: int
    pin_start: int

    def setpins(self, pin_up: int, pin_down: int, pin_left: int, pin_right: int, pin_land: int, pin_join: int, pin_leave: int, pin_start: int):
        self.pin_up = pin_up
        self.pin_down = pin_down
        self.pin_left = pin_left
        self.pin_right = pin_right
        self.pin_land = pin_land

        self.pin_join = pin_join
        self.pin_leave = pin_leave
        self.pin_start = pin_start
    
    def initialize(self):
        assert type(self.pin_up) is int \
            and type(self.pin_down) is int \
            and type(self.pin_left) is int \
            and type(self.pin_right) is int \
            and type(self.pin_land) is int \
            and type(self.pin_join) is int \
            and type(self.pin_leave) is int \
            and type(self.pin_start) is int, 'pins must be initialized using setpins() method!'

        GPIO.setmode(GPIO.BCM)

        for pin in [self.pin_up, self.pin_down, self.pin_left, self.pin_right, self.pin_land]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(self.pin_up, GPIO.RISING, callback=lambda: self.push(TetrisKey.UP), bouncetime=200)
        GPIO.add_event_detect(self.pin_down, GPIO.RISING, callback=lambda: self.push(TetrisKey.DOWN), bouncetime=200)
        GPIO.add_event_detect(self.pin_left, GPIO.RISING, callback=lambda: self.push(TetrisKey.LEFT), bouncetime=200)
        GPIO.add_event_detect(self.pin_right, GPIO.RISING, callback=lambda: self.push(TetrisKey.RIGHT), bouncetime=200)
        GPIO.add_event_detect(self.pin_land, GPIO.RISING, callback=lambda: self.push(TetrisKey.LAND), bouncetime=200)

    def close(self):
        for pin in [self.pin_up, self.pin_down, self.pin_left, self.pin_right, self.pin_land]:
            GPIO.remove_event_detect(pin)

        GPIO.cleanup()


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
