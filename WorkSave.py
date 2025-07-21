# WorkSave.py
# 등록된 감지 대상 창 저장 경로
import json
import os

# AppData\Roaming\NungTimer 경로 설정
SAVE_DIR = os.path.join(os.getenv("APPDATA"), "NungTimer")
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "registered_windows.json")

def save_registered_list(process_list):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(list(process_list), f)
        print("[WorkSave] 등록창 저장 완료")
    except Exception as e:
        print(f"[WorkSave] 저장 실패: {e}")

def load_registered_list():
    try:
        if not os.path.exists(SAVE_PATH):
            return []
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("[WorkSave] 등록창 불러오기 완료\n===========타이머 작동 준비 완료===========")
        return data
    except Exception as e:
        print(f"[WorkSave] 불러오기 실패: {e}")
        return []
