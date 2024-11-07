import subprocess

def block_bluetooth():
    subprocess.run(["netsh", "interface", "set", "interface", "Bluetooth Network Connection", "admin=disable"])
