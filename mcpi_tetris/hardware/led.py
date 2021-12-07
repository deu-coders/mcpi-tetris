import RPi.GPIO as GPIO
import time
from PIL import ImageColor

import mcpi_tetris.hardware.constants as constants

from .hardware import Hardware

class LED(Hardware):

    pin_led_r: int
    pin_led_g: int
    pin_led_b: int

    def setpins(self, pin_led_r: int, pin_led_g: int, pin_led_b: int):
        self.pin_led_r = pin_led_r
        self.pin_led_g = pin_led_g
        self.pin_led_b = pin_led_b

    def initialize(self):
        self.name = 'RGB LED'

        if not self.assert_hardware_enabled():
            return

        self.setpins(
            pin_led_r=constants.PIN_LED_R,
            pin_led_g=constants.PIN_LED_G,
            pin_led_b=constants.PIN_LED_B,
        )

        self.setup(self.pin_led_r, GPIO.OUT)
        self.setup(self.pin_led_g, GPIO.OUT)
        self.setup(self.pin_led_b, GPIO.OUT)

        self.p_R = self.PWM(self.pin_led_r, 1000)
        self.p_G = self.PWM(self.pin_led_g, 1000)
        self.p_B = self.PWM(self.pin_led_b, 1000)

        self.p_R.start(0)
        self.p_G.start(0)
        self.p_B.start(0)

    def mapping(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def on(self, color_hex: int):
        if not self.assert_hardware_enabled():
            return

        r_val = (color_hex & 0xFF0000) >> 16
        g_val = (color_hex & 0x00FF00) >> 8
        b_val = (color_hex & 0x0000FF) >> 0

        r_val = self.mapping(r_val, 0, 255, 0, 100)
        g_val = self.mapping(g_val, 0, 255, 0, 100)
        b_val = self.mapping(b_val, 0, 255, 0, 100)

        self.p_R.ChangeDutyCycle(100 - r_val)     
        self.p_G.ChangeDutyCycle(100 - g_val)
        self.p_B.ChangeDutyCycle(100 - b_val)

    def off(self):
        if not self.assert_hardware_enabled():
            return

        self.on(0xFFFFFF)

        #self.p_R.ChangeDutyCycle(100)
        #self.p_G.ChangeDutyCycle(100)
        #self.p_B.ChangeDutyCycle(100)

    def close(self):
        if not self.assert_hardware_enabled():
            return

        self.off()
        return super().close()


# led = Led(16,20,21)
# led.on('#008d62')
# time.sleep(5)
# led.off()
