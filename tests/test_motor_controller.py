import importlib
import sys
import types
import unittest


class FakePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.start_calls = []
        self.duty_cycle_calls = []
        self.stop_calls = 0

    def start(self, duty_cycle):
        self.start_calls.append(duty_cycle)

    def ChangeDutyCycle(self, duty_cycle):
        self.duty_cycle_calls.append(duty_cycle)

    def stop(self):
        self.stop_calls += 1


class FakeGPIO(types.ModuleType):
    BCM = "BCM"
    OUT = "OUT"
    LOW = 0
    HIGH = 1

    def __init__(self):
        super().__init__("RPi.GPIO")
        self.setmode_calls = []
        self.setup_calls = []
        self.output_calls = []
        self.cleanup_calls = 0
        self.pwms = {}

    def setmode(self, mode):
        self.setmode_calls.append(mode)

    def setup(self, pin, mode, initial=None):
        self.setup_calls.append((pin, mode, initial))

    def output(self, pin, value):
        self.output_calls.append((pin, value))

    def cleanup(self):
        self.cleanup_calls += 1

    def PWM(self, pin, frequency):
        pwm = FakePWM(pin, frequency)
        self.pwms[pin] = pwm
        return pwm


class MotorControllerTests(unittest.TestCase):
    def setUp(self):
        self.fake_gpio = FakeGPIO()
        self.fake_rpi = types.ModuleType("RPi")
        self.fake_rpi.GPIO = self.fake_gpio

        self._original_rpi = sys.modules.get("RPi")
        self._original_rpi_gpio = sys.modules.get("RPi.GPIO")

        sys.modules["RPi"] = self.fake_rpi
        sys.modules["RPi.GPIO"] = self.fake_gpio

        if "control.control" in sys.modules:
            del sys.modules["control.control"]

        self.control_module = importlib.import_module("control.control")
        self.MotorController = self.control_module.MotorController

    def tearDown(self):
        if self._original_rpi is None:
            sys.modules.pop("RPi", None)
        else:
            sys.modules["RPi"] = self._original_rpi

        if self._original_rpi_gpio is None:
            sys.modules.pop("RPi.GPIO", None)
        else:
            sys.modules["RPi.GPIO"] = self._original_rpi_gpio

        sys.modules.pop("control.control", None)

    def test_init_sets_gpio_mode_and_wheels(self):
        controller = self.MotorController()

        self.assertEqual(self.fake_gpio.setmode_calls, [self.fake_gpio.BCM])
        self.assertEqual(controller.front_right_wheel, [23, 24])
        self.assertEqual(controller.back_right_wheel, [25, 16])
        self.assertEqual(controller.front_left_wheel, [5, 6])
        self.assertEqual(controller.back_left_wheel, [12, 13])

    def test_setup_all_configures_all_pins_and_starts_pwm(self):
        controller = self.MotorController()
        controller.setup_all()

        setup_pins = [call[0] for call in self.fake_gpio.setup_calls]
        self.assertEqual(set(setup_pins), set(controller.pins))

        expected_pwm_pins = {
            controller.front_right_wheel[0],
            controller.back_right_wheel[0],
            controller.front_left_wheel[0],
            controller.back_left_wheel[0],
        }
        self.assertEqual(set(self.fake_gpio.pwms.keys()), expected_pwm_pins)

        for pin in expected_pwm_pins:
            self.assertEqual(self.fake_gpio.pwms[pin].start_calls, [0])

    def test_drive_clamps_speed_and_sets_forward_direction(self):
        controller = self.MotorController()
        controller.setup_all()

        wheel = controller.front_right_wheel
        controller.drive(controller.FORWARD, wheel, speed=150)

        pwm = self.fake_gpio.pwms[wheel[0]]
        self.assertEqual(pwm.duty_cycle_calls[-1], 100)
        self.assertIn((wheel[0], self.fake_gpio.HIGH), self.fake_gpio.output_calls)
        self.assertIn((wheel[1], self.fake_gpio.LOW), self.fake_gpio.output_calls)

    def test_drive_all_backward_clamps_to_zero(self):
        controller = self.MotorController()
        controller.setup_all()

        controller.drive_all(controller.BACKWARD, speed=-5)

        wheels = [
            controller.front_right_wheel,
            controller.back_right_wheel,
            controller.front_left_wheel,
            controller.back_left_wheel,
        ]

        for wheel in wheels:
            self.assertIn((wheel[0], self.fake_gpio.LOW), self.fake_gpio.output_calls)
            self.assertIn((wheel[1], self.fake_gpio.HIGH), self.fake_gpio.output_calls)
            self.assertEqual(self.fake_gpio.pwms[wheel[0]].duty_cycle_calls[-1], 0)

    def test_set_speed_all_applies_to_all_pwm_channels(self):
        controller = self.MotorController()
        controller.setup_all()

        controller.set_speed_all(25)

        for pwm in self.fake_gpio.pwms.values():
            self.assertEqual(pwm.duty_cycle_calls[-1], 25)

    def test_stop_all_stops_each_wheel(self):
        controller = self.MotorController()
        controller.setup_all()

        controller.stop_all()

        wheels = [
            controller.front_right_wheel,
            controller.back_right_wheel,
            controller.front_left_wheel,
            controller.back_left_wheel,
        ]

        for wheel in wheels:
            self.assertEqual(self.fake_gpio.pwms[wheel[0]].duty_cycle_calls[-1], 0)
            self.assertIn((wheel[0], self.fake_gpio.LOW), self.fake_gpio.output_calls)
            self.assertIn((wheel[1], self.fake_gpio.LOW), self.fake_gpio.output_calls)

    def test_cleanup_stops_pwm_and_cleans_gpio(self):
        controller = self.MotorController()
        controller.setup_all()

        controller.cleanup()

        for pwm in self.fake_gpio.pwms.values():
            self.assertEqual(pwm.stop_calls, 1)

        self.assertIsNone(controller.pwm)
        self.assertEqual(self.fake_gpio.cleanup_calls, 1)


if __name__ == "__main__":
    unittest.main()
