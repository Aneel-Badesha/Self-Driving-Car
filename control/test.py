import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Motor pins (using pin 16)
# Motor 1: pins 23, 24
# Motor 2: pins 25, 16
# Motor 3: pins 5, 6
# Motor 4: pins 12, 13
pins = [23, 24, 25, 16, 5, 6, 12, 13]

for pin in pins:
    try:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        print(f"Pin {pin} configured successfully")
    except Exception as e:
        print(f"Pin {pin} failed: {e}")

# Test all motors forward
GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.LOW)

GPIO.output(25, GPIO.HIGH)
GPIO.output(16, GPIO.LOW)

GPIO.output(5, GPIO.HIGH)
GPIO.output(6, GPIO.LOW)

GPIO.output(12, GPIO.HIGH)
GPIO.output(13, GPIO.LOW)

time.sleep(20)

# Stop all motors
for pin in pins:
    GPIO.output(pin, GPIO.LOW)

GPIO.cleanup()
