import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from scanner import discover_bluetooth_devices, get_device_info, connect_to_device, disconnect_from_device
from classifier import classify_device
from blocker import block_bluetooth
from utils import load_config, save_config
from history import history

config = load_config('config.yaml')

scan_running = False
scan_paused = False
scan_thread = None
all_devices = []
connected_device = None

def display_device(device):
    if isinstance(device, tuple):
        name, mac = device
    else:
        name = getattr(device, 'name', 'None') or 'None'
        mac = getattr(device, 'address', 'Unknown') or 'Unknown'
    
    category = classify_device((name, mac), None, config)
    history.add_device((name, mac))
    
    if not any(mac in item for item in listbox.get(0, tk.END)):
        all_devices.append(f"{name} - {mac} ({category})")
        listbox.insert(tk.END, f"{name} - {mac} ({category})")
        if category == "audio":
            block_bluetooth(mac)
            messagebox.showinfo("Bloqueo", "Adaptador Bluetooth deshabilitado.")

def filter_devices():
    search_term = search_var.get().lower()
    filter_type = filter_var.get()
    filtered_devices = []

    for device in all_devices:
        name, mac, category = device.split(' - ')[0], device.split(' - ')[1].split(' ')[0], device.split('(')[-1].strip(')')
        if (filter_type == "Name" and search_term in name.lower()) or \
           (filter_type == "MAC" and search_term in mac.lower()) or \
           (filter_type == "Type" and search_term in category.lower()):
            filtered_devices.append(device)
    
    listbox.delete(0, tk.END)
    for device in filtered_devices:
        listbox.insert(tk.END, device)

def show_history():
    history_window = tk.Toplevel(app)
    history_window.title("Historial de Dispositivos")
    history_listbox = tk.Listbox(history_window, width=80, height=20)
    history_listbox.pack(pady=10)
    
    for device, timestamp in history.get_devices():
        name, mac = device
        history_listbox.insert(tk.END, f"{timestamp} - {name} - {mac}")

def update_progress(progress_var, progress_bar, status_label, progress):
    progress_var.set(progress)
    progress_bar.update()
    status_label.config(text=f"Escaneando... {int(progress)}%")

def update_info_progress(progress_var, progress_bar, status_label, progress):
    progress_var.set(progress)
    progress_bar.update()
    status_label.config(text=f"Obteniendo información... {int(progress)}%")

async def scan_devices(progress_var, progress_bar, status_label):
    global scan_running, scan_paused
    scan_time = config.get('scan_time', 10)
    min_rssi = config.get('min_rssi', -100)
    
    for i in range(scan_time):
        if not scan_running:
            break
        while scan_paused:
            await asyncio.sleep(1)
        await asyncio.sleep(1)
        results = await discover_bluetooth_devices(1)

        app.after(0, update_progress, progress_var, progress_bar, status_label, (i + 1) * 100 / scan_time)

        for device, advertisement_data in results:
            if getattr(advertisement_data, 'rssi', -100) >= min_rssi:
                app.after(0, display_device, device)

    app.after(0, status_label.config, {"text": "Escaneo completado"})
    app.after(0, progress_var.set, 100)
    app.after(0, progress_bar.update)

    info_progress_var = tk.DoubleVar()
    info_progress_bar = ttk.Progressbar(frame, variable=info_progress_var, maximum=100)
    info_progress_bar.pack(pady=10, fill=tk.X)
    app.after(0, status_label.config, {"text": "Obteniendo información de dispositivos"})
    for i, device in enumerate(results):
        if isinstance(device, tuple):
            continue
        try:
            info = await get_device_info(device)
            print(info)
        except Exception as e:
            print(f"Error obteniendo información de {device.address}: {e}")
        app.after(0, update_info_progress, info_progress_var, info_progress_bar, status_label, (i + 1) * 100 / len(results))

    app.after(0, status_label.config, {"text": "Proceso completado"})
    app.after(0, info_progress_var.set, 100)
    app.after(0, info_progress_bar.update)

def start_scan_thread():
    global scan_running, scan_paused, scan_thread, all_devices
    if scan_thread and scan_thread.is_alive():
        return
    scan_running = True
    scan_paused = False
    progress_var.set(0)
    status_label.config(text="Iniciando escaneo...")
    all_devices = []
    listbox.delete(0, tk.END)
    scan_thread = threading.Thread(target=lambda: asyncio.run(scan_devices(progress_var, progress_bar, status_label)))
    scan_thread.start()

def stop_scan():
    global scan_running
    scan_running = False
    status_label.config(text="Escaneo detenido")

def pause_scan():
    global scan_paused
    scan_paused = not scan_paused
    status_label.config(text="Escaneo pausado" if scan_paused else "Escaneando...")

def copy_to_clipboard():
    app.clipboard_clear()
    results = listbox.get(0, tk.END)
    results_str = "\n".join(results)
    app.clipboard_append(results_str)
    messagebox.showinfo("Copiado", "Resultados copiados al portapapeles")

def block_selected_device():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un dispositivo de la lista para bloquear.")
        return
    selected_device = listbox.get(selected[0])
    mac = selected_device.split(' - ')[1].split(' ')[0]
    block_bluetooth(mac)
    messagebox.showinfo("Bloqueo", f"Dispositivo {mac} bloqueado.")

def connect_selected_device():
    global connected_device
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un dispositivo de la lista para conectarse.")
        return
    selected_device = listbox.get(selected[0])
    mac = selected_device.split(' - ')[1].split(' ')[0]

    async def connect():
        result = await connect_to_device(mac)
        if "error" in result:
            messagebox.showerror("Error", result["error"])
        else:
            connected_device = result["client"]
            messagebox.showinfo("Conexión", f"Conectado a {mac}")

    asyncio.run(connect())

