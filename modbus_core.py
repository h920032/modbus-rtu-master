import struct

def calculate_crc(data: bytes) -> int:
    """Calculates the CRC16 for Modbus RTU."""
    crc = 0xFFFF
    for char in data:
        crc ^= char
        for _ in range(8):
            if (crc & 0x0001):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def append_crc(data: bytes) -> bytes:
    """Appends the CRC16 to the data."""
    crc = calculate_crc(data)
    # Modbus expects little-endian CRC
    return data + struct.pack('<H', crc)

def validate_crc(data: bytes) -> bool:
    """Validates the CRC16 of the received data."""
    if len(data) < 2:
        return False
    received_crc = struct.unpack('<H', data[-2:])[0]
    calculated_crc = calculate_crc(data[:-2])
    return received_crc == calculated_crc

def build_read_holding_registers_frame(slave_id: int, start_address: int, quantity: int) -> bytes:
    """Builds a frame to read holding registers (Function Code 03)."""
    # Slave ID (1 byte) + Function Code (1 byte) + Start Address (2 bytes) + Quantity (2 bytes)
    frame = struct.pack('>BBHH', slave_id, 3, start_address, quantity)
    return append_crc(frame)

def build_read_input_registers_frame(slave_id: int, start_address: int, quantity: int) -> bytes:
    """Builds a frame to read input registers (Function Code 04)."""
    # Slave ID (1 byte) + Function Code (1 byte) + Start Address (2 bytes) + Quantity (2 bytes)
    frame = struct.pack('>BBHH', slave_id, 4, start_address, quantity)
    return append_crc(frame)
