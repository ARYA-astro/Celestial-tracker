from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
import time

FONT = ImageFont.load_default()
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

main_menu = {
    "Menu": ["1.Track", "2.Settings", "3.Telemetry", "4.Align", "5. Exit"],
    "1.Track": ["1.Start", "2.Stop", "3.Back"],
    "2.Settings": ["1.Display", "2.Sound", "3.Back"],
    "3.Telemetry": ["1.View Data", "2.Export Data", "3.Back"],
    "4.Align": ["1.Calibrate", "2.Back"],
    "5. Exit": ["1.Confirm", "2.Back"]
    
}

sel_idx = 0
sel_opt = "Menu"

def draw_menu(title):
    with canvas(device) as draw:
        draw.rectangle((0, 0, 128, 64), outline="white", fill="black")  # Clear the screen
        draw.text((60, 3), title, fill="white", font=FONT)
        for index, option in enumerate(main_menu[sel_opt]):
            y_position = 15 + (index) * 12 
            rectangle_coords = (1, y_position - 1, 127, y_position + 11)
            if index == sel_idx:
                draw.rectangle(rectangle_coords, outline="black", fill="white")
                draw.text((5, y_position), option, fill="black", font=FONT)
            else:
                draw.text((5, y_position), option, fill="white", font=FONT)

Actions = {"UP", "DOWN", "SELECT", "EXIT"}
draw_menu(sel_opt)
time.sleep(1)  # Pause for a moment to show the initial menu

while True:
    Action = input("Enter action (UP, DOWN, SELECT, EXIT): ").strip().upper()

    if Action not in Actions:
        print("Invalid action. Please enter UP, DOWN, SELECT, or EXIT.")
        continue

    elif Action == "UP":
        if sel_idx > 0:
            sel_idx -= 1
        elif sel_idx == 0:
            sel_idx = len(sel_opt) - 1

    elif Action == "DOWN":
        if sel_idx < len(sel_opt) - 1:
            sel_idx += 1
        elif sel_idx == len(sel_opt) - 1:
            sel_idx = 0

    elif Action == "SELECT":
    
        if sel_opt in main_menu:
            if sel_opt == "5. Exit":
                print("Exiting the menu.")
                break

            else:
                sel_opt = main_menu[sel_opt][sel_idx]
                sel_idx = 0

        elif sel_opt not in main_menu:
            if "Back" in sel_opt:
                sel_opt = main_menu["Menu"]
                sel_idx = 0
            else:
                print(f"You selected: {sel_opt}")
                time.sleep(1)  # Pause to show the selection
                sel_opt = main_menu["Menu"]
                sel_idx = 0       

    elif Action == "EXIT":
        print("Exiting the menu.")
        break  

    draw_menu(sel_opt)                  
