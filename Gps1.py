import pynmea2
msg = pynmea2.parse('$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47')
print(f"latitude: {msg.latitude},\nlongitude: {msg.longitude},\nDate and Time: {msg.timestamp},\nNumber of Satellites: {msg.num_sats}")