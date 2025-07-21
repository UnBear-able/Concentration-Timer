import threading
import time
import TimerCore
import ProcessTracker
import IdleTracker
import WorkChecker
import WindowLister
import GlobalShareVariable

_prev_idle = None
_prev_state = None
_running = True  # 종료용 플래그 추가
_thread = None

def run_monitoring_loop():
    global _prev_idle, _prev_state, _running

    while _running:
        # 창 추적 및 유휴 감지 수행
        ProcessTracker.track_foreground_window()
        IdleTracker.check_idle_state()
        GlobalShareVariable.window_list = WindowLister.get_open_windows()

        # 유휴 상태 판정
        GlobalShareVariable.idle_state = IdleTracker.is_idle()

        # 작업창 추적 (track_mode에 따라 현재/직전 창 모두 고려)
        tracked = ProcessTracker.get_tracked_windows()
        registered = WorkChecker.get_registered_list()
        GlobalShareVariable.working_state = any(w in registered for w in tracked)

        # 타이머 상태 평가
        TimerCore.evaluate_timer_state()
        time.sleep(1)

def start():
    global _thread
    _thread = threading.Thread(target=run_monitoring_loop, daemon=True)
    _thread.start()

def stop():
    global _running, _thread
    _running = False
    if _thread is not None:
        _thread.join()
