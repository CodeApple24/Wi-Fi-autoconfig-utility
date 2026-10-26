import tkinter as tk
import subprocess
import ctypes
import sys
from tkinter import messagebox

ENABLE_CMD = 'wlan set autoconfig enabled=yes interface="Wi-Fi"'
DISABLE_CMD = 'wlan set autoconfig enabled=no interface="Wi-Fi"'

def run_netsh_elevated(arguments):
    try:
        result = subprocess.run(["netsh"] + arguments.split(), capture_output=True, text=True, check=True)
        messagebox.showinfo("Success", "Command executed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Command failed with exit code {e.returncode}\n{e.stderr}")
    except FileNotFoundError:
        messagebox.showerror("Error", "netsh utility not found. Ensure you are running this on windows.")

def EnableAutoconfig():
    run_netsh_elevated(ENABLE_CMD)

def DisableAutoconfig():
    run_netsh_elevated(DISABLE_CMD)

root = tk.Tk()
root.title("Autoconfig Setter")
root.geometry("600x500")


EnableButton = tk.Button(root, text="Enable Autoconfig", command=EnableAutoconfig, bg="lightgreen")
EnableButton.pack(pady = 10)
DisableButton = tk.Button(root, text="Disable Autoconfig", command=DisableAutoconfig, bg="lightcoral")
DisableButton.pack(pady=10)

root.mainloop()
