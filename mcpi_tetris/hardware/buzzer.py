from typing import Any
import RPi.GPIO as GPIO
import time
import mcpi_tetris.hardware.constants as constants
from .hardware import Hardware

class Buzzer(Hardware):

    buzzer_pwm: Any = None

    def initialize(self):
        self.name = 'Buzzer'

        if not self.assert_hardware_enabled():
            return

        self.setup(constants.PIN_BUZZER, GPIO.OUT)
        self.buzzer_pwm = self.PWM(constants.PIN_BUZZER, 10)
        self.buzzer_pwm.start(50)

    def play_tetris_bgm(self):
        if not self.assert_hardware_enabled():
            print('Cannot play music.')
            return

        for melody in constants.BUZZER_MELODIES:
            if (melody[1] > 0) :
                noteDuration = constants.BUZZER_WHOLENOTE / melody[1]
            else:
                noteDuration = constants.BUZZER_WHOLENOTE / abs(melody[1])
                noteDuration *= 1.5

            note = melody[0]
            actualspeed = noteDuration
            self.buzzer_pwm.ChangeFrequency(constants.BUZZER_FREQUENCIES[note])
            time.sleep(actualspeed)
            self.buzzer_pwm.ChangeFrequency(10)

    def play_tetris_bgm_loop(self):
        if not self.assert_hardware_enabled():
            print('Cannot play music.')
            return

        while True:
            try:
                self.play_tetris_bgm()

            except KeyboardInterrupt:
                print('Stop playing music ...')
                break
