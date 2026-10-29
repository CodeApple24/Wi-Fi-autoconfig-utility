import customtkinter as ctk
import subprocess
import re
import ctypes
import sys
import threading
import time
import platform
import pystray
import os
import socket
from tkinter import messagebox
from PIL import Image

if platform.system() != "Windows": 
    print("Error: Autoconfig Setter is only compatible with Windows")
    sys.exit(1)


# Make sure code is running as admin
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() != 0:
        return True

    args = subprocess.list2cmdline(sys.argv)
    
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, args, None, 0
    )
    sys.exit(0)

app_ref = None
server_socket = None

def is_instance_running() -> bool:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 48921))
        client.sendall(b"SHOW")
        client.close()
        return True
    except (ConnectionRefusedError, socket.error):
        return False

def bind_single_instance_server() -> bool:
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 48921))
        server_socket.listen(1)

        def run_server():
            while True:
                try:
                    conn, _ = server_socket.accept()
                    data = conn.recv(1024)
                    conn.close()
                    if data == b"SHOW" and app_ref:
                        app_ref.root.after(0, app_ref.show_window)
                except Exception:
                    continue
        threading.Thread(target=run_server, daemon=True).start()
        return True
    except Exception:
        return False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

QUERY_CMD = 'wlan show autoconfig'
NO_WINDOW_FLAG = subprocess.CREATE_NO_WINDOW
IMAGES_DIR = resource_path("images")

# Dynamically fetch active wireless interface name
def get_main_interface() -> str:
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            errors="ignore",
            check=True,
            creationflags=NO_WINDOW_FLAG
        )
        match = re.search(r'Name\s*:\s*(.+)', result.stdout)

        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return "Wi-Fi"

# Dynamically fetch current status of autoconfig setting (on or off)
def get_autoconfig_status() -> bool:
    try:
        result = subprocess.run(
            ["netsh"] + QUERY_CMD.split(),
            capture_output=True,
            text=True,
            errors="ignore",
            check=True,
            creationflags=NO_WINDOW_FLAG
        )

        pattern = r'Auto configuration\s+(?:logic\s+)?is\s+(enabled|disabled)'
        match = re.search(pattern, result.stdout, re.IGNORECASE)

        if match:
            return match.group(1).lower() == "enabled"

        return "enabled" in result.stdout.lower()
    except Exception:
        print("System Error")
        return False

#Run netsh command, used for autoconfig enabling/disabling
def run_netsh_elevated(args_list):
    try:
        result = subprocess.run(["netsh"] + args_list, capture_output=True, text=True, check=True, creationflags=NO_WINDOW_FLAG)
        messagebox.showinfo("Success", "Command executed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Command failed with exit code {e.returncode}\n{e.stderr}")
        return False
    except FileNotFoundError:
        messagebox.showerror("Error", "netsh utility not found. Ensure you are running this on windows.")
        return False


# Create UI
THEME_BG = "#232334"

def apply_theme(root):
    """Apply the project theme to a window. CustomTkinter styles per widget,
    so the widgets themselves carry the rest of the colours."""
    root.configure(fg_color=THEME_BG)


