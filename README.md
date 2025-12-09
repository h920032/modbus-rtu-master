# Modbus RTU Master Tool

A modern, web-based Modbus RTU Master tool for communicating with slave devices via serial port. Built with Python (Flask) and a responsive HTML/CSS frontend.

## Features

- **Modern Web Interface**: Clean, dark-mode UI with responsive design.
- **Serial Configuration**: Easy setup for Port, Baudrate, Parity, etc.
- **Raw Command Sender**: Send arbitrary hex strings with optional automatic CRC16 calculation.
- **Register Scanner**: Scan a range of registers to discover available data points on a slave device.
- **Real-time Logging**: View TX/RX data and errors in a dedicated console log.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)

## Installation

1.  Clone or download this repository.
2.  Navigate to the project directory:
    ```bash
    cd modbus_rtu_tool
    ```
3.  Install the required dependencies:
    ```bash
    pip install pyserial flask
    ```

## Usage

1.  Start the application:
    ```bash
    python3 app.py
    ```
2.  Open your web browser and go to:
    ```
    http://127.0.0.1:5000
    ```
3.  **Connect**:
    - Select your Serial Port from the dropdown (click refresh if needed).
    - Configure Baudrate and Parity.
    - Click **Connect**.

4.  **Send Commands**:
    - In the "Raw Command" section, enter your hex string (e.g., `01 03 00 00 00 01`).
    - Keep "Auto Append CRC16" checked to handle CRC automatically.
    - Click **Send Command**.

5.  **Scan Registers**:
    - In the "Register Scanner" section, set the Slave ID, Function Code, Start Address, and Count.
    - Click **Start Scan** to probe the device.

## Project Structure

- `app.py`: Flask backend server handling serial communication.
- `modbus_core.py`: Core logic for Modbus frames and CRC calculation.
- `static/`: Contains frontend assets (`index.html`, `style.css`, `script.js`).

## Troubleshooting

- **No Ports Found**: Ensure your USB-to-Serial adapter is plugged in and drivers are installed.
- **Permission Denied**: On Linux/Mac, you might need to add your user to the `dialout` group or use `sudo` (though not recommended for web apps).
- **CRC Errors**: Check if your baudrate and parity settings match the slave device.
