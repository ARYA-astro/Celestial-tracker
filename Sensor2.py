
import smbus2
import time
import math

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

# --- 3. Read Raw 16-bit Hardware Data ---
def read_block_data(addr, start_reg):
    # Read 6 consecutive bytes starting from the data register (X_Low, X_High, Y_Low, Y_High, Z_Low, Z_High)
    # We use read_i2c_block_data because the hardware auto-increments register addresses to dump all 3 axes at once
    data = bus.read_i2c_block_data(addr, start_reg, 6)
    
    # Convert the 8-bit pairs into single 16-bit signed integers (twos-complement)
    x = (data[1] << 8) | data[0]
    if x >= 32768: x -= 65536
        
    y = (data[3] << 8) | data[2]
    if y >= 32768: y -= 65536
        
    z = (data[5] << 8) | data[4]
    if z >= 32768: z -= 65536
        
    return x, y, z

# --- 4. The Orientation Math Pipeline ---
def get_orientation():
    # 0x28 is the starting data register for Accelerometer (X, Y, Z data block)
    ax, ay, az = read_block_data(ACCEL_ADDR, 0x28 | 0x80) # 0x80 enables auto-increment auto-read
    
    # 0x03 is the starting data register for Magnetometer (LSM303 mag registers are big-endian usually)
    mx, my, mz = read_block_data(MAG_ADDR, 0x03)

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

# --- Main Execution Loop ---
if __name__ == "__main__":
    try:
        init_sensor()
        print("Starting Star Tracker Engine... Press Ctrl+C to Stop.")
        while True:
            pitch, roll, heading = get_orientation()
            
            # Clean output format for your display
            print(f"Heading: {heading:6.1f}° N | Pitch (Tilt): {pitch:+5.1f}° | Roll: {roll:+5.1f}°")
            
            time.sleep(0.2)  # Update 5 times a second so the Pi CPU doesn't spike
            
    except KeyboardInterrupt:
        print("\nClosing I2C Bus cleanly. Tracker Stopped.")