import threading
import time
import TimeLogger
import TimerCore

_prev_state = None
_running = True  # 종료용 플래그


def run_sync_loop():
    global _prev_state, _running

    while _running:
        current_state = TimerCore.is_all_timer_running()

        if _prev_state is not None and current_state != _prev_state:
            if current_state:
                TimeLogger.log_start()
            else:
                TimeLogger.log_end()

        _prev_state = current_state
        time.sleep(1)

def start():
    t = threading.Thread(target=run_sync_loop, daemon=True)
    t.start()

def stop():
    global _running
    _running = False

