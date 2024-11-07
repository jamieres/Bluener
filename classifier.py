from utils import load_mac_vendors

mac_vendors = load_mac_vendors('standard_mac.txt')

def classify_device(device, metadata, config):
    keywords = config['keywords']
    if isinstance(device, tuple):
        name = device[0]
    else:
        name = device.name or "None"

    if name is None:
        name = "None"

    if any(keyword.lower() in name.lower() for keyword in keywords):
        return "audio"
    return "other"
