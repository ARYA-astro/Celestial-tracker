import serial
import pynmea2


def read_gps(port, baud=9600, timeout=1):
    try:
        with serial.Serial(port, baudrate=baud, timeout=timeout) as ser:
            while True:
                raw_data = ser.readline().decode('ascii', errors='ignore').strip()
                if raw_data.startswith('$GPGGA') and len(raw_data) > 10:
                    try:
                        msg = pynmea2.parse(raw_data)
                        no = msg.sats
                        print(f"Raw Data:{msg}")
                        print(f"No.of satellites: {no}")

                    except pynmea2.ParseError as e:
                        print(f"Error:{e}")
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Closing port.")


if __name__ == '__main__':
    read_gps('/dev/serial0')
