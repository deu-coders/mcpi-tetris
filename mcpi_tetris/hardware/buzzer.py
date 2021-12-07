from typing import Any
import RPi.GPIO as GPIO
import time
import mcpi_tetris.hardware.constants as constants
from .hardware import Hardware

class Buzzer(Hardware):

    buzzer_pwm: Any = None

    def initialize(self):
        self.setup(constants.PIN_BUZZER, GPIO.OUT)
        self.buzzer_pwm = self.PWM(constants.PIN_BUZZER, 10)
        self.buzzer_pwm.start(50)

    def play_tetris_bgm(self):
        if self.buzzer_pwm is None:
            self.initialize()

        while True:
            try:
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

            except KeyboardInterrupt:
                print('Stop playing music ...')
                break
