from .i2c import Lcd as InternalLcd
from .hardware import Hardware


class LCD(Hardware):

    display: InternalLcd

    def initialize(self):
        self.name = 'LCD'

        if not self.assert_hardware_enabled():
            return

        self.display = InternalLcd()

    def send(self, line: int, message: str):
        if not self.assert_hardware_enabled():
            return

        self.display.lcd_display_string(message, line)

    def close(self):
        if not self.assert_hardware_enabled():
            return

        self.display.lcd_clear()

# try:
#     display.lcd_display_string("player 1 : 100", 1)  
#     display.lcd_display_string("player 2 : 200", 2)  
#     sleep(2)                              
# except:
#     display.lcd_clear()
