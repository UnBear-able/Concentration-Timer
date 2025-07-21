# IdleTracker.py

import ctypes
import GlobalShareVariable

# Windows 구조체 정의
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

# 내부 상태 저장
_is_idle = False

def get_idle_duration():
    """마지막 입력 후 경과 시간 (초 단위)"""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0  # 1000 = 1초
    return 0

def check_idle_state():
    """현재 유휴 상태인지 계산하여 내부 상태 갱신"""
    global _is_idle
    idle_time = get_idle_duration()
    threshold = GlobalShareVariable.idle_threshold_sec or 60
    prev = _is_idle
    _is_idle = idle_time >= threshold

    # 상태 변화 감지 시 로그 출력
    if prev != _is_idle:
        status = "잠수중" if _is_idle else "활동 재개"
        print(f"[IdleTracker] 상태 변경: {status}")

def is_idle():
    """외부에서 현재 유휴 상태인지 확인하는 함수"""
    return _is_idle
