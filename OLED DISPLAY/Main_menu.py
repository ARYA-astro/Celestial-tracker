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
    len_options = len(main_menu[sel_opt])
    if len_options <= 3:
        start_idx = 0
        end_idx = len_options
    else:
        if sel_idx == 0:
            start_idx = 0
        elif sel_idx == len_options - 1:
            start_idx = len_options - 3
        else:
            start_idx = sel_idx - 1

        end_idx = start_idx + 3            
                
    with canvas(device) as draw:
        draw.rectangle((0, 0, 127, 63), outline="white", fill="black")  # Clear the screen
        draw.text((37, 3), title, fill="white", font=FONT)
        for index, idx in enumerate(range(start_idx, end_idx)):
            option = main_menu[sel_opt][idx]
            y_position = 14 + index * 12
            rectangle_coords = (1, y_position, 127, y_position + 11)
            if idx == sel_idx:
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
            sel_idx = len(main_menu[sel_opt]) - 1

    elif Action == "DOWN":
        if sel_idx < len(main_menu[sel_opt]) - 1:
            sel_idx += 1
        elif sel_idx == len(main_menu[sel_opt]) - 1:
            sel_idx = 0

    elif Action == "SELECT":
    
        selected_option = main_menu[sel_opt][sel_idx] 
        if "Exit" in selected_option:
            print("Exiting the menu.")
            break

        elif selected_option not in main_menu:
            if "Back" in selected_option:
                sel_opt = "Menu"
                sel_idx = 0
            else:
                print(f"Selected option: {selected_option}")
                time.sleep(1)  # Pause to show the selected option

        elif selected_option in main_menu:
            sel_opt = selected_option
            sel_idx = 0        


    elif Action == "EXIT":
        print("Exiting the menu.")
        break
         

    draw_menu(sel_opt)                  
