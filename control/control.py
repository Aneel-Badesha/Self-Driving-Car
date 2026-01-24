import RPi.GPIO as GPIO
import time

class MotorController:
    FORWARD = 1
    BACKWARD = 0
    DEFAULT_FREQ = 100

    def __init__(self):
        self.front_right_wheel = [23, 24]
        self.back_right_wheel = [25, 16]
        self.front_left_wheel = [5, 6]
        self.back_left_wheel = [12, 13]
        self.pins = [23, 24, 25, 16, 5, 6, 12, 13]
        self.pwm = {}
        GPIO.setmode(GPIO.BCM)

    def gpio_setup(self, wheel):
        for pin in wheel:
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                print(f"Pin {pin} configured successfully")
            except Exception as e:
                print(f"Pin {pin} failed: {e}")
        # Setup PWM on the first pin of the wheel
        if wheel[0] not in self.pwm:
            self.pwm[wheel[0]] = GPIO.PWM(wheel[0], self.DEFAULT_FREQ)
            self.pwm[wheel[0]].start(0)

    def setup_all(self):
        # Set up all pins first
        for pin in self.pins:
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            except Exception as e:
                print(f"Pin {pin} failed: {e}")
        # Set up all PWM channels
        for wheel in [self.front_right_wheel, self.back_right_wheel, self.front_left_wheel, self.back_left_wheel]:
            if wheel[0] not in self.pwm:
                self.pwm[wheel[0]] = GPIO.PWM(wheel[0], self.DEFAULT_FREQ)
                self.pwm[wheel[0]].start(0)
        print("All pins and PWM channels configured successfully")

    def drive(self, direction, wheel, speed=100):
        # Clamp speed
        speed = max(0, min(100, speed))
        self.pwm[wheel[0]].ChangeDutyCycle(speed)
        if direction == self.FORWARD:
            GPIO.output(wheel[0], GPIO.HIGH)
            GPIO.output(wheel[1], GPIO.LOW)
        else:
            GPIO.output(wheel[0], GPIO.LOW)
            GPIO.output(wheel[1], GPIO.HIGH)

    def drive_all(self, direction, speed=100):
        # Set direction for all wheels first
        for wheel in [self.front_right_wheel, self.back_right_wheel, self.front_left_wheel, self.back_left_wheel]:
            if direction == self.FORWARD:
                GPIO.output(wheel[0], GPIO.HIGH)
                GPIO.output(wheel[1], GPIO.LOW)
            else:
                GPIO.output(wheel[0], GPIO.LOW)
                GPIO.output(wheel[1], GPIO.HIGH)
        # Then set PWM for all wheels
        speed = max(0, min(100, speed))
        for wheel in [self.front_right_wheel, self.back_right_wheel, self.front_left_wheel, self.back_left_wheel]:
            self.pwm[wheel[0]].ChangeDutyCycle(speed)

    def set_speed(self, wheel, speed):
        speed = max(0, min(100, speed))
        self.pwm[wheel[0]].ChangeDutyCycle(speed)

    def set_speed_all(self, speed):
        self.set_speed(self.front_right_wheel, speed)
        self.set_speed(self.back_right_wheel, speed)
        self.set_speed(self.front_left_wheel, speed)
        self.set_speed(self.back_left_wheel, speed)

    def stop(self, wheel):
        self.pwm[wheel[0]].ChangeDutyCycle(0)
        for pin in wheel:
            GPIO.output(pin, GPIO.LOW)

    def stop_all(self):
        self.stop(self.front_right_wheel)
        self.stop(self.back_right_wheel)
        self.stop(self.front_left_wheel)
        self.stop(self.back_left_wheel)

    def cleanup(self):
        if self.pwm:
            for pwm in self.pwm.values():
                try:
                    pwm.stop()
                except Exception:
                    pass
            self.pwm = None  # Break all references
        for pin in self.pins:
            try:
                GPIO.output(pin, GPIO.LOW)
            except Exception:
                pass
        try:
            GPIO.cleanup()
        except Exception:
            pass