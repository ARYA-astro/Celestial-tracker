from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
import time

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

with canvas(device) as draw:
    draw.text((10, 10), "Hello World!", font=proportional(CP437_FONT), fill="white") #Draw text with CP437_FONT
    draw.text((10,30), "Hello World!", font=proportional(LCD_FONT), fill="white") #Draw text with LCD_FONT
    draw.text((10,50), "Hello World!", fill="white") # Draw text with default font 
    draw.rectangle(device.bounding_box, outline="white") #Draw a rectangle around the display
                                                                           #If I want to not use the actual coordinates of the display, I can use device.bounding_box to get the coordinates of the display
time.sleep(2) #Wait for 2 seconds
device.clear() #Clear the display
time.sleep(2) #Wait for 2 seconds
x = 0
y = 0
while x < 128 and y < 64:
        with canvas(device) as draw:
           draw.text((x, y), ".", fill ="white") #Draw a dot at the current coordinates
        time.sleep(0.1) #Wait for 0.1 seconds
        x += 1 #Increment the x coordinate by 1
        y += 1 #Increment the y coordinate by 1

device.clear() #Clear the display 