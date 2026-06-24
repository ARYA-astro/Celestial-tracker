import math
import time
from smbus2 import SMBus

# Open I2C bus 1
bus = SMBus(1)

# Sensor I2C Device Addresses
ACCEL_ADDR = 0x19
MAG_ADDR = 0x1E

# --- REGISTER INITIALIZATION ---
# Accelerometer: Turn on normal power mode, 100Hz refresh rate, enable X, Y, Z axes
# Register 0x20 (CTRL_REG1_A) = 0x57 (binary 01010111)
bus.write_byte_data(ACCEL_ADDR, 0x20, 0x57)

# Magnetometer: Set to Continuous-conversion mode so it updates data constantly
# Register 0x02 (MR_REG_M) = 0x00
bus.write_byte_data(MAG_ADDR, 0x02, 0x00)


def convert_to_signed_16(high, low):
    """Combines two 8-bit bytes into a single signed 16-bit integer."""
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value

def actual_accel(r1, r2, r3):
    roll = math.atan2(r2, r3)
    pitch = math.atan2(-r1, math.sqrt(r2**2 + r3**2))
    
    return roll, pitch

def actual_mag(m1, m2, m3, pitch, roll):
    flat_X = m1 * math.cos(pitch) + m3 * math.sin(pitch)
    flat_Y = m1 * math.sin(roll) * math.sin(pitch) + m2 * math.cos(roll) - m3 * math.sin(roll) * math.cos(pitch)
    heading = math.atan2(-flat_Y, flat_X)
    actual_heading = heading * (180 / math.pi)

    return actual_heading


print("--- GY-511 Raw SMBus2 Tracker Running ---")

try:
    while True:
        # 1. READ ACCELEROMETER DATA
        # 0x28 is OUT_X_L_A. We add 0x80 (making it 0xA8) to enable auto-increment
        # so we can read all 6 bytes (X_L, X_H, Y_L, Y_H, Z_L, Z_H) in one transaction.
        accel_data = bus.read_i2c_block_data(ACCEL_ADDR, 0x28 | 0x80, 6)
        
        accel_x = convert_to_signed_16(accel_data[1], accel_data[0])
        accel_y = convert_to_signed_16(accel_data[3], accel_data[2])
        accel_z = convert_to_signed_16(accel_data[5], accel_data[4])

        # 2. READ MAGNETOMETER DATA
        # 0x03 is OUT_X_H_M. The magnetometer automatically auto-increments.
        # Note: Magnetometer byte layout is High then Low, and the order is X, Z, Y!
        mag_data = bus.read_i2c_block_data(MAG_ADDR, 0x03, 6)
        
        mag_x = convert_to_signed_16(mag_data[0], mag_data[1])
        mag_z = convert_to_signed_16(mag_data[2], mag_data[3])
        mag_y = convert_to_signed_16(mag_data[4], mag_data[5])
        
        roll, pitch = actual_accel(accel_x, accel_y, accel_z)
        heading = actual_mag(mag_x, mag_y, mag_z, pitch, roll)
        print(f"Roll: {math.degrees(roll):.2f} | Pitch: {math.degrees(pitch):.2f} | Heading: {heading:.2f}")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nClosing I2C bus safely.")
    bus.close()