def disconnect_device():
    global connected_device
    if not connected_device:
        messagebox.showwarning("Advertencia", "No hay dispositivos conectados para desconectar.")
        return

    async def disconnect():
        result = await disconnect_from_device(connected_device)
        if "error" in result:
            messagebox.showerror("Error", result["error"])
        else:
            connected_device = None
            messagebox.showinfo("Desconexión", "Dispositivo desconectado")

    asyncio.run(disconnect())

def show_advanced_config():
    config_window = tk.Toplevel(app)
    config_window.title("Configuración Avanzada")
    config_window.geometry("400x300")

    def save_config_values():
        config['scan_time'] = int(scan_time_var.get())
        config['min_rssi'] = int(min_rssi_var.get())
        save_config(config)
        messagebox.showinfo("Configuración Guardada", "La configuración ha sido guardada.")
        config_window.destroy()

    scan_time_var = tk.StringVar(value=config.get('scan_time', 10))
    min_rssi_var = tk.StringVar(value=config.get('min_rssi', -100))

    ttk.Label(config_window, text="Tiempo de Escaneo (s):", font=("Segoe UI", 12)).pack(pady=10)
    ttk.Entry(config_window, textvariable=scan_time_var, font=("Segoe UI", 12)).pack(pady=10)

    ttk.Label(config_window, text="Intensidad de Señal Mínima (dBm):", font=("Segoe UI", 12)).pack(pady=10)
    ttk.Entry(config_window, textvariable=min_rssi_var, font=("Segoe UI", 12)).pack(pady=10)

    ttk.Button(config_window, text="Guardar Configuración", command=save_config_values, style="Accent.TButton").pack(pady=20)

app = tk.Tk()
app.title("Bluener")
app.geometry("800x600")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 12))
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TListbox", font=("Segoe UI", 10))
style.configure("TProgressbar", thickness=30)
style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"), background="#0078D7", foreground="white")

frame = ttk.Frame(app, padding="20 20 20 20")
frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(frame, text="Bluener", font=("Segoe UI", 24, "bold"))
title_label.pack(pady=10)

description_label = ttk.Label(frame, text="Detecta, identifica y bloquea dispositivos Bluetooth.", font=("Segoe UI", 14))
description_label.pack(pady=5)

separator = ttk.Separator(frame, orient='horizontal')
separator.pack(fill='x', pady=10)

search_frame = ttk.Frame(frame)
search_frame.pack(pady=10)

search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 12))
search_entry.grid(row=0, column=0, padx=5, pady=5)

filter_var = tk.StringVar(value="Name")
filter_menu = ttk.OptionMenu(search_frame, filter_var, "Name", "Name", "MAC", "Type")
filter_menu.grid(row=0, column=1, padx=5, pady=5)

search_button = ttk.Button(search_frame, text="Search", command=filter_devices)
search_button.grid(row=0, column=2, padx=5, pady=5)

search_frame.grid_columnconfigure(0, weight=1)
search_frame.grid_columnconfigure(1, weight=1)
search_frame.grid_columnconfigure(2, weight=1)

button_frame_1 = ttk.Frame(frame)
button_frame_1.pack(pady=10)

start_button = ttk.Button(button_frame_1, text="Start Scan", command=start_scan_thread)
start_button.grid(row=0, column=0, padx=5, pady=5)

pause_button = ttk.Button(button_frame_1, text="Pause/Resume Scan", command=pause_scan)
pause_button.grid(row=0, column=1, padx=5, pady=5)

stop_button = ttk.Button(button_frame_1, text="Stop Scan", command=stop_scan)
stop_button.grid(row=0, column=2, padx=5, pady=5)

copy_button = ttk.Button(button_frame_1, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.grid(row=0, column=3, padx=5, pady=5)

block_button = ttk.Button(button_frame_1, text="Block Selected Device", command=block_selected_device)
block_button.grid(row=0, column=4, padx=5, pady=5)

button_frame_1.grid_columnconfigure(0, weight=1)
button_frame_1.grid_columnconfigure(1, weight=1)
button_frame_1.grid_columnconfigure(2, weight=1)
button_frame_1.grid_columnconfigure(3, weight=1)
button_frame_1.grid_columnconfigure(4, weight=1)

button_frame_2 = ttk.Frame(frame)
button_frame_2.pack(pady=10)

connect_button = ttk.Button(button_frame_2, text="Connect to Device", command=connect_selected_device)
connect_button.grid(row=0, column=0, padx=5, pady=5)

disconnect_button = ttk.Button(button_frame_2, text="Disconnect Device", command=disconnect_device)
disconnect_button.grid(row=0, column=1, padx=5, pady=5)

history_button = ttk.Button(button_frame_2, text="View History", command=show_history)
history_button.grid(row=0, column=2, padx=5, pady=5)

config_button = ttk.Button(button_frame_2, text="Advanced Config", command=show_advanced_config, style="Accent.TButton")
config_button.grid(row=0, column=3, padx=5, pady=5)

button_frame_2.grid_columnconfigure(0, weight=1)
button_frame_2.grid_columnconfigure(1, weight=1)
button_frame_2.grid_columnconfigure(2, weight=1)
button_frame_2.grid_columnconfigure(3, weight=1)

listbox_label = ttk.Label(frame, text="Dispositivos encontrados:", font=("Segoe UI", 14))
listbox_label.pack(pady=5)

listbox = tk.Listbox(frame, width=80, height=15, font=("Segoe UI", 10))
listbox.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X)

status_label = ttk.Label(frame, text="", font=("Segoe UI", 14))
status_label.pack(pady=5)

app.mainloop()
