import yaml

def load_config(filename='config.yaml'):
    try:
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}

def save_config(config, filename='config.yaml'):
    with open(filename, 'w') as file:
        yaml.safe_dump(config, file)

def load_mac_vendors(filename='standard_mac.txt'):
    mac_vendors = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                mac_vendors[parts[0]] = parts[1]
    return mac_vendors