class Application:
    def __init__(self, root):
        self.root = root
        root.title("Autoconfig Setter")
        root.geometry("600x450")
        root.minsize(600, 450)
        root.update_idletasks()
        root.geometry(
            f"+{(root.winfo_screenwidth() - 600) // 2}"
            f"+{(root.winfo_screenheight() - 450) // 2}"
        )
        apply_theme(root)

        try:
            root.iconbitmap(os.path.join(IMAGES_DIR, "icon.ico"))
        except Exception:
            pass

        root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.is_visible = threading.Event()
        self.is_visible.set()

        self.tray_icon = None
        self.setup_tray()

        self.MainLabel = ctk.CTkLabel(root, text="Autoconfig Setter", text_color="#A7F3D0", font=ctk.CTkFont(family="Segoe Print", size=55), width=520, height=100)
        self.MainLabel.place(
            relx = 40/600,
            rely = 1/450,
            anchor="nw"
        )

        self.separator2 = ctk.CTkFrame(root, corner_radius=0, fg_color="gray70", width=600, height=3)
        self.separator2.place(
            relx = 0,
            rely = 101/450,
            anchor = "nw"
        )

        self.EnableButton = ctk.CTkButton(root, command=self.EnableAutoconfig, text="Enable Autoconfig", text_color="#1E293B", fg_color="#10B981", hover_color="#34D399", font=ctk.CTkFont(family="Segoe UI", size=26), corner_radius=12, width=240, height=50)
        self.EnableButton.place(
            relx=40/600,
            rely=195/450,
            anchor="nw"
        )

        self.DisableButton = ctk.CTkButton(root, command=self.DisableAutoconfig, text="Disable Autoconfig", text_color="#FEE2E2", fg_color="#BE123C", hover_color="#E11D48",  font=ctk.CTkFont(family="Segoe UI", size=26), corner_radius=12, width=240, height=50)
        self.DisableButton.place(
            relx=320/600,
            rely=195/450,
            anchor="nw"
        )

        self.StatusFrame = ctk.CTkFrame(
            root,
            fg_color="transparent",
            corner_radius=0
        )

        self.StatusLabel = ctk.CTkLabel(self.StatusFrame, text="Autoconfig Status:", text_color="#94A3B8", font=ctk.CTkFont(family="Segoe UI", size=26), width=0, height=40)

        self.label5 = ctk.CTkLabel(self.StatusFrame, text="", text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", size=26), width=0, height=40)

        self.StatusLabel.grid(row=0, column=0, padx=(0, 8))
        self.label5.grid(row=0, column=1)

        self.StatusFrame.place(
            relx = 0.5,
            rely = 320/450,
            anchor="center"
        )

        self.update_status()

    def setup_tray(self):
        try:
            icon_path = os.path.join(IMAGES_DIR, "icon.png")
            image = Image.open(icon_path)
            menu = pystray.Menu(
                pystray.MenuItem("Show App", self.show_window, default=True),
                pystray.MenuItem("Exit", self.exit_app)
            )
            self.tray_icon = pystray.Icon(
                "AutoconfigSetter",
                image,
                "AutoconfigSetter",
                menu
            )
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Failed to initalize system tray icon: {e}")
            
    def hide_window(self):
        self.is_visible.clear()
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.update_status()
        self.is_visible.set()

    def exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit(0)


    # Change status label when autoconfig setting changes
    def on_autoconfig_enabled(self):
        self.label5.configure(text="Enabled", text_color="#44ab7b")

    def on_autoconfig_disabled(self):
        self.label5.configure(text="Disabled", text_color="#d75656")

    # Enable or disable autoconfig setting and trigger status label update
    def EnableAutoconfig(self):
       interface = get_main_interface()
       if run_netsh_elevated(["wlan", "set", "autoconfig", "enabled=yes", f"interface={interface}"]):
           self.on_autoconfig_enabled()

    def DisableAutoconfig(self):
        interface = get_main_interface()
        if run_netsh_elevated(["wlan", "set", "autoconfig", "enabled=no", f"interface={interface}"]):
            self.on_autoconfig_disabled()

    # Status label updater
    def update_status(self):
        if get_autoconfig_status():
            self.on_autoconfig_enabled()
        else:
            self.on_autoconfig_disabled()

    # Poll autoconfig setting every 1~ second to update status label
    def _event_listener_worker(self):
        former_status = get_autoconfig_status()
        while True:
            self.is_visible.wait()

            time.sleep(1)
            try:
                status = get_autoconfig_status()
                if status == former_status:
                    continue

                former_status = status

                if status:
                    self.root.after(0, self.on_autoconfig_enabled)
                else:
                    self.root.after(0, self.on_autoconfig_disabled)
            except Exception:
                pass

    # Trigger the listener function
    def start_watcher(self):
        watcher_thread = threading.Thread(
            target=self._event_listener_worker,
            daemon=True,
            name="WLANEventWatcher"
        )

        watcher_thread.start()
        
# initiate app
if __name__ == "__main__":
    if is_instance_running():
        sys.exit(0)

    run_as_admin()

    if not bind_single_instance_server():
        sys.exit(0)
    
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.resizable(False, False)
    app = Application(root)

    app_ref = app

    app.start_watcher()
    root.mainloop()