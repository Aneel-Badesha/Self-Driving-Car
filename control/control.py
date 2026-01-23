import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Motor 1: pins 23, 24 front_right_wheel
# Motor 2: pins 25, 16 back_right_wheel
# Motor 3: pins 5, 6 front_left_wheel
# Motor 4: pins 12, 13 back_left_wheel
front_right_wheel = [23, 24]
back_right_wheel = [25, 16]
front_left_wheel = [5, 6]
back_left_wheel = [12, 13]
pins = [23, 24, 25, 16, 5, 6, 12, 13]

def gpio_setup(wheel):
    for pin in wheel:
        try:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            print(f"Pin {pin} configured successfully")
        except Exception as e:
            print(f"Pin {pin} failed: {e}")

def drive(speed, direction, wheel):
    if direction == FORWARD:
        GPIO.output(wheel[0], GPIO.HIGH)
        GPIO.output(wheel[1], GPIO.LOW)
    else:
        GPIO.output(wheel[0], GPIO.LOW)
        GPIO.output(wheel[1], GPIO.HIGH)

def stop(wheel):

def speed():