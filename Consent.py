import tkinter as tk
import json
import os
from datetime import datetime  # 시간 기록용

# AppData 경로 설정
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "NungTimer")
os.makedirs(APPDATA_DIR, exist_ok=True)

CONSENT_FILE = os.path.join(APPDATA_DIR, "consent.json")

DEFAULT_SETTINGS = {
    "track_mode": "dual",
    "idle_threshold_sec": 60
}

def has_user_consented():
    """consent.json 파일 존재 여부 + agreed: true 체크"""
    if not os.path.exists(CONSENT_FILE):
        return False

    try:
        with open(CONSENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("agreed", False) is True
    except Exception:
        return False

def request_user_consent():
    """동의창을 띄우고, 동의하면 파일 기록 및 설정 초기화"""
    win = tk.Tk()
    win.title("사용자 동의")
    win.geometry("420x160")
    win.resizable(False, False)

    label = tk.Label(win, text=(
        "이 프로그램은 창 추적 및 유휴 시간 상태를 기록합니다.\n"
        "데이터는 로컬에만 저장되며 정보를 수집하거나 외부로 전송되지 않습니다.\n"
        "동의하지 않으면 프로그램은 종료되며, 어떤 기록도 저장되지 않습니다."
    ), wraplength=400, justify="left")
    label.pack(pady=25)

    def agree():
        consent_data = {
            "agreed": True,
            "agreed_at": datetime.now().isoformat()
        }
        with open(CONSENT_FILE, "w", encoding="utf-8") as f:
            json.dump(consent_data, f, indent=2, ensure_ascii=False)
        win.destroy()

    def decline():
        win.destroy()
        exit()

    def on_close():
        decline()
    win.protocol("WM_DELETE_WINDOW", on_close)

    btn_frame = tk.Frame(win)
    btn_frame.pack()

    tk.Button(btn_frame, text="동의", command=agree).pack(side="left", padx=10)
    tk.Button(btn_frame, text="취소", command=decline).pack(side="left", padx=10)

    win.mainloop()
