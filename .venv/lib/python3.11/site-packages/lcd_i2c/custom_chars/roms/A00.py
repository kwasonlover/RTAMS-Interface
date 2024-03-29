# See page 17 of the specsheet:
# https://www.sparkfun.com/datasheets/LCD/HD44780.pdf

from lcd_i2c.custom_chars.main import ROM
from .. import CustomChar
from ..others import a_accent, e_accent, i_accent, o_accent, u_accent, heart, smile, half_moon

ROM_A00 = ROM(
    default_custom_chars=[
        a_accent,
        e_accent,
        i_accent,
        o_accent,
        u_accent,
        heart,
        smile,
        half_moon,
    ],
    available_chars=[
        '                ',  # 00. Custom chars loaded to rom, displayed twice in a row
        '                ',  # 01. empty
        ' !"#$%&\'()*+,-./', # 02. 
        '0123456789:;<>=?',  # 03. 
        '@ABCDEFGHIJKLMNO',  # 04. 
        'PQRSTUVWXYZ[¥]^_',  # 05. 
        '`abcdefghijklmno',  # 06. 
        'pqrstuvwxyz{|}→←',  # 07. 
        '                ',  # 08. empty
        '                ',  # 09. empty
        '????????????????',  # 10. non latin characters
        '????????????????',  # 11. non latin characters
        '????????????????',  # 12. non latin characters
        '????????????????',  # 13. non latin characters
        'αäβεμσρ?√?𝑖?₵?ñö',  # 14. 
        'pqθ?ΩüΣπx̄????÷ █',  # 15. 
    ],
    replaceable_chars = '¥→←αäβεμσρ√𝑖₵ñöθΩüΣπx̄÷█'
)

