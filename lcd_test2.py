from rpi_lcd import LCD

lcd = LCD(bus=0, width=16, rows=2)

lcd.text('Hello World!', 1)
lcd.text('Raspberry Pi',2)