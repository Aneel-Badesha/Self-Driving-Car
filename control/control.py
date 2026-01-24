import RPi.GPIO as GPIO
import time

class MotorController:
    FORWARD = 1
    BACKWARD = 0

    def __init__(self):
        self.front_right_wheel = [23, 24]
        self.back_right_wheel = [25, 16]
        self.front_left_wheel = [5, 6]
        self.back_left_wheel = [12, 13]
        self.pins = [23, 24, 25, 16, 5, 6, 12, 13]
        GPIO.setmode(GPIO.BCM)

    def gpio_setup(self, wheel):
        for pin in wheel:
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                print(f"Pin {pin} configured successfully")
            except Exception as e:
                print(f"Pin {pin} failed: {e}")

    def setup_all(self):
        self.gpio_setup(self.front_right_wheel)
        self.gpio_setup(self.back_right_wheel)
        self.gpio_setup(self.front_left_wheel)
        self.gpio_setup(self.back_left_wheel)

    def drive(self, direction, wheel):
        if direction == self.FORWARD:
            GPIO.output(wheel[0], GPIO.HIGH)
            GPIO.output(wheel[1], GPIO.LOW)
        else:
            GPIO.output(wheel[0], GPIO.LOW)
            GPIO.output(wheel[1], GPIO.HIGH)

    def drive_all(self, direction):
        self.drive(direction, self.front_right_wheel)
        self.drive(direction, self.back_right_wheel)
        self.drive(direction, self.front_left_wheel)
        self.drive(direction, self.back_left_wheel)

    def stop(self, wheel):
        for pin in wheel:
            GPIO.output(pin, GPIO.LOW)

    def stop_all(self):
        self.stop(self.front_right_wheel)
        self.stop(self.back_right_wheel)
        self.stop(self.front_left_wheel)
        self.stop(self.back_left_wheel)

    def cleanup(self):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()