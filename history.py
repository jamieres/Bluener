import datetime

class History:
    def __init__(self):
        self.devices = []

    def add_device(self, device):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.devices.append((device, timestamp))

    def get_devices(self):
        return self.devices

history = History()
