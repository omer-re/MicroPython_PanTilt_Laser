from machine import Pin, PWM, Timer
import time


class PanTilt:
    # Constants
    PAN_MIN, PAN_MAX = 30, 150
    TILT_MIN, TILT_MAX = 50, 150
    STEP = 1

    def __init__(self, pan_pin=18, tilt_pin=5, laser_pin=17):
        # Initialize pins
        self.pan_servo = PWM(Pin(pan_pin), freq=50)
        self.tilt_servo = PWM(Pin(tilt_pin), freq=50)
        self.laser = Pin(laser_pin, Pin.OUT)
        # Initial Position
        self.pan_angle = self.update_servo(self.pan_servo, 90)
        self.tilt_angle = self.update_servo(self.tilt_servo, 90)

        # Direction Flags
        self.pan_direction = 1
        self.tilt_direction = 1
        print('pantilt init')
        # self.set_starting_point(90, 90)
        self.laser_on()
        time.sleep(2)
        self.laser_off()

    def update_servo(self, servo, angle):
        min_duty = 40
        max_duty = 115
        duty = int(min_duty + (angle / 180) * (max_duty - min_duty))

        duty = max(0, min(1023, duty))
        servo.duty(duty)

    def laser_on(self):
        self.laser.value(1)

    def laser_off(self):
        self.laser.value(0)

    def move_laser(self):
        self.laser_on()
        self.update_servo(self.pan_servo, self.pan_angle)
        self.update_servo(self.tilt_servo, self.tilt_angle)
        time.sleep(0.05)

    def set_starting_point(self, start_pan_angle, start_tilt_angle):
        # self.pan_angle = max(self.PAN_MIN, min(self.PAN_MAX, start_pan_angle))
        # self.tilt_angle = max(self.TILT_MIN, min(self.TILT_MAX, start_tilt_angle))
        self.update_servo(self.pan_servo, 90)
        self.update_servo(self.tilt_servo, 90)
        self.move_laser()

    def run(self, duration=None):
        print('pantilt run')
        start_time = time.time()

        try:
            while True:
                if duration and time.time() - start_time >= duration:
                    break
                # print(time.time() - start_time)

                self.laser_on()  # Turn laser ON
                self.pan_angle += self.pan_direction * self.STEP
                self.tilt_angle += self.tilt_direction * self.STEP

                if self.pan_angle <= self.PAN_MIN or self.pan_angle >= self.PAN_MAX:
                    self.pan_direction *= -1

                if self.tilt_angle <= self.TILT_MIN or self.tilt_angle >= self.TILT_MAX:
                    self.tilt_direction *= -1

                self.move_laser()
                time.sleep(0.01)
        finally:
            self.laser_off()  # Turn laser OFF
            self.set_starting_point(90, 90)

    def run_for_duration(self, duration):
        print(f'pantilt run for duration {duration}')
        self.run(duration=duration)

    def test_circle(self):
        for i in range(90, 10, 2):
            self.pan_angle = i
            self.tilt_angle = i
            self.move_laser()
            time.sleep(0.1)

        for i in range(10, 170, 2):
            self.pan_angle = i
            self.tilt_angle = i
            self.move_laser()
            time.sleep(0.1)
        for i in range(170, 10, -2):
            self.pan_angle = i
            self.tilt_angle = i
            self.move_laser()
            time.sleep(0.1)
        for i in range(10, 90, 2):
            self.pan_angle = i
            self.tilt_angle = i
            self.move_laser()
            time.sleep(0.1)


