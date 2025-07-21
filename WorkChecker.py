# WorkChecker.py

import ProcessTracker

# 등록된 작업창 목록
_registered_processes = set()

def update_registered_list(new_list):
    """main_gui에서 등록창 목록을 업데이트할 때 호출"""
    global _registered_processes
    _registered_processes = set(name.lower().strip() for name in new_list)

def is_in_registered_window():
    """현재 또는 직전 창이 등록된 작업창인지 여부 반환"""
    current = ProcessTracker.get_current_process()
    previous = ProcessTracker.get_previous_process()

    return current in _registered_processes or previous in _registered_processes

def get_registered_list():
    """디버깅/표시용: 등록된 목록 반환"""
    return list(_registered_processes)
