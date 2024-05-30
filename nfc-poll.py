from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from rpi_lcd import LCD
import logging
from time import sleep

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

lcd = LCD(bus=0, width=16, rows=2)

pn532 = Pn532_i2c()
pn532.SAMconfigure()

lcd.text("NFC Polling", 1)
sleep(1)
lcd.clear()
lcd.text("Tap a card", 1)

def scroll_text(text, row=2, delay=0.5):
    # Scroll the text continuously
    while True:
        for i in range(len(text) - 13):
            lcd.text(text[i:i+16], row)
            sleep(delay)

try:
    while True:
        card_data = pn532.read_mifare().get_data()
        card_data_formatted = ' '.join(format(x, '02X') for x in card_data)
        nfc_uid = ' '.join(card_data_formatted.split()[7:])
        logging.info(nfc_uid)
        print(nfc_uid)
        scroll_text(nfc_uid, row=2, delay=0.7)

except KeyboardInterrupt:
    # Stop scrolling when Ctrl+C is pressed
    lcd.clear()
    lcd.text("Scrolling stopped", 2)
