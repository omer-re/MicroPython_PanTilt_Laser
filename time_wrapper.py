import ntptime
import machine
import utime
from machine import Timer


class TimeSynchronizer:
    def __init__(self):
        self.timer = Timer(0)
        self.sync_time()
        # Set the timer to sync time every 2 hours (7200 seconds)
        self.timer.init(period=7200 * 1000, mode=Timer.PERIODIC, callback=lambda t: self.sync_time())

    def sync_time(self):
        try:
            # Synchronize with NTP server
            ntptime.settime()
            # Adjust for Israel's local time (UTC+2 or UTC+3 for DST)
            self.adjust_for_ist()
        except:
            pass  # Handle errors (e.g., network issues)

    def adjust_for_ist(self):
        # Get the current time
        year, month, mday, hour, minute, second, weekday, yearday = utime.localtime()
        hour += 3
        """# Adjust for DST if necessary
        if self.is_dst(year, month, mday):
            hour += 3  # UTC+3 for DST
        else:
            hour += 2  # UTC+2 for standard time"""
        # Set the adjusted time
        utime.localtime(utime.mktime((year, month, mday, hour, minute, second, weekday, yearday)))

    @staticmethod
    def is_dst(year, month, day):
        """
        Determine if the given date is in Daylight Saving Time (DST) in Israel.
        DST starts at 02:00 AM on the last Friday before April 2nd and
        ends at 02:00 AM on the last Sunday of October.
        """

        # Check if the month is outside of DST period
        if month < 3 or month > 10:
            return False

        # For April through September, DST is always in effect
        if 3 < month < 10:
            return True

        # Calculate the last Friday before April 2nd
        april_2nd = utime.mktime((year, 4, 2, 0, 0, 0, 0, 0))
        last_friday_before_april_2nd = april_2nd - ((utime.localtime(april_2nd)[6] + 2) % 7) * 86400

        # Calculate the last Sunday of October
        october_31st = utime.mktime((year, 10, 31, 0, 0, 0, 0, 0))
        last_sunday_of_october = october_31st - (utime.localtime(october_31st)[6] % 7) * 86400

        # Convert the current date to seconds since epoch
        current_date = utime.mktime((year, month, day, 0, 0, 0, 0, 0))

        # Check if the current date is within the DST period
        return last_friday_before_april_2nd <= current_date < last_sunday_of_october

    def get_current_datetime(self):
        # Get the current UTC time
        year, month, mday, hour, minute, second, weekday, yearday = utime.localtime()

        # Adjust for Israel's local time (UTC+2 or UTC+3 for DST)
        if self.is_dst(year, month, mday):
            hour += 3  # UTC+3 for DST
        else:
            hour += 2  # UTC+2 for standard time

        # Handle cases where the hour adjustment rolls over to the next day
        if hour >= 24:
            hour -= 24
            mday += 1

        # Return the adjusted time
        return (year, month, mday, hour, minute, second, weekday, yearday)


# Usage example (this will be executed on boot if this script is main)
if __name__ == "__main__":
    synchronizer = TimeSynchronizer()
    print("Current time:", synchronizer.get_current_datetime())

