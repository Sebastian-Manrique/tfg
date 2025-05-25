from src.core.utils import shared_flags
import RPi.GPIO as GPIO
import threading
import time

CAM_LED = 17
SCAN_LED = 27
BUTTON_GPIO = 22  # o 26 si quieres usar el original


class HardwareController:
    def __init__(self, on_button_press=None):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(CAM_LED, GPIO.OUT)
        GPIO.setup(SCAN_LED, GPIO.OUT)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.scanning = True
        self._start_button_listener(on_button_press)

    def _start_button_listener(self, on_button_press=None):
        def check_button():
            button_previously_pressed = False
            while self.scanning:
                if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
                    if not button_previously_pressed:
                        button_previously_pressed = True

                        shared_flags.button_pressed_after_detection = True

                        if on_button_press:
                            on_button_press()
                else:
                    button_previously_pressed = False
                time.sleep(0.1)

        threading.Thread(target=check_button, daemon=True).start()

    def camera_on(self):
        GPIO.output(CAM_LED, True)

    def camera_off(self):
        GPIO.output(CAM_LED, False)

    def blink_camera(self, times=2, delay=0.2):
        for _ in range(times):
            GPIO.output(CAM_LED, False)
            time.sleep(delay)
            GPIO.output(CAM_LED, True)
            time.sleep(delay)

    def scan_success(self):
        GPIO.output(SCAN_LED, True)
        time.sleep(1)
        GPIO.output(SCAN_LED, False)

    def cleanup(self):
        GPIO.output(CAM_LED, False)
        GPIO.output(SCAN_LED, False)
        GPIO.cleanup()
