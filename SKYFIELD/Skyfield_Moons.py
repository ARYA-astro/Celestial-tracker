import os
from skyfield.api import load, wgs84

file = r"D:\Downloads\jup365.bsp"
eph1 = load(file)
eph2 = load('de421.bsp')
my_location = wgs84.latlon(28.6139, 77.2090)

print("Loaded ephemeris...")
print(f"Available bodies in the ephemeris: {eph1}")

jupiter = eph1['jupiter barycenter']
metis = eph1['metis']


ts = load.timescale()
t = ts.now()

observer = eph2['earth'] + my_location
position1 = observer.at(t).observe(jupiter)
position2 = observer.at(t).observe(metis)
alt1, az1, distance1 = position1.apparent().altaz()
alt2, az2, distance2 = position2.apparent().altaz()

print(f"Altitude of Jupiter: {alt1.degrees:.2f} degrees")
print(f"Azimuth of Jupiter:  {az1.degrees:.2f} degrees")
print(f"Distance to Jupiter: {distance1.km:.2f} km")

print(f"Altitude of Metis: {alt2.degrees:.2f} degrees")
print(f"Azimuth of Metis:  {az2.degrees:.2f} degrees")
print(f"Distance to Metis: {distance2.km:.2f} km")
