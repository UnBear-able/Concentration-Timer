# 현재 포그라운드 창의 실행 파일명을 추적하여 작업 타이머 제어에 활용함

import win32gui
import win32process
import psutil
import GlobalShareVariable

# 전역 상태 변수
current_process_name = ""
previous_process_name = ""

# 현재 상태를 외부에서 불러올 수 있게 하는 함수들
def get_current_process():
    return current_process_name

def get_previous_process():
    return previous_process_name

# 설정값에 따라 현재/직전 프로세스를 반환
def get_tracked_windows():
    mode = GlobalShareVariable.track_mode
    if mode == "single":
        return [get_current_process()]
    elif mode == "dual":
        return [get_current_process(), get_previous_process()]
    else:
        return [get_current_process()]  # fallback

# 현재 포그라운드 창의 프로세스 이름을 가져오는 함수
def get_foreground_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        return proc.name().strip().lower()
    except Exception:
        return "알 수 없음"

# 현재/직전 프로세스 추적 (1회 수행)
def track_foreground_window():
    '''현재, 직전 프로세스 추적'''
    global current_process_name, previous_process_name
    proc_name = get_foreground_process_name()
    if proc_name != current_process_name:
        previous_process_name = current_process_name
        current_process_name = proc_name
