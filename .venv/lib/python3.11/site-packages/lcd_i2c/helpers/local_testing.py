class SMBus():
    def __init__(self, val: int) -> None:
        pass

    def write_byte_data(self, address: int, b: int, data: int):
        print(f"Write to address: {address} - b: {b} - data: {data}")

    def write(self, value: int) -> None:
        print(value)