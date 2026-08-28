import gpiozero as gpio
import time

x_axis = gpio.DigitalInputDevice(17, pull_up=False)
y_axis = gpio.DigitalInputDevice(27, pull_up=False)
select_button = gpio.DigitalInputDevice(22, pull_up=True)


while True:
    if x_axis.value == 1:
        print("Joystick:HIGH")
    elif x_axis.value == 0:
        print("Joystick:LOW")
    elif y_axis.value == 1:
        print("Joystick:HIGH")    
    elif y_axis.value == 0:
        print("Joystick:LOW")
    elif select_button.value == 1:
        print("Button:HIGH")
    elif select_button.value == 0:
        print("Button:LOW")

        time.sleep(0.1)
            

