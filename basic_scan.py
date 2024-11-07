import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    print(f"Dispositivo detectado: {device.name} - {device.address}")

async def basic_scan():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(30)
    await scanner.stop()

asyncio.run(basic_scan())