import os, time
from skyfield.api import Loader, Star, wgs84
from skyfield.data import hipparcos

HIP_NUMBERS = {
    # --- Top Brightest Stars ---
    "Sirius": 32349,
    "Canopus": 30438,
    "Alpha Centauri": 71683,
    "Arcturus": 69673,
    "Vega": 91262,
    "Capella": 24608,
    "Rigel": 24436,
    "Procyon": 37279,
    "Betelgeuse": 27989,
    "Achernar": 7588,
    "Hadar": 68702,
    "Altair": 97649,
    "Aldebaran": 21421,
    "Antares": 80763,
    "Spica": 65474,
    "Pollux": 37826,
    "Fomalhaut": 113368,
    "Deneb": 102098,
    "Mimosa": 62434,
    "Regulus": 49669,

    # --- Famous Navigation & Constellation Stars ---
    "Polaris": 11767,
    "Castor": 36850,
    "Bellatrix": 26727,
    "Elnath": 25428,
    "Alnilam": 26311,
    "Alnitak": 26727,
    "Saiph": 27366,
    "Alioth": 62956,
    "Dubhe": 54061,
    "Merak": 53910,
    "Phecda": 58001,
    "Megrez": 59774,
    "Mizar": 65378,
    "Alkaid": 67301,
    "Alcor": 65477,

    # --- Other Notable Stars ---
    "Tarazed": 97278,
    "Algol": 14576,
    "Mira": 10826,
    "Proxima Centauri": 70890,
    "Barnard's Star": 87937,
    "Thuban": 68756,
    "Hamal": 9884,
    "Denebola": 57632,
    "Alphard": 46390,
    "Sadr": 100453,
    "Albireo": 95947,
    "Rasalhague": 86032,
    "Scheat": 113889,
    "Markab": 113963,
    "Alpheratz": 677,
    "Enif": 107315
}
# 1. Setup a clean local directory to store catalog data offline
# This ensures it downloads ONCE and works offline forever.
DATA_DIR = './astrometry_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

load = Loader(DATA_DIR)
ts = load.timescale()

# 2. Define the observer location (Update with your coaching center coordinates)
# Elevation is in meters
planets = load('de421.bsp')
earth = planets['earth']
my_location = earth + wgs84.latlon(latitude_degrees=30.7333, longitude_degrees=76.7794, elevation_m=350)

print("Loading Hipparcos Star Catalog into memory...")

# 3. Load the star catalog (downloads on first run, loads from disk after)
with load.open(hipparcos.URL) as f:
    raw_df = hipparcos.load_dataframe(f)

print(f"Total stars loaded from master file: {len(raw_df)}")

# 4. Filter out faint objects to protect Raspberry Pi RAM
# Magnitude <= 6.0 keeps only the stars visible to the naked eye (~9,000 stars)
MAGNITUDE_LIMIT = 6.0
visible_stars_df = raw_df[raw_df['magnitude'] <= MAGNITUDE_LIMIT]
print(f"Catalog filtered! Active trackable stars (Magnitude <= {MAGNITUDE_LIMIT}): {len(visible_stars_df)}")

# 5. Helper function to fetch and calculate target angles
def get_star_altaz(hip_id, tracking_time):
    try:
        # Extract the star directly from our filtered dataframe row using its HIP ID
        target_star = Star.from_dataframe(visible_stars_df.loc[hip_id])
        
        # Run the standard observational tracking pipeline
        astrometric = my_location.at(tracking_time).observe(target_star)
        alt, az, distance = astrometric.apparent().altaz()
        
        return alt.degrees, az.degrees
    except KeyError:
        print(f"Error: Star HIP {hip_id} is either too faint or doesn't exist in the database.")
        return None, None
    
def list_available_stars(tracking_time):
    final_list = []
    print("\n--- Available Trackable Stars ---")
    for i in HIP_NUMBERS:
        hip_id = HIP_NUMBERS[i]
        alt = get_star_altaz(hip_id, tracking_time)
        if alt > 0:
            final_list.append(i)
    return final_list        

def get_local_time():
    from datetime import datetime
    import pytz
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    return current_time.strftime("%Y-%m-%d %H:%M:%S") 

def time_at_which_star_is_visible(hip_id):
    # This function calculates the next time a star will be above the horizon
    # For simplicity, we will check every 10 minutes for the next 24 hours
    from datetime import timedelta
    current_time = ts.now()
    for i in range(0, 144):  # Check for the next 24 hours (144 intervals of 10 minutes)
        future_time = current_time + timedelta(minutes=i*10)
        alt, az = get_star_altaz(hip_id, future_time)
        if alt > 0:
            return future_time.utc_strftime()
    return "The star will not be visible in the next 24 hours."           


# --- Quick Test Execution ---
if __name__ == '__main__':
    # Use the live system clock converted for the Skyfield engine
    from datetime import datetime
    import pytz
    
    local_tz = pytz.timezone('Asia/Kolkata')
    current_time = ts.from_datetime(local_tz.localize(datetime.now()))
    
    print(f"Hi! Welcome to the Star Tracking System. Current time: {get_local_time()}")
    time.delay(1)
    print("Calculating Altitude and Azimuth for all available stars...")
    time.delay(1)
    print("Note: Only stars above the horizon (Altitude >= 0°) will be displayed.")
    time.delay(1)
    Answer = input("Do you want to see the list of available stars or Do you want to track a specific star? (Type 'list' or 'track'): ").strip().lower()
    time.delay(1)
    
    if Answer == "list" or Answer == "l":
        list_available_stars(current_time)
        Answer2 = input("Do you want to track a specific star now? (Type 'yes' or 'no'): ").strip().lower()
        if Answer2 == "yes" or Answer2 == "y":
            star_name = input("Enter the name of the star you want to track (e.g., Sirius, Vega): ").strip()
            if star_name in HIP_NUMBERS:
                stars = list_available_stars(current_time)
                if star_name in stars:
                    altitude, azimuth = get_star_altaz(HIP_NUMBERS[star_name], current_time)
                    print(f"\nTracking {star_name}...")
                    print(f"Altitude: {altitude:.2f} degrees")
                    print(f"Azimuth:  {azimuth:.2f} degrees")
                elif star_name not in stars:
                    print(f"Sorry, {star_name} is currently below the horizon and cannot be tracked.")
                    time.delay(1)    
                    
    
