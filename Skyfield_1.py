from skyfield.api import load, wgs84
from datetime import datetime
from pytz import timezone

# 1. Setup the basic data
ts = load.timescale()
eph = load('de421.bsp')
sun, earth = eph['sun'], eph['earth']

# 2. Set your POSITION (Latitude and Longitude)
# Example: Delhi, India (Lat: 28.6, Lon: 77.2)
my_location = wgs84.latlon(28.6139, 77.2090)

# 3. Set the TIME
# This creates a specific time (Year, Month, Day, Hour, Minute)
# We use UTC time to keep it accurate
local_tz = timezone('Asia/Kolkata')  # Set your local timezone
local_time = local_tz.localize(datetime(2024, 6, 21, 17, 30))
specific_time = ts.utc(2024, 6, 21, 12, 0) # June 21, 2024 at 12:00 PM UTC

# 4. Calculate the position
# We "observe" the sun from our location on earth
observer = earth + my_location
astrometric = observer.at(specific_time).observe(sun)
apparent = astrometric.apparent()

# 5. Get Altitude and Azimuth
# Altitude: How high in the sky (0 is horizon, 90 is directly up)
# Azimuth: Compass direction (0 is North, 90 is East, 180 is South)
alt, az, distance = apparent.altaz()

print(f"Time: {specific_time.utc_strftime()}")
print(f"Sun Altitude: {alt.degrees:.2f} degrees")
print(f"Sun Azimuth:  {az.degrees:.2f} degrees")