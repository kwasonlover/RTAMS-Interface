EN_BIT = 0x04 # 0000 0100 - Enable
RW_BIT = 0x02 # 0000 0010 - Read/Write
RS_BIT = 0x01 # 0000 0001 - Register selector

#  commands
LCD_CLEARDISPLAY    = 0x01 # 0000 0001
LCD_RETURNHOME      = 0x02 # 0000 0010
LCD_ENTRYMODESET    = 0x04 # 0000 0100
LCD_DISPLAYCONTROL  = 0x08 # 0000 1000
LCD_CURSORSHIFT     = 0x10 # 0001 0000
LCD_FUNCTIONSET     = 0x20 # 0010 0000
LCD_SET_CGRAM_ADDR  = 0x40 # 0100 0000 - Character Generator RAM
LCD_SET_DDRAM_ADDR  = 0x80 # 1000 0000 - Display Data RAM

# flags for display entry mode
LCD_ENTRYRIGHT          = 0x00 # 0000 0000
LCD_ENTRYLEFT           = 0x02 # 0000 0010
LCD_ENTRYSHIFTINCREMENT = 0x01 # 0000 0001
LCD_ENTRYSHIFTDECREMENT = 0x00 # 0000 0000

# flags for display on/off control
LCD_DISPLAYON       = 0x04 # 0000 0100
LCD_DISPLAYOFF      = 0x00 # 0000 0000
LCD_CURSORON        = 0x02 # 0000 0010
LCD_CURSOROFF       = 0x00 # 0000 0000
LCD_BLINKON         = 0x01 # 0000 0001
LCD_BLINKOFF        = 0x00 # 0000 0000

# flags for display/cursor shift
LCD_DISPLAYMOVE     = 0x08 # 0000 1000
LCD_CURSORMOVE      = 0x00 # 0000 0000
LCD_MOVERIGHT       = 0x04 # 0000 0100
LCD_MOVELEFT        = 0x00 # 0000 0000

# flags for function set
LCD_8BITMODE        = 0x10 # 0001 0000
LCD_4BITMODE        = 0x00 # 0000 0000
LCD_2LINE           = 0x08 # 0000 1000
LCD_1LINE           = 0x00 # 0000 0000
LCD_5x10DOTS        = 0x04 # 0000 0100
LCD_5x8DOTS         = 0x00 # 0000 0000

# flags for backlight control
LCD_BACKLIGHT       = 0x08 # 0000 1000
LCD_NOBACKLIGHT     = 0x00 # 0000 0000