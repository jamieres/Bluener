import asyncio
from bleak import BleakScanner, BleakClient
import serial.tools.list_ports
from classifier import classify_device
from utils import load_config

config = load_config('config.yaml')
discovered_devices = []

def detection_callback(device, advertisement_data):
    discovered_devices.append((device, advertisement_data))

async def discover_bluetooth_devices(scan_time=10):
    global discovered_devices
    discovered_devices = []
    scanner = BleakScanner(detection_callback, filters={"DuplicateData": False})
    await scanner.start()
    await asyncio.sleep(scan_time)
    await scanner.stop()

    ports = serial.tools.list_ports.comports()
    for port in ports:
        discovered_devices.append((port.description, port.device))

    return discovered_devices

async def get_device_info(device):
    try:
        async with BleakClient(device) as client:
            info = {
                "name": device.name,
                "address": device.address,
                "rssi": device.rssi,
            }
            services = await client.get_services()
            for service in services:
                info[service.uuid] = []
                for char in service.characteristics:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        info[service.uuid].append({char.uuid: value})
                    except Exception as e:
                        info[service.uuid].append({char.uuid: str(e)})
            return info
    except Exception as e:
        return {"error": str(e)}

async def connect_to_device(mac):
    device = next((d for d, _ in discovered_devices if getattr(d, 'address', None) == mac), None)
    if not device:
        return {"error": "Dispositivo no encontrado"}

    try:
        client = BleakClient(device)
        await client.connect()
        return {"client": client, "status": "connected"}
    except Exception as e:
        return {"error": str(e)}

async def disconnect_from_device(client):
    try:
        await client.disconnect()
        return {"status": "disconnected"}
    except Exception as e:
        return {"error": str(e)}
