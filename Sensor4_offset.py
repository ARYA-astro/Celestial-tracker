
import smbus2
import time
import math

# --- 0. Target Orientation Setup ---

# Target Altitude is the angle above the horizon you want to point the telescope, in degrees (0° to 90°)
target_alt = 60.0   
# Target Azimuth is the direction you want to point the telescope, in degrees from North (0° to 360°) 
target_az = 120.0

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

# --- 2. Calibration Offsets ---
# Adjust these values to match your sensor's bias. Positive values subtract from the raw reading.
OFFSET_AX = 0.0
OFFSET_AY = 0.0
OFFSET_AZ = 0.0
OFFSET_MX = 0.0
OFFSET_MY = 0.0
OFFSET_MZ = 0.0  

# --- 2. Initialize the Hardware Over I2C ---
def init_sensor():
    try:
        # Write 0x57 to CTRL_REG1_A: Power on accelerometer, 100Hz data rate, enable all 3 axes (X, Y, Z)
        bus.write_byte_data(ACCEL_ADDR, CTRL_REG1_A, 0x57)
        
        # Write 0x10 to CRA_REG_M: Set Magnetometer data output rate to 15Hz
        bus.write_byte_data(MAG_ADDR, CRA_REG_M, 0x10)
        
        # Write 0x00 to MR_REG_M: Set Magnetometer to Continuous Conversion Mode
        bus.write_byte_data(MAG_ADDR, MR_REG_M, 0x00)
        print("GY-511 Sensor Initialized Successfully.")
    except OSError as e:
        raise RuntimeError(
            f"Could not initialize the sensor over I2C. Check wiring, power, bus number, and I2C enablement. Original error: {e}"
        ) from e

# --- 3. Read Raw 16-bit Hardware Data ---
def read_block_data(addr, start_reg, offsets=(0.0, 0.0, 0.0)):
    try:
        # Read 6 consecutive bytes starting from the data register (X_Low, X_High, Y_Low, Y_High, Z_Low, Z_High)
        # We use read_i2c_block_data because the hardware auto-increments register addresses to dump all 3 axes at once
        data = bus.read_i2c_block_data(addr, start_reg, 6)
    except OSError as e:
        raise RuntimeError(
            f"I2C read failed for address 0x{addr:X} register 0x{start_reg:X}. Check the sensor wiring, address, and I2C bus. Original error: {e}"
        ) from e
    
    # Convert the 8-bit pairs into single 16-bit signed integers (twos-complement)
    x = (data[0] << 8) | data[1]
    if x >= 32768: x -= 65536
        
    z = (data[2] << 8) | data[3]
    if z >= 32768: z -= 65536
        
    y = (data[4] << 8) | data[5]
    if y >= 32768: y -= 65536

    return x, z, y

# --- 4. The Orientation Math Pipeline ---
def get_orientation(offset_mx=0.0, offset_my=0.0):
    # 0x28 is the starting data register for Accelerometer (X, Y, Z data block)
    ax, ay, az = read_block_data(
        ACCEL_ADDR,
        0x28 | 0x80
    ) # 0x80 enables auto-increment auto-read
    
    # 0x03 is the starting data register for Magnetometer (LSM303 mag registers are big-endian usually)
    mx, mz, my = read_block_data(
        MAG_ADDR,
        0x03
    )

    # Apply calibration offsets so the heading calculation uses the calibrated values.
    mx -= offset_mx
    my -= offset_my

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
        
    return math.degrees(pitch), math.degrees(roll), heading_deg

def get_offset(target_time):
    min_mx = float('inf')
    max_mx = float('-inf')
    min_my = float('inf')
    max_my = float('-inf')

    seconds_passed = 0
    last_print_time = time.time()

    while seconds_passed < target_time:
        mx, mz, my = read_block_data(MAG_ADDR, 0x03)
        
        # Update min/max values for calibration
        min_mx = min(min_mx, mx)
        max_mx = max(max_mx, mx)
        min_my = min(min_my, my)
        max_my = max(max_my, my)

        offset_mx = (max_mx + min_mx) / 2
        offset_my = (max_my + min_my) / 2


        # Print progress every second
        current_time = time.time()
        if current_time - last_print_time >= 1:
            seconds_passed += 1
            last_print_time = current_time
            print(f"Calibration Progress: {seconds_passed}/{target_time} seconds")

    return offset_mx, offset_my        





# --- Main Execution Loop ---
if __name__ == "__main__":
    try:
        init_sensor()
        print("Starting Star Tracker Engine... Press Ctrl+C to Stop.")
        print("Calibrating Magnetometer Offsets. Please rotate the sensor in all directions for 20 seconds...")
        offset_mx, offset_my = get_offset(20)  # Calibrate for 20 seconds
        print(f"Calibration Complete. Magnetometer Offsets: MX Offset: {offset_mx:.2f}, MY Offset: {offset_my:.2f}")

        while True:
            pitch, roll, heading = get_orientation(offset_mx, offset_my)

            actual_pitch = pitch - OFFSET_AX
            actual_roll = roll - OFFSET_AY
            
            # Clean output format for your display
            print(f"Heading: {heading:6.1f}° N | Pitch (Tilt): {actual_pitch:+5.1f}° | Roll: {actual_roll:+5.1f}°")
            print(f"Displacement from Target: Altitude Error: {actual_pitch - target_alt:+5.1f}° | Azimuth Error: {heading - target_az:+5.1f}°")
            
            time.sleep(0.2)  # Update 5 times a second so the Pi CPU doesn't spike
            
    except KeyboardInterrupt:
        print("\nClosing I2C Bus cleanly. Tracker Stopped.")
    except Exception as e:
        print(f"\nSensor error: {e}")