import smbus2
import time
import math

from Sensor2 import read_block_data

# --- 1. Hardware Pin & Address Setup ---
# The Raspberry Pi 3 B+ uses I2C bus 1 (Pins: GPIO 2 is SDA, GPIO 3 is SCL)
BUS_NUMBER = 1
bus = smbus2.SMBus(BUS_NUMBER)

# GY-511 (LSM303) Hardware Addresses on the I2C Bus
ACCEL_ADDR = 0x19  # Accelerometer I2C address
MAG_ADDR   = 0x1E  # Magnetometer I2C address

# Sensor Internal Register Map (Where the data hides)
CTRL_REG1_A = 0x20  # Control register to turn on Accelerometer
CRA_REG_M   = 0x00  # Control register to turn on Magnetometer
MR_REG_M    = 0x02  # Mode register for Magnetometer

# --- 2. Initialize the Hardware Over I2C ---
def init_sensor():
    # Write 0x57 to CTRL_REG1_A: Power on accelerometer, 100Hz data rate, enable all 3 axes (X, Y, Z)
    bus.write_byte_data(ACCEL_ADDR, CTRL_REG1_A, 0x57)
    
    # Write 0x10 to CRA_REG_M: Set Magnetometer data output rate to 15Hz
    bus.write_byte_data(MAG_ADDR, CRA_REG_M, 0x10)
    
    # Write 0x00 to MR_REG_M: Set Magnetometer to Continuous Conversion Mode
    bus.write_byte_data(MAG_ADDR, MR_REG_M, 0x00)
    print("GY-511 Sensor Initialized Successfully.")

def read_accel_data(ACCEL_ADDR, start_reg):
    # Read 6 consecutive bytes starting from the data register (X_Low, X_High, Y_Low, Y_High, Z_Low, Z_High)
    data = bus.read_i2c_block_data(ACCEL_ADDR, start_reg, 6)
    
    # Convert the 8-bit pairs into single 16-bit signed integers (twos-complement)
    x = (data[1] << 8) | data[0]
    if x >= 32768: x -= 65536
        
    y = (data[3] << 8) | data[2]
    if y >= 32768: y -= 65536
        
    z = (data[5] << 8) | data[4]
    if z >= 32768: z -= 65536
        
    return x, y, z

def read_mag_data(MAG_ADDR, start_reg):
    # Read 6 consecutive bytes starting from the data register (X_High, X_Low, Z_High, Z_Low, Y_High, Y_low)
    data = bus.read_i2c_block_data(MAG_ADDR, start_reg, 6)

    # Convert the 8-bit pairs into single 16-bit signed integers (twos-complement)
    x = (data[0] << 8) | data[1]
    if x >= 32768: x -= 65536

    z = (data[2] << 8) | data[3]
    if z >= 32768: z -= 65536

    y = (data[4] << 8) | data[5]
    if y >= 32768: y -= 65536
        
    return x, y, z

def calibrate_magnetometer():
    print("Calibrating Magnetometer...")
    print("Please rotate the sensor in all directions for 30 seconds.")
    
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')

    start_time = time.time()
    second = start_time
    while second <= 20:
        mx, my, mz = read_mag_data(MAG_ADDR, 0x03)
        
        # Update min and max values for X and Y axes
        min_x = min(min_x, mx)
        max_x = max(max_x, mx)
        min_y = min(min_y, my)
        max_y = max(max_y, my)

        time.sleep(0.1)  # Small delay to avoid overwhelming the I2C bus
        start_time = time.time()
        if start_time - second >= 1:
            second += 1
            print(f"Time elapsed: {second} seconds")

    # Calculate offsets as the average of min and max values
    offset_x = (max_x + min_x) / 2
    offset_y = (max_y + min_y) / 2

    print(f"Calibration complete. Offsets: X={offset_x}, Y={offset_y}")
    return offset_x, offset_y

def get_orientation(offset_x, offset_y):
    # 0x28 is the starting data register for Accelerometer (X, Y, Z data block)
    ax, ay, az = read_accel_data(ACCEL_ADDR, 0x28 | 0x80) # 0x80 enables auto-increment auto-read
    
    # 0x03 is the starting data register for Magnetometer (LSM303 mag registers are big-endian usually)
    mx, my, mz = read_mag_data(MAG_ADDR, 0x03)
    mx -= offset_x  # Apply user-defined offsets to magnetometer readings
    my -= offset_y  # Apply user-defined offsets to magnetometer readings

    # Step A: Pitch & Roll calculation (Radians)
    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2))

    # Step B: Tilt-Compensation (Flattening X and Y)
    xh = mx * math.cos(pitch) + mz * math.sin(pitch)    
    yh = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)

    # Step C: Calculate Heading using arctan2 to prevent division by zero crashes
    heading_rad = math.atan2(-yh, xh)       
    heading_deg = math.degrees(heading_rad)

    # Standardize heading scale to absolute 0 - 360 degrees
    if heading_deg < 0:
        heading_deg += 360

    heading_deg += 1.3  # Apply a small correction factor to the heading (empirically determined)    

    return math.degrees(pitch), math.degrees(roll), heading_deg    

# --- Main Execution Loop ---
if __name__ == "__main__":
    try:
        init_sensor()
        offset_x, offset_y = calibrate_magnetometer()
        print("Starting Star Tracker Engine... Press Ctrl+C to Stop.")
        while True:
            pitch, roll, heading = get_orientation(offset_x, offset_y)
            
            # Clean output format for your display
            print(f"Heading: {heading:6.1f}° N | Pitch (Tilt): {pitch:+5.1f}° | Roll: {roll:+5.1f}°")
            
            time.sleep(0.2)  # Update 5 times a second so the Pi CPU doesn't spike

    except KeyboardInterrupt:
        print("\nClosing I2C Bus cleanly. Tracker Stopped.")        