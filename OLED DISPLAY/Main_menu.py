from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
import time

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

main_menu = ["1.Track", "2.Settings", "3.Telemetry", "4.Align", "5. Exit"]
selected_option = 0

def draw_menu():
    with canvas(device) as draw:
        draw.rectangle((0, 0, 128, 64), outline="white", fill="black")  # Clear the screen
        draw.text((5, 3), "Main Menu", fill="white", font=proportional(CP437_FONT))
        for index, option in enumerate(main_menu):
            y_position = 7 + (index) * 12 
            rectangle_coords = (0, y_position - 2, 128, y_position + 12)
            if index == selected_option:
                draw.rectangle(rectangle_coords, outline="white", fill="white")
                draw.text((5, y_position), option, fill="black", font=proportional(CP437_FONT))
            else:
                draw.text((5, index * 12), option, fill="white", font=proportional(CP437_FONT))

Actions = {"UP", "DOWN", "SELECT", "EXIT"}
draw_menu()
time.sleep(1)  # Pause for a moment to show the initial menu

while True:
    Action = input("Enter action (UP, DOWN, SELECT, EXIT): ").strip().upper()

    if Action not in Actions:
        print("Invalid action. Please enter UP, DOWN, SELECT, or EXIT.")
        continue

    elif Action == "UP":
        if selected_option > 0:
            selected_option -= 1
        elif selected_option == 0:
            selected_option = len(main_menu) - 1

    elif Action == "DOWN":
        if selected_option < len(main_menu) - 1:
            selected_option += 1
        elif selected_option == len(main_menu) - 1:
            selected_option = 0    

    elif Action == "SELECT":
        print(f"You selected: {main_menu[selected_option]}")
        time.sleep(1)  # Pause for a moment to show the selection

    elif Action == "EXIT":
        print("Exiting the menu.")
        break  

    draw_menu()                  