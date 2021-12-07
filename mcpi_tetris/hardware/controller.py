from collections import deque
from typing import Optional
import RPi.GPIO as GPIO

from mcpi_tetris.core.controller import Controller, TetrisKey
import mcpi_tetris.hardware.constants as constants
from .hardware import Hardware


class Joystick(Hardware):

    queue: deque

    def poll(self) -> Optional[TetrisKey]:
        if len(self.queue) == 0:
            return None

        print(self.queue)
        return self.queue.pop()

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
        self.name = 'Joystick'

        if not self.assert_hardware_enabled():
            return

        self.queue = deque()

        self.setpins(
            pin_up=constants.PIN_UP,
            pin_down=constants.PIN_DOWN,
            pin_left=constants.PIN_LEFT,
            pin_right=constants.PIN_RIGHT,
            pin_land=constants.PIN_LAND,

            pin_join=constants.PIN_JOIN,
            pin_leave=constants.PIN_LEAVE,
            pin_start=constants.PIN_START,
        )

        assert type(self.pin_up) is int \
            and type(self.pin_down) is int \
            and type(self.pin_left) is int \
            and type(self.pin_right) is int \
            and type(self.pin_land) is int \
            and type(self.pin_join) is int \
            and type(self.pin_leave) is int \
            and type(self.pin_start) is int, 'pins must be initialized using setpins() method!'

        for pin in [
            self.pin_up,
            self.pin_down,
            self.pin_left,
            self.pin_right,
            self.pin_land,

            self.pin_join,
            self.pin_leave,
            self.pin_start
        ]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.pin_up, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.UP), bouncetime=200)
        GPIO.add_event_detect(self.pin_down, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.DOWN), bouncetime=200)
        GPIO.add_event_detect(self.pin_left, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.LEFT), bouncetime=200)
        GPIO.add_event_detect(self.pin_right, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.RIGHT), bouncetime=200)
        GPIO.add_event_detect(self.pin_land, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.LAND), bouncetime=200)

        GPIO.add_event_detect(self.pin_join, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.JOIN), bouncetime=200)
        GPIO.add_event_detect(self.pin_leave, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.LEAVE), bouncetime=200)
        GPIO.add_event_detect(self.pin_start, GPIO.FALLING, callback=lambda _: self.queue.appendleft(TetrisKey.START), bouncetime=200)

    def close(self):
        for pin in [
            self.pin_up,
            self.pin_down,
            self.pin_left,
            self.pin_right,
            self.pin_land,

            self.pin_join,
            self.pin_leave,
            self.pin_start
        ]:
            GPIO.remove_event_detect(pin)


class RPiGPIOJoystickController(Controller):
    """클라이언트 측에서 GPIO를 사용한 입력을 받을 때 사용"""

    joystick: Joystick

    def initialize(self):
        self.joystick = Joystick()

    def pop(self) -> Optional[TetrisKey]:
        return self.joystick.poll()

    def close(self):
        self.joystick.close()
