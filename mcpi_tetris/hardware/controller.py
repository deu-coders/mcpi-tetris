import RPi.GPIO as GPIO

from mcpi_tetris.core.controller import Controller, TetrisKey
import mcpi_tetris.hardware.constants as constants


class RPiGPIOJoystickController(Controller):
    """클라이언트 측에서 GPIO를 사용한 입력을 받을 때 사용"""

    pin_up: int = constants.PIN_UP
    pin_down: int = constants.PIN_DOWN
    pin_left: int = constants.PIN_LEFT
    pin_right: int = constants.PIN_RIGHT
    pin_land: int = constants.PIN_LAND

    pin_join: int = constants.PIN_JOIN
    pin_leave: int = constants.PIN_LEAVE
    pin_start: int = constants.PIN_START

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

        GPIO.add_event_detect(self.pin_up, GPIO.RISING, callback=lambda _: self.push(TetrisKey.UP), bouncetime=200)
        GPIO.add_event_detect(self.pin_down, GPIO.RISING, callback=lambda _: self.push(TetrisKey.DOWN), bouncetime=200)
        GPIO.add_event_detect(self.pin_left, GPIO.RISING, callback=lambda _: self.push(TetrisKey.LEFT), bouncetime=200)
        GPIO.add_event_detect(self.pin_right, GPIO.RISING, callback=lambda _: self.push(TetrisKey.RIGHT), bouncetime=200)
        GPIO.add_event_detect(self.pin_land, GPIO.RISING, callback=lambda _: self.push(TetrisKey.LAND), bouncetime=200)

    def close(self):
        for pin in [self.pin_up, self.pin_down, self.pin_left, self.pin_right, self.pin_land]:
            GPIO.remove_event_detect(pin)

        GPIO.cleanup()
