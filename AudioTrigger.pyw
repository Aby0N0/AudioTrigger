import os
import sys
import ctypes
import subprocess
import json
import winreg
import xml.etree.ElementTree as ET
import customtkinter as ctk
from tkinter import messagebox

# 修复：使用正确的 sys.executable 锁定真实物理路径
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(script_dir)

SVV_PATH = os.path.join(script_dir, "SoundVolumeView.exe")
CONFIG_FILE = os.path.join(script_dir, "AudioTrigger_config.json")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1)
    sys.exit()

def ensure_audit_policy():
    cmds = [
        'auditpol /set /subcategory:"{0CCE922B-69AE-11D9-BED3-505054503030}" /success:enable',
        'auditpol /set /subcategory:"Process Creation" /success:enable',
        'auditpol /set /subcategory:"进程创建" /success:enable',
        'auditpol /set /subcategory:"{0CCE922C-69AE-11D9-BED3-505054503030}" /success:enable',
        'auditpol /set /subcategory:"Process Termination" /success:enable',
        'auditpol /set /subcategory:"进程终止" /success:enable'
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"headset": "", "speaker": "", "library": {}, "rules": {}}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_audio_devices():
    devices_dict = {}
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                guid = winreg.EnumKey(key, i)
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, fr"{key_path}\{guid}") as sub_key:
                        state, _ = winreg.QueryValueEx(sub_key, "DeviceState")
                        if state == 1:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, fr"{key_path}\{guid}\Properties") as prop_key:
                                name, _ = winreg.QueryValueEx(prop_key, "{b3f8fa53-0004-438e-9003-51a46e139bfc},6")
                                device_id = f"{{0.0.0.00000000}}.{guid}"
                                devices_dict[name] = device_id
                except: continue
    except: pass
    return devices_dict if devices_dict else {"未检测到设备": ""}

def get_true_case_path(path):
    try:
        if not os.path.exists(path): return path
        parts = os.path.normpath(path).split(os.sep)
        res = parts[0].upper() + os.sep
        for part in parts[1:]:
            matched = False
            for name in os.listdir(res):
                if name.lower() == part.lower():
                    res = os.path.join(res, name)
                    matched = True
                    break
            if not matched: return path
        return res
    except: return path

