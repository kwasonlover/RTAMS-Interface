from time import sleep

def delay(seconds: float):
    sleep(seconds)

def delay_ms(miliseconds: float):
    sleep(miliseconds/1000)

def delay_us(microseconds: float):
    sleep(microseconds/1_000_000)