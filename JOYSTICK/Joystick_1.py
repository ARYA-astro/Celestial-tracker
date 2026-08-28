import gpiozero as gpio
import time

x_axis = gpio.DigitalInputDevice(17, pull_up=False)
y_axis = gpio.DigitalInputDevice(27, pull_up=False)
select_button = gpio.DigitalInputDevice(22, pull_up=True)


while True:
    if x_axis.value == 1:
        x_val = "RIGHT"
    elif x_axis.value == 0:
        x_val = "LEFT"
    else:
        x_val = "CENTRE"

    if y_axis.value == 1:
        y_val = "UP"
    elif y_axis.value == 0:
        y_val = "DOWN"
    else:
        y_val = "CENTRE"
    
    btn_val = "YES" if select_button.value == 1 else "NO"

    if x_val == "CENTRE" and y_val == "CENTRE":
        ovr_val = "CENTRE"
    else:
        ovr_val = f"{y_val}-{x_val}".strip("CENTRE")
    print(f"Direction: {ovr_val:<12} | Button: {btn_val}")    
    
        time.sleep(0.1)
            

