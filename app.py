import time
import serial
import serial.tools.list_ports
from flask import Flask, request, jsonify, send_from_directory
import modbus_core
import struct

app = Flask(__name__, static_url_path='')

# Global serial port object
ser = None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/ports', methods=['GET'])
def list_ports():
    ports = serial.tools.list_ports.comports()
    return jsonify([p.device for p in ports])

@app.route('/api/connect', methods=['POST'])
def connect():
    global ser
    data = request.json
    port = data.get('port')
    baudrate = int(data.get('baudrate', 9600))
    parity_str = data.get('parity', 'None')
    
    parity_map = {
        "None": serial.PARITY_NONE,
        "Even": serial.PARITY_EVEN,
        "Odd": serial.PARITY_ODD,
        "Mark": serial.PARITY_MARK,
        "Space": serial.PARITY_SPACE
    }
    
    try:
        if ser and ser.is_open:
            ser.close()
            
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=parity_map.get(parity_str, serial.PARITY_NONE),
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        return jsonify({"status": "connected", "port": port})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    global ser
    if ser and ser.is_open:
        ser.close()
    ser = None
    return jsonify({"status": "disconnected"})

@app.route('/api/send', methods=['POST'])
def send_command():
    global ser
    if not ser or not ser.is_open:
        return jsonify({"error": "Not connected"}), 400
    
    data = request.json
    hex_str = data.get('hex', '')
    use_crc = data.get('use_crc', True)
    
    try:
        # Clean hex string
        clean_hex = hex_str.replace(" ", "").replace("0x", "")
        raw_bytes = bytes.fromhex(clean_hex)
        
        if use_crc:
            to_send = modbus_core.append_crc(raw_bytes)
        else:
            to_send = raw_bytes
            
        ser.reset_input_buffer()
        ser.write(to_send)
        
        # Wait for response
        time.sleep(0.1)
        # Simple adaptive wait
        retries = 5
        while ser.in_waiting == 0 and retries > 0:
            time.sleep(0.1)
            retries -= 1
            
        response = b''
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            
        resp_hex = response.hex(' ').upper()
        sent_hex = to_send.hex(' ').upper()
        
        crc_valid = False
        if response and len(response) >= 2:
            crc_valid = modbus_core.validate_crc(response)
            
        return jsonify({
            "tx": sent_hex,
            "rx": resp_hex,
            "crc_valid": crc_valid
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/read_register', methods=['POST'])
def read_register():
    # Helper for scanning: read a single register
    global ser
    if not ser or not ser.is_open:
        return jsonify({"error": "Not connected"}), 400
        
    data = request.json
    slave_id = int(data.get('slave_id'))
    address = int(data.get('address'))
    func_code = int(data.get('func_code', 3))
    
    try:
        if func_code == 3:
            frame = modbus_core.build_read_holding_registers_frame(slave_id, address, 1)
        else:
            frame = modbus_core.build_read_input_registers_frame(slave_id, address, 1)
            
        ser.reset_input_buffer()
        ser.write(frame)
        
        time.sleep(0.05)
        retries = 3
        while ser.in_waiting == 0 and retries > 0:
            time.sleep(0.05)
            retries -= 1
            
        response = b''
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            
        if not response:
            return jsonify({"status": "no_response"})
            
        if modbus_core.validate_crc(response):
            # Parse value (Slave(1)+Func(1)+Bytes(1)+Data(2)+CRC(2))
            if len(response) >= 7:
                val = struct.unpack('>H', response[3:5])[0]
                return jsonify({"status": "ok", "value": val, "hex": f"0x{val:04X}"})
            else:
                return jsonify({"status": "error", "message": "Short response"})
        else:
            return jsonify({"status": "error", "message": "CRC Fail"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
