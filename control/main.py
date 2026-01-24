import time
from control import MotorController as mc

FORWARD = 1
BACKWARD = 0

if __name__ == "__main__":

    try:
        # Create motor controller instance
        motors = mc()
        motors.setup_all()

        # Drive all wheels forward
        motors.drive_all(FORWARD)
        time.sleep(5)
        motors.stop_all()
    finally:
        motors.cleanup()

