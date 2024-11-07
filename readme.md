The code provided consists of two Python scripts: `eth8020.py` and `utility.py`. Below is a detailed description that can be used for a GitHub repository README file or project documentation.

---

# eth8020 class and utility module

## Class overview

The `eth8020` class is designed to manage Ethernet communication using a TCP socket. It allows you to send and receive messages, controlling relays, acquire analog signals and logging events. The included `utility.py` module provides additional functionality such as logging, timing and serial port management.

## Features include

- **Socket communication**: Establishes a TCP connection to a specified IP address and port.
- **Relay control**: Supports switching relays on and off, with methods to manage multiple relays.
- **Thread Security**: Uses thread locking to ensure secure access to shared resources during communication.
- **Logging**: Integrates logging capabilities for debugging and error reporting.
- **Utility functions**: Includes utilities for time tracking, exception logging, and serial communication.

## To install

To use this code, make sure you have Python and the necessary libraries installed. You can install the required libraries using pip:

```bash
pip install rich pyserial
```

## Usage

### eth8020 quick test example from CLI

To quickly test a device from the command line (CLI) and turn on the first relay prompt:

```bash
python eth8020.py --ip <ip eth8020 device> --ron 0
```

and then immediately disable the relay by typing:

```bash
python eth8020.py --ip <ip eth8020 device> --roff 0
```

to see all possible arguments:

```bash
python eth8020.py -h
```

and obtain this output:
```bash
usage: eth8020.py [-h] [-i IP] [-p PORT] [--ron RON] [--roff ROFF]

eth8020 class ver.0.1 (07/11/2024)

options:
  -h, --help            show this help message and exit
  -i IP, --ip IP        Indirizzo ip modulo eth
  -p PORT, --port PORT  Porta modulo eth
  --ron RON             Numero relé da accendere
  --roff ROFF           Numero relé da spegnere
```



### eth8020 Class

To create an instance of the eth8020 class and connect to a device, do the following:

```python
from eth8020 import eth8020

# Initialize the eth8020 instance
device = eth8020(ip="192.168.1.100", port=17494)

# Connect to the device
if device.connect():
    print("Connected successfully.")
else:
    print("Connection failed.")

# Turn on relay at position 1
if device.releOn(1):
    print("Relay 1 turned ON.")

# Turn off relay at position 1
if device.releOff(1):
    print("Relay 1 turned OFF.")

# Close the connection
device.close()
```

### Utility Module

The `utility.py` module provides several utility functions, such as:

- **Logging exceptions**: Use `logException()` to log errors with traceback information.
- **Timing**: The `timer` class helps track elapsed time for operations.
- **Serial port management**: The `port` class manages serial connections, allowing for easy setup and teardown.

## Logging Configuration

The logging system uses the `rich` library for advanced output formatting. You can configure the log level according to your needs (e.g., DEBUG, INFO, WARNING).

## Versioning

- **Version**: 0.1
- **Date**: 07/11/2024

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Adjustments may be made based on specific project requirements or additional features implemented in future releases.
The board datasheet is at the link: https://www.robot-electronics.co.uk/files/eth8020.pdf
