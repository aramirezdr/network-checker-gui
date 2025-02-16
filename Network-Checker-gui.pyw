import os
import platform
import subprocess
import socket
import psutil
import customtkinter as ctk
from tkinter import messagebox

def get_default_gateway():
    if platform.system().lower() == 'windows':
        command = 'ipconfig'
    else:
        command = 'ip route'

    try:
        output = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError:
        return None

    if platform.system().lower() == 'windows':
        for line in output.splitlines():
            if 'Default Gateway' in line:
                parts = line.split()
                if len(parts) >= 4:
                    return parts[-1]
    else:
        for line in output.splitlines():
            if line.startswith('default via'):
                parts = line.split()
                if len(parts) >= 3:
                    return parts[2]

    return None

def get_ip_and_interface():
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    return addr.address, interface
    except Exception as e:
        return 'N/A', 'N/A'
    return 'N/A', 'N/A'

def get_logon_server():
    if platform.system().lower() == 'windows':
        try:
            output = subprocess.check_output('echo %logonserver%', shell=True, text=True)
            return output.strip()
        except subprocess.CalledProcessError:
            return 'N/A'
    else:
        return 'N/A'

def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    try:
        output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError:
        return 'Ping failed'

def dns_query(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.error:
        return 'DNS resolution failed'

def check_connection():
    gateway = get_default_gateway()
    ip_address, interface = get_ip_and_interface()
    logon_server = get_logon_server()

    ip_result.set(f"IP: {ip_address}")
    interface_result.set(f"Interface: {interface}")
    logon_server_result.set(f"Logon Server: {logon_server}")
    
    if gateway:
        ping_result = ping(gateway)
        gw_result.set(f"Gateway ({gateway}):\n{ping_result}")
    else:
        gw_result.set("Gateway not found")
    
    dns_ip = dns_query("google.com")
    dns_result.set(f"DNS google.com: {dns_ip}")

def main():
    global gw_result, ip_result, interface_result, dns_result, logon_server_result
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("OBS Network Connection Checker")
    root.geometry("500x400")
    
    frame = ctk.CTkFrame(root)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    ctk.CTkLabel(frame, text="Network Connection Checker", font=("Arial", 16)).pack(pady=10)
    
    ip_result = ctk.StringVar()
    ctk.CTkLabel(frame, textvariable=ip_result).pack()
    
    interface_result = ctk.StringVar()
    ctk.CTkLabel(frame, textvariable=interface_result).pack()
    
    logon_server_result = ctk.StringVar()
    ctk.CTkLabel(frame, textvariable=logon_server_result).pack()
    
    gw_result = ctk.StringVar()
    ctk.CTkLabel(frame, textvariable=gw_result, wraplength=450, justify="left").pack(pady=5)
    
    dns_result = ctk.StringVar()
    ctk.CTkLabel(frame, textvariable=dns_result).pack()
    
    ctk.CTkButton(frame, text="Check Connection", command=check_connection).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
