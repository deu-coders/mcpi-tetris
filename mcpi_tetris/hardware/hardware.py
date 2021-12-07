from typing import Any, List
import RPi.GPIO as GPIO


class Hardware:

    enabled = False
    hardwares: List['Hardware'] = []

    @staticmethod
    def enable_hardwares():
        Hardware.enabled = True
        GPIO.setmode(GPIO.BCM)
        print('Hardware enabled. Set GPIO mode to BCM.')

    @staticmethod
    def cleanup_hardwares():
        if not Hardware.enabled:
            return

        print('Cleanup all hardware resources ...')
        for hardware in Hardware.hardwares:
            hardware.close()

        GPIO.cleanup()

    pins: List[int]
    pwms: List[Any]
    name: str

    def __init__(self):
        self.pins = []
        self.pwms = []
        self.name = 'Unknown'

        self.initialize()

    def initialize(self):
        pass

    def print(self, message: str):
        print(f'Hardware {self.name}: {message}')

    def assert_hardware_enabled(self):
        if not Hardware.enabled:
            self.print('INFO: hardware request detected, but hardware is disabled. Please enable hardware to use.')
            return False

        return True

    def setup(self, pin: int, in_or_out: int):
        if not self.assert_hardware_enabled():
            return

        self.pins.append(pin)
        GPIO.setup(pin, in_or_out)
        self.print(f'INFO: pin {pin} used by {self.name}')

    def PWM(self, pin: int, value: int):
        if not self.assert_hardware_enabled():
            return

        if pin not in self.pins:
            self.print('WARNING: You must call setup before using pin in PWM()')

        pwm = GPIO.PWM(pin, value)
        self.pwms.append(pwm)
        self.print(f'INFO: pin {pin} pwm initialized by value {value}.')
        return pwm

    def close(self):
        if not self.assert_hardware_enabled():
            return

        for pin in self.pins:
            GPIO.setmode(pin, GPIO.OUT)

        for pwm in self.pwms:
            pwm.stop()