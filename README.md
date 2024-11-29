# Bluener

**Bluener** is a program designed to detect, identify and block Bluetooth devices. This tool is ideal for managing device connectivity in environments where precise control over Bluetooth connections is required, such as in offices, educational centers and security environments.

## Objectives

- Detect nearby Bluetooth devices.
- Identify detected devices by name and MAC address.
- Classify devices by type (audio, other).
- Block audio devices automatically if found.
- Provide options for manual connection and disconnection of devices.
- Allow advanced configuration of scanning parameters.

## Features

- Intuitive and friendly user interface.
- Search and filter options for detected devices.
- History of detected devices with timestamps.
- Advanced settings to adjust scan time and minimum signal strength.
- Copy results to clipboard functionality.
- Ability to block audio devices automatically.
- Manual connection and disconnection options for selected devices.

## Options

- **Start Scan**: Begins the scanning process for Bluetooth devices.
- **Pause/Resume Scan**: Pauses or resumes the ongoing scan.
- **Stop Scan**: Stops the scanning of devices.
- **Copy to Clipboard**: Copies the scan results to the clipboard.
- **Lock Selected Device**: Locks the selected device in the list.
- **Connect to Device**: Manually connects to the selected device.
- **Disconnect Device**: Disconnects the connected device manually.
- **View History**: Displays the history of detected devices.
- **Advanced Settings**: Allows you to configure advanced scan settings.

## Required Dependencies

- Python 3.8 or higher

- Python Libraries:
- `tkinter`: For the graphical user interface.
- `asyncio`: For handling asynchronous tasks.
- `bleak`: For interaction with Bluetooth devices.
- `pyserial`: For serial device detection.
- `yaml`: For handling YAML configuration files.

## Installation Instructions

1. Clone or download the project repository.
2. Install the necessary dependencies with pip:

pip install bleak pyserial pyyaml

## Run the main gui.py file:

python gui.py

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

NOTE: It is a working version but it is still in progress. Any question just write to me (jamieres-at-gmail-dot-com)