def generate_xml(full_path, device_id, is_start):
    event_id = "4688" if is_start else "4689"
    name_attr = "NewProcessName" if is_start else "ProcessName"
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <Triggers>
        <EventTrigger>
          <Enabled>true</Enabled>
          <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="Security"&gt;&lt;Select Path="Security"&gt;*[System[EventID={event_id}]] and *[EventData[Data[@Name='{name_attr}']='{full_path}']]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
        </EventTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>HighestAvailable</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
        <Hidden>true</Hidden>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>"{SVV_PATH}"</Command>
          <Arguments>/SetDefault "{device_id}" all</Arguments>
        </Exec>
      </Actions>
    </Task>"""
    return xml_template

def write_task(task_name, xml_content):
    xml_path = os.path.join(script_dir, f"temp_{task_name}.xml")
    with open(xml_path, "w", encoding="utf-16") as f: f.write(xml_content)
    process = subprocess.run(["schtasks", "/create", "/tn", task_name, "/xml", xml_path, "/f"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if os.path.exists(xml_path): os.remove(xml_path)
    return process.returncode == 0

def delete_task(task_name):
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AudioTriggerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AudioTrigger") 
        self.geometry("850x550")
        self.resizable(False, False)
        
        if not os.path.exists(SVV_PATH):
            messagebox.showerror("缺少核心组件", f"找不到 SoundVolumeView.exe！\n请将其与本程序放在同一目录。")
            sys.exit()
            
        ensure_audit_policy() 
        
        self.config = load_config()
        self.device_dict = get_audio_devices() 
        
        self.selected_left = None
        self.selected_right = None
        self.left_btns = {}
        self.right_btns = {}
        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        left_header = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))
        ctk.CTkLabel(left_header, text="我的游戏库", font=("Microsoft YaHei", 16, "bold")).pack(side="left")
        ctk.CTkButton(left_header, text="添加程序", command=self.browse_file, width=100).pack(side="right", padx=(0, 15))

        right_header = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_header.grid(row=0, column=2, sticky="ew", padx=(10, 0), pady=(0, 5))
        ctk.CTkLabel(right_header, text="自动处理列表", font=("Microsoft YaHei", 16, "bold")).pack(side="left")

        self.left_listbox = ctk.CTkScrollableFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        self.left_listbox.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=1, sticky="ns", padx=10)
        
        ctk.CTkButton(btn_frame, text="▶", font=("Arial", 28, "bold"), width=60, height=40, command=self.move_to_right).pack(pady=(80, 10))
        ctk.CTkButton(btn_frame, text="◀", font=("Arial", 28, "bold"), width=60, height=40, command=self.move_to_left).pack(pady=(10, 10))
        ctk.CTkButton(btn_frame, text="×", font=("Arial", 28, "bold"), fg_color="#C0392B", hover_color="#E74C3C", width=60, height=40, command=self.delete_entry).pack(pady=(10, 10))

        self.right_listbox = ctk.CTkScrollableFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        self.right_listbox.grid(row=1, column=2, sticky="nsew", padx=(10, 0))

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(bottom_frame, text="清除所有规则", fg_color="#8B0000", hover_color="#FF0000", command=self.clear_all_rules).pack(side="left")
        
        self.banner_label = ctk.CTkLabel(bottom_frame, text="", text_color="#2ECC71", font=("Microsoft YaHei", 13, "bold"))
        self.banner_label.pack(side="left", padx=15)

        device_names = list(self.device_dict.keys())
        dev_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        dev_frame.pack(side="right")
        
        ctk.CTkLabel(dev_frame, text="游戏设备(耳机):").grid(row=0, column=0, padx=5, pady=5)
        self.headset_combo = ctk.CTkComboBox(dev_frame, values=device_names, width=220, command=self.on_device_changed)
        self.headset_combo.grid(row=0, column=1, padx=5, pady=5)
        if self.config["headset"] in device_names: 
            self.headset_combo.set(self.config["headset"])
        else:
            self.headset_combo.set("请选择设备")

        ctk.CTkLabel(dev_frame, text="日常设备(音箱):").grid(row=1, column=0, padx=5, pady=5)
        self.speaker_combo = ctk.CTkComboBox(dev_frame, values=device_names, width=220, command=self.on_device_changed)
        self.speaker_combo.grid(row=1, column=1, padx=5, pady=5)
        if self.config["speaker"] in device_names: 
            self.speaker_combo.set(self.config["speaker"])
        else:
            self.speaker_combo.set("请选择设备")
        
        self.draw_lists()

    def show_banner(self, text):
        self.banner_label.configure(text=text)
        self.after(2500, lambda: self.banner_label.configure(text=""))

    def browse_file(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if file_path:
            full_path = get_true_case_path(os.path.normpath(file_path))
            exe_name = os.path.basename(full_path)
            if exe_name not in self.config["rules"] and exe_name not in self.config["library"]:
                self.config["library"][exe_name] = full_path
                save_config(self.config)
                self.draw_lists()

    def draw_lists(self):
        for w in self.left_listbox.winfo_children(): w.destroy()
        for w in self.right_listbox.winfo_children(): w.destroy()
        self.left_btns.clear()
        self.right_btns.clear()

        for exe_name in sorted(self.config["library"].keys()):
            btn = ctk.CTkButton(self.left_listbox, text=exe_name, fg_color="transparent", anchor="w", command=lambda a=exe_name: self.select_left(a))
            btn.pack(fill="x", pady=2)
            self.left_btns[exe_name] = btn

        for exe_name in sorted(self.config["rules"].keys()):
            btn = ctk.CTkButton(self.right_listbox, text=exe_name, fg_color="transparent", anchor="w", command=lambda a=exe_name: self.select_right(a))
            btn.pack(fill="x", pady=2)
            self.right_btns[exe_name] = btn
            
        self.update_selection_colors()

    def update_selection_colors(self):
        for name, btn in self.left_btns.items(): btn.configure(fg_color="#1f538d" if name == self.selected_left else "transparent")
        for name, btn in self.right_btns.items(): btn.configure(fg_color="#1f538d" if name == self.selected_right else "transparent")

    def select_left(self, name):
        self.selected_left = name
        self.selected_right = None 
        self.update_selection_colors()

    def select_right(self, name):
        self.selected_right = name
        self.selected_left = None 
        self.update_selection_colors()

    def move_to_right(self):
        if not self.selected_left: return
        headset_name = self.headset_combo.get()
        speaker_name = self.speaker_combo.get()
        
        exe_name = self.selected_left
        full_path = self.config["library"][exe_name]

        has_valid_device = (headset_name != "请选择设备" and speaker_name != "请选择设备" and 
                            "未检测" not in headset_name and "未检测" not in speaker_name and 
                            headset_name and speaker_name)

        if has_valid_device:
            headset_guid = self.device_dict.get(headset_name)
            speaker_guid = self.device_dict.get(speaker_name)
            write_task(f"AudioTrigger_ON_{exe_name}", generate_xml(full_path, headset_guid, True))
            write_task(f"AudioTrigger_OFF_{exe_name}", generate_xml(full_path, speaker_guid, False))

        del self.config["library"][exe_name]
        self.config["rules"][exe_name] = full_path
        save_config(self.config)
        self.selected_left = None
        self.draw_lists()

    def move_to_left(self):
        if not self.selected_right: return
        exe_name = self.selected_right
        full_path = self.config["rules"][exe_name]
        
        delete_task(f"AudioTrigger_ON_{exe_name}")
        delete_task(f"AudioTrigger_OFF_{exe_name}")
        
        del self.config["rules"][exe_name]
        self.config["library"][exe_name] = full_path
        save_config(self.config)
        self.selected_right = None
        self.draw_lists()

    def delete_entry(self):
        if self.selected_left:
            exe_name = self.selected_left
            del self.config["library"][exe_name]
            save_config(self.config)
            self.selected_left = None
            self.draw_lists()
        elif self.selected_right:
            exe_name = self.selected_right
            delete_task(f"AudioTrigger_ON_{exe_name}")
            delete_task(f"AudioTrigger_OFF_{exe_name}")
            del self.config["rules"][exe_name]
            save_config(self.config)
            self.selected_right = None
            self.draw_lists()

    def on_device_changed(self, choice=None):
        self.config["headset"] = self.headset_combo.get()
        self.config["speaker"] = self.speaker_combo.get()
        save_config(self.config)
        
        headset_name = self.config["headset"]
        speaker_name = self.config["speaker"]
        
        if headset_name == "请选择设备" or speaker_name == "请选择设备" or not headset_name or not speaker_name:
            return

        headset_guid = self.device_dict.get(headset_name)
        speaker_guid = self.device_dict.get(speaker_name)
        
        if not headset_guid or not speaker_guid:
            return

        for exe_name, full_path in self.config["rules"].items():
            write_task(f"AudioTrigger_ON_{exe_name}", generate_xml(full_path, headset_guid, True))
            write_task(f"AudioTrigger_OFF_{exe_name}", generate_xml(full_path, speaker_guid, False))

    def clear_all_rules(self):
        try:
            output = subprocess.check_output('schtasks /query /fo csv', shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode('ansi', errors='ignore')
            for line in output.splitlines():
                if "AudioTrigger_" in line:
                    task_name = line.split('","')[0].strip('"').lstrip('\\')
                    delete_task(task_name)
            self.config["library"].update(self.config["rules"])
            self.config["rules"].clear()
            save_config(self.config)
            self.selected_left = None
            self.selected_right = None
            self.draw_lists()
            self.show_banner("已清除所有规则")
        except: pass

if __name__ == "__main__":
    app = AudioTriggerApp()
    app.mainloop()