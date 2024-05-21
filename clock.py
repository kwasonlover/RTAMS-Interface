import time

from datetime import datetime
from rpi_lcd import LCD

lcd = LCD(bus=0, width=16, rows=2)

def get_current_time():
    return datetime.now().strftime("%I:%M %p")


while True:
    try:
        lcd.clear()
        current_time = get_current_time()
        lcd.text(current_time, 1)
        time.sleep(1)
    except KeyboardInterrupt:
        lcd.clear()
        exit