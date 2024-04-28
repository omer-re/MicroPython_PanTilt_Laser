from pan_tilt import PanTilt
from time_wrapper import *
import machine
import time
import network
from time import sleep
import ntptime
from machine import Pin
from creds import WIFI_KEYS
wifi_connected = 0
max_retries = 8
# Global station variable
station = network.WLAN(network.STA_IF)

# Replace '2' with the correct GPIO pin number for your ESP32 board
led = Pin(2, Pin.OUT)
button = Pin(34, Pin.IN)
halt = Pin(33, Pin.IN, Pin.PULL_UP)

counter = 0
prev_button = 0


def connect():
    global station  # Indicate that we're using the global station variable
    global wifi_connected
    keys_ = WIFI_KEYS
    sleep(0.2)
    station.active(True)
    stat = station.scan()
    best_ap = (None, 0, 0, -100)
    SSID = ''
    for s in stat:
        check = s[0].decode('utf-8')
        if check in keys_.keys() and s[3] > best_ap[3]:
            best_ap = s
            print(f'The best Access Point found is {best_ap[0]}')
            SSID = best_ap[0].decode('utf-8')

    if best_ap[0] != None:
        station.connect(SSID, keys_[SSID])
        while station.isconnected() == False:
            pass
        print(f'Connected to {SSID}')
        wifi_connected = 1
    else:
        wifi_connected = 0
        print("No suitable Access Point found.")
    return wifi_connected


def attempt_function_call(func, max_retries):
    """
    Attempts to call the given function until it returns True or the maximum number of retries is reached.

    :param func: The function to be called.
    :param max_retries: Maximum number of attempts.
    :return: True if the function call was successful, False otherwise.
    """
    for attempt in range(1, max_retries + 1):
        try:
            if func():
                print(f"Attempt {attempt}: Success.")
                return True
            else:
                print(f"Attempt {attempt}: Function returned False.")
        except Exception as e:
            print(f"Attempt {attempt}: Failed with error: {e}")

        if attempt == max_retries:
            print("Max attempts reached. Giving up.")
            return False
        else:
            print("Retrying...")
            time.sleep(1)  # Wait for 1 second before retrying


def check_time():
    current_time = synchronizer.get_current_datetime()
    current_hour, current_minute = current_time[3], current_time[4]
    time_pairs = [(8, 25), (16, 25), (22, 25), (11, 36), (11, 38), (12, 45), (12, 50), (13, 13), (14, 14), (15, 15),(16,25),(17,25),(18,25),(19,25)]
    print(f'check_time time is {current_hour}:{current_minute}')
    if (current_hour, current_minute) in time_pairs:
        print(f"launched by time {current_hour}:{current_minute}")
        pan_tilt.run_for_duration(120)
        pan_tilt.laser_off()


def run_for_button():
    global prev_button
    res = button.value()
    if res==1 and res != prev_button:
        print("run for button")
        pan_tilt.run_for_duration(120)
        pan_tilt.laser_off()
    prev_button = button.value()


def timer_callback(t):
    global counter
    counter += 1
    counter=counter%1200

    if halt.value() == 0:
        print("HALT")
        # To stop the timer temporarily
        timer.deinit()
        #time.sleep(7)
        # To restart the timer
        #timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_callback)

    if counter % 2 == 0:
        run_for_button()
        print("check button")

    # Task 2: Runs every 3 ticks
    if counter % 10 == 0:
        print("check_time")
        check_time()

    if counter % 35 == 0:
        pan_tilt.laser_on()
        time.sleep(2)
        pan_tilt.laser_off()

if halt.value() != 0:
    time.sleep(5)
    # Set up a timer
    timer = Timer(1)
    timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_callback)

pan_tilt = None
if __name__ == "__main__":
    # connect to wifi
    attempt_function_call(connect, max_retries)

    synchronizer = TimeSynchronizer()
    prev_button = button.value()
    if halt.value() != 0:
        # init pan tilt
        pan_tilt = PanTilt()
        # sync time

        # pan_tilt.move_to_angle_in_steps(90)
        # test pan tilt
        pan_tilt.test_circle()
        time.sleep(1)
    # set starting point
    print(f"Current time: {synchronizer.get_current_datetime()[3]}:{synchronizer.get_current_datetime()[4]}")

    # run using timer interrupts
