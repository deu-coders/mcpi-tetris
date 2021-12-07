import time
from mcpi_tetris.hardware.hardware import Hardware


def pause():
    input('Press enter to continue ...')


def test_led():
    print('Test LED ...')

    from mcpi_tetris.hardware.led import LED
    led = LED()

    print('\tled.on(0xFFFFFF) // white')
    led.on(0xFFFFFF)
    pause()

    print('\tled.on(0xFF0000) // red')
    led.on(0xFF0000)
    pause()

    print('\tled.on(0x00FF00) // green')
    led.on(0x00FF00)
    pause()

    print('\tled.on(0x0000FF) // blue')
    led.on(0x0000FF)
    pause()

    print('\tled.on(0xFF00FB) // pink')
    led.on(0xFF00FB)
    pause()

    print('\tled.off()')
    led.off()
    pause()

    led.close()


def test_buzzer():
    print('Test Buzzer ...')

    from mcpi_tetris.hardware.buzzer import Buzzer
    buzzer = Buzzer()

    print('\tbuzzer.play_tetris_bgm()')
    print('\tPress Ctrl+C to continue ...')

    try:
        buzzer.play_tetris_bgm_loop()
    except KeyboardInterrupt:
        pass

    buzzer.close()


def test_lcd():
    print('Test LCD ...')

    from mcpi_tetris.hardware.lcd import LCD
    lcd = LCD()

    print('\tlcd.send(1, "Hello World!")')
    lcd.send(1, 'Hello World!')
    pause()

    print('\tlcd.send(2, "Test 123456")')
    lcd.send(2, 'Test 123456')
    pause()

    lcd.close()


def test_joystick():
    print('Test Joystick')

    from mcpi_tetris.hardware.controller import RPiGPIOJoystickController
    controller = RPiGPIOJoystickController(1)
    controller.preinitialize()

    print('\tPress Ctrl+C to continue ...')

    try:
        while True:
            key = controller.pop()
            if key is None:
                time.sleep(0.1)
                continue

            print('Key pressed:', key)

    except KeyboardInterrupt:
        pass

    controller.close()


def before_test():
    from dotenv import load_dotenv
    load_dotenv()

    Hardware.enable_hardwares()


def after_test():
    Hardware.cleanup_hardwares()


def test():
    before_test()

    try:
        # Add your unit test
        test_led()
        test_lcd()
        test_buzzer()
        test_joystick()
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        after_test()


if __name__ == '__main__':
    test()