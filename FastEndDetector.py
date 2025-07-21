import threading
import time
import TimeLogger
import GlobalShareVariable
import IdleTracker
import TimerCore

_running = True
_thread = None

def fast_end_loop():
    global _running
    sleep_interval = 1.0

    while _running:
        try:
            is_running = TimerCore.is_all_timer_running()
            is_idle = IdleTracker.is_idle() 
            visible_windows = GlobalShareVariable.window_list

            if is_running and not is_idle:
                sleep_interval = 0.3
                if len(visible_windows) == 0:
                    print("[FastEndDetector] 조건 만족. 빠른 로그 아웃 트리거.")
                    TimeLogger.log_end(reason="빠른종료감지")
            else:
                sleep_interval = 1.0

        except Exception as e:
            print(f"[FastEndDetector] 오류 발생: {e}")
            sleep_interval = 1.0

        time.sleep(sleep_interval)

def start():
    global _thread
    _thread = threading.Thread(target=fast_end_loop, daemon=True)
    _thread.start()
    print("[FastEndDetector] 적응형 서브 루프 시작됨")

def stop():
    global _running, _thread
    _running = False
    if _thread is not None:
        _thread.join()