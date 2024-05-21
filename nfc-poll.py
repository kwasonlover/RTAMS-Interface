from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from rpi_lcd import LCD

lcd = LCD(bus=0, width=16, rows=2)

pn532 = Pn532_i2c()
pn532.SAMconfigure()

lcd.text("NFC Polling", 1)
sleep(1)
lcd.clear()
lcd.text("Tap a card", 1)
while True: 
    
    card_data = pn532.read_mifare().get_data()
    card_data_formatted = ' '.join(format(x, '02X') for x in card_data)
    nfc_uid = ' '.join(card_data_formatted.split()[7:])
    print(nfc_uid)
    lcd.text(nfc_uid, 2)