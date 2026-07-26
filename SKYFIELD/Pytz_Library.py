import pytz, time
from datetime import datetime, timedelta

tz = pytz.timezone("Asia/Kolkata")
dt = tz.localize(datetime.now())  # Localize the datetime to the specified timezone

delta = timedelta(seconds=1)

initial_time = dt  # Store the initial datetime

while True:
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        print("Calculating for midnight...")
        delta_time = dt - initial_time  # Calculate the time difference from the initial time
        delta_time = int(delta_time.total_seconds())
        total_hours, remainder = divmod(delta_time, 3600)
        total_minutes, total_seconds = divmod(remainder, 60)
        
        print(f"{total_hours} Hours, {total_minutes} minutes and {total_seconds} second")
        break  # Exit the loop after reaching midnight
    dt += delta

