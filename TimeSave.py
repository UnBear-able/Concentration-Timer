# TimeSave 모듈: 타이머 데이터를 파일로 저장하고 불러오는 기능 담당

import json
import os
import threading
from datetime import datetime

SAVE_DIR = os.path.join(os.getenv("APPDATA"), "NungTimer")
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "cumulative_timer_data.json")

def save_time(elapsed_seconds):
    """
    누적 시간을 초 단위로 저장 
    """
    # print(f"[TimeSave] 총 타이머 저장됨")

    data = {
        "elapsed_time": elapsed_seconds,
        "last_saved": datetime.now().isoformat()
    }

    try:
        with open(SAVE_PATH, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[오류] 파일 저장 실패: {e}")


def load_time():
    print(f"[TimeSave] 시도 중: {SAVE_PATH}")

    if not os.path.exists(SAVE_PATH):
        print("[TimeSave] 파일 없음")
        return 0

    try:
        with open(SAVE_PATH, 'r') as f:
            data = json.load(f)
            elapsed = data.get("elapsed_time", 0)
            print(f"[TimeSave] 로드된 값: {elapsed} ({type(elapsed)})")

            if not isinstance(elapsed, (int, float)):
                raise ValueError("숫자 아님")

            return elapsed
    except Exception as e:
        print(f"[TimeSave] 에러: {e}")
        return 0

def start_auto_save_loop(get_time_callback):
    """
    주어진 get_elapsed_time 콜백을 3초마다 호출하여 저장
    """
    def loop():
        elapsed = get_time_callback()
        save_time(elapsed)
        t = threading.Timer(3, loop)
        t.daemon = True  # <-- 이 줄을 추가! 창이 종료되면 루프도 종료됨
        t.start()

    loop()
