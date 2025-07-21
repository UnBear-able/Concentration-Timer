# WindowLister.py

import win32gui
import win32process
import psutil

def get_open_windows():
    """열려 있는 창들의 실행 파일명 리스트 반환"""
    window_list = set()

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        if win32gui.GetWindowText(hwnd) == "":
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            exe_name = proc.name().strip().lower()
            window_list.add(exe_name)
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return sorted(window_list)
