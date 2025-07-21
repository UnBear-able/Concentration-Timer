import tkinter as tk
from tkinter import ttk
import json
import os
import GlobalShareVariable

# AppData 경로 설정
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "NungTimer")
os.makedirs(APPDATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APPDATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "track_mode": "single",            # or "dual"
    "idle_threshold_sec": 60          # in seconds
}

class SettingWindow:
    def __init__(self, root):
        self.root = root

        self.dim = tk.Frame(root, bg="gray")
        self.dim.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.window = tk.Toplevel(root)
        self.window.title("설정")
        self.window.geometry("300x320+%d+%d" % (root.winfo_x(), root.winfo_y()))
        self.window.transient(root)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        self.window.resizable(False, False)  # 크기 조절 불가능하게 설정

        self.load_settings()
        self.open_setting_window()

    def open_setting_window(self):
        # 창 추적 방식
        track_frame = ttk.LabelFrame(self.window, text="창 추적 방식", padding=(10, 5))
        track_frame.pack(padx=15, pady=(10, 0), fill="x")

        self.track_var = tk.StringVar(value=self.settings["track_mode"])
        ttk.Radiobutton(track_frame, text="현재 창만", variable=self.track_var, value="single").pack(anchor="w")
        ttk.Radiobutton(track_frame, text="현재 창 + 직전 창", variable=self.track_var, value="dual").pack(anchor="w")

        # 유휴시간 설정
        idle_frame = ttk.LabelFrame(self.window, text="잠수 상태 간주 시간", padding=(10, 5))
        idle_frame.pack(padx=15, pady=(10, 0), fill="x")

        self.idle_var = tk.StringVar()
        idle_options = ["30초", "1분", "3분", "5분", "10분"]
        self.idle_map = {"30초": 30, "1분": 60, "3분": 180, "5분": 300, "10분": 600}
        for label, sec in self.idle_map.items():
            if self.settings["idle_threshold_sec"] == sec:
                self.idle_var.set(label)
                break
        self.idle_menu = ttk.Combobox(idle_frame, values=idle_options, textvariable=self.idle_var, state="readonly")
        self.idle_menu.pack(pady=5, anchor="w")

        # 버튼 영역
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=15)

        save_btn = ttk.Button(btn_frame, text="저장", command=self.save)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(btn_frame, text="취소", command=self.cancel)
        cancel_btn.pack(side="left", padx=5)

        # 저장 경로 안내 문구 추가
        ttk.Label(self.window,
                  text="⚙ 설정 및 로그 파일은 다음 경로에 저장됩니다:\nC:\\Users\\사용자명\AppData\\Roaming\\NungTimer",
                  font=("Arial", 9), foreground="gray", justify="left", wraplength=280).pack(pady=(5, 35))
        # 창 추적 방식

        # 크레딧 표시 (소심하게)
        
        credit_label = ttk.Label(
            self.window,
            text="Directed by 눙곰\n(with AI-assisted development by ChatGPT)",
            font=("Arial", 8),
            foreground="gray"
        )
        credit_label.pack(pady=(0, 10))
        

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except:
            self.settings = DEFAULT_SETTINGS.copy()

    def save(self):
        # 전역 반영
        GlobalShareVariable.track_mode = self.track_var.get()
        GlobalShareVariable.idle_threshold_sec = self.idle_map[self.idle_var.get()]

        # json 저장
        settings = {
            "track_mode": self.track_var.get(),
            "idle_threshold_sec": self.idle_map[self.idle_var.get()]
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        self.dim.destroy()
        self.window.destroy()

    def cancel(self):
        self.dim.destroy()
        self.window.destroy()

def apply_initial_settings():
    # 최초 실행 시 설정 파일이 없으면 생성
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2, ensure_ascii=False)

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except:
        settings = DEFAULT_SETTINGS.copy()

    GlobalShareVariable.track_mode = settings["track_mode"]
    GlobalShareVariable.idle_threshold_sec = settings["idle_threshold_sec"]

# 모듈 import 시 자동으로 설정값 적용
apply_initial_settings()
