from gpiozero import Button
import gpiozero as GPIO

button = Button(17, pull_up=False)

button.wait_for_press()
print("Button was pressed")