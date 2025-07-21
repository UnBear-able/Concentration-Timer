import os
import json
import shutil
from datetime import datetime, timedelta
from tkinter import messagebox
import TimerCore


SAVE_DIR = os.path.join(os.getenv("APPDATA"), "NungTimer")
os.makedirs(SAVE_DIR, exist_ok=True)
LOG_PATH = os.path.join(SAVE_DIR, "log_current.json")

# 현재 세션 시작 시각과 중복 방지 플래그
_current_start = None
_logged_end_once = False
_logged_start_once = False


# 로그 생성시 데이터 보호를 위해 임시 파일 만들기
def safe_save_log(log_data):
    temp_path = LOG_PATH + ".tmp"

    # bak 백업
    if os.path.exists(LOG_PATH):
        try:
            shutil.copy(LOG_PATH, LOG_PATH + ".bak")
        except Exception as e:
            print(f"[Logger] 로그 백업 실패: {e}")


    try:
        # 1단계: 임시 파일에 저장
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        # 2단계: 원본 파일을 덮어쓰기
        os.replace(temp_path, LOG_PATH)  # atomic replace

    except Exception as e:
        print(f"[Logger] 로그 저장 실패 (무결성 보호됨): {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================
# 📥 로그 파일에 엔트리 추가
# =========================
def _append_log_entry(entry):
    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        else:
            log_data = {}

        date = entry["date"]
        log_data.setdefault(date, []).append(entry)

        # 기존 json.dump(...) 대신 안전 저장 함수 호출
        safe_save_log(log_data)

    except Exception as e:
        print(f"[Logger] 시작 로그 저장 실패: {e}")


# =========================
# 🟢 로그 시작 기록
# =========================
def log_start():
    global _current_start, _logged_end_once, _logged_start_once

    if _logged_start_once:
        return

    _current_start = datetime.now()
    print(f"[Logger] 타이머 시작 로그 저장: {_current_start}")

    all_timer_value = int(TimerCore.get_cumulative_elapsed())

    log_entry = {
        "date": _current_start.strftime("%Y-%m-%d"),
        "start": _current_start.strftime("%H:%M:%S"),
        "main_timer_value": all_timer_value
    }

    _logged_start_once = True
    _logged_end_once = False
    _append_log_entry(log_entry)


# =========================
# 🔴 로그 종료 기록
# =========================
def log_end():
    global _current_start, _logged_end_once, _logged_start_once

    if _logged_end_once:
        return
    


    # 현재 종료 시각
    end_dt = datetime.now()
    end_date_str = end_dt.strftime("%Y-%m-%d")
    end_time_str = end_dt.strftime("%H:%M:%S")

    if _current_start is None:
        print("[Logger] 타이머가 작동한 적 없음 — 종료 로그 생략")
        return
    # 시작 시각
    start_date_str = _current_start.strftime("%Y-%m-%d")
    start_time_str = _current_start.strftime("%H:%M:%S")

    print(f"[Logger] 타이머 종료 로그 저장: {start_date_str} → {end_date_str} / {start_time_str} ~ {end_time_str}\n============================================")

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except Exception:
        log_data = {}

    sessions = log_data.get(start_date_str, [])

    if end_dt.date() > _current_start.date():
        if sessions and "end" not in sessions[-1]:
            sessions[-1]["end"] = "23:59:59"
        else:
            sessions.append({"start": start_time_str, "end": "23:59:59"})
        log_data[start_date_str] = sessions

        if end_date_str not in log_data:
            log_data[end_date_str] = []
        log_data[end_date_str].append({"start": "00:00:00", "end": end_time_str})
    else:
        if sessions and "end" not in sessions[-1]:
            sessions[-1]["end"] = end_time_str
        else:
            sessions.append({"start": start_time_str, "end": end_time_str})
        log_data[start_date_str] = sessions

    try:
        safe_save_log(log_data)
    except Exception as e:
        print(f"[Logger] 로그 저장 실패: {e}")

    _logged_end_once = True
    _logged_start_once = False





# =========================
# 🧼 비정상 종료 복구 처리
# =========================
def cleanup_last_session():
    """비정상 종료 후 마지막 세션에 end가 없으면 보정해서 기록"""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except Exception:
        return

    if not log_data:
        return

    latest_date = sorted(log_data.keys())[-1]
    sessions = log_data[latest_date]

    if not sessions:
        return

    last_session = sessions[-1]

    if "end" in last_session or "main_timer_value" not in last_session:
        return

    try:
        start_time_str = last_session["start"]
        start_date_str = last_session["date"]
        main_timer_value = last_session["main_timer_value"]

        # 시작 시간 파싱
        start_timestamp = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
        now_accum = int(TimerCore.get_cumulative_elapsed())
        elapsed_diff = now_accum - main_timer_value

        if elapsed_diff < 0:
            print("[Logger] 역산 불가: 음수 시간 차이")
            return

        # 보정된 종료 시각 계산
        recovered_end_timestamp = start_timestamp + timedelta(seconds=elapsed_diff)

        if recovered_end_timestamp.date() > start_timestamp.date():
            # 🔹 첫날 종료 보정: 23:59:59
            last_session["end"] = "23:59:59"
            log_data[start_date_str][-1] = last_session

            # 🔹 다음날 새 세션 생성
            new_date_str = recovered_end_timestamp.strftime("%Y-%m-%d")
            new_end_str = recovered_end_timestamp.strftime("%H:%M:%S")

            if new_date_str not in log_data:
                log_data[new_date_str] = []

            log_data[new_date_str].append({
                "date": new_date_str,
                "start": "00:00:00",
                "end": new_end_str
                # ❌ main_timer_value는 제외 → 역산 안 하게 함
            })

        else:
            # 날짜 넘기지 않은 경우 일반 end 추가
            last_session["end"] = recovered_end_timestamp.strftime("%H:%M:%S")
            log_data[start_date_str][-1] = last_session

        # 저장
        safe_save_log(log_data)

        print(f"[Logger] 비정상 종료 감지, end 로그 복구 완료")

    except Exception as e:
        print(f"[Logger] 로그 보정 실패: {e}")




# =========================
# 🔁 프로그램 시작 시 복구
# =========================
try:
    cleanup_last_session()
except Exception as e:
    print(f"[Logger] 세션 복구 중 예외 발생: {e}")




# 로그 저장 실패후 재부팅 시 복구를 요청하는 코드
def check_log_recovery():
    """이전 저장 실패로 남은 .tmp 로그 파일이 있다면 복구 여부를 묻는다"""
    tmp_path = LOG_PATH + ".tmp"
    if os.path.exists(tmp_path):
        user_choice = messagebox.askyesno(
            "이전 로그 복구",
            "이전 로그 저장 중 문제가 발생한 것으로 보입니다.\n로그를 복구하시겠습니까?"
        )

        if user_choice:
            try:
                os.replace(tmp_path, LOG_PATH)
                messagebox.showinfo("복구 완료", "이전 로그를 성공적으로 복구했습니다.")
            except Exception as e:
                messagebox.showerror("복구 실패", f"복구 중 오류 발생:\n{e}")
        else:
            try:
                os.remove(tmp_path)
                messagebox.showinfo("삭제 완료", "임시 로그 파일을 삭제했습니다.")
            except Exception as e:
                messagebox.showerror("삭제 실패", f"삭제 중 오류 발생:\n{e}")


#백업의 백업 코드, bak파일로 백업 시도
def check_log_backup_recovery(
):
    """log_current.json이 없고 log_current.json.bak이 있다면 복구 여부를 묻는다"""
    bak_path = LOG_PATH + ".bak"
    if not os.path.exists(LOG_PATH) and os.path.exists(bak_path):
        user_choice = messagebox.askyesno(
            "백업 로그 복구",
            "기존 로그 파일이 없고 백업(log_current.json.bak)이 존재합니다.\n복구하시겠습니까?"
        )

        if user_choice:
            try:
                os.replace(bak_path, LOG_PATH)
                messagebox.showinfo("복구 완료", "백업 로그를 복구했습니다.")
            except Exception as e:
                messagebox.showerror("복구 실패", f"복구 중 오류 발생:\n{e}")
