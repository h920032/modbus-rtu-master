import modbus_core
import struct

def test_crc():
    # Test case: 01 03 00 00 00 01 -> CRC should be 84 0A (Low High) -> 0A84 in hex?
    # Let's check a known standard.
    # 01 03 00 00 00 01
    # CRC is 0x0A84 (Little Endian: 84 0A)
    
    data = bytes.fromhex("01 03 00 00 00 01")
    crc = modbus_core.calculate_crc(data)
    print(f"Data: {data.hex()} -> CRC: {crc:04X}")
    
    expected_crc = 0x0A84
    if crc == expected_crc:
        print("CRC Test 1 PASS")
    else:
        print(f"CRC Test 1 FAIL. Expected {expected_crc:04X}, got {crc:04X}")

    # Test append
    frame = modbus_core.append_crc(data)
    print(f"Appended Frame: {frame.hex()}")
    if frame.hex().upper() == "010300000001840A":
        print("Append CRC Test PASS")
    else:
        print("Append CRC Test FAIL")

    # Test validate
    if modbus_core.validate_crc(frame):
        print("Validate CRC Test PASS")
    else:
        print("Validate CRC Test FAIL")

if __name__ == "__main__":
    test_crc()
