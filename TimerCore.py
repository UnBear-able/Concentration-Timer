# TimerCore 모듈: 작업 집중 타이머의 핵심 타이머 로직 관리

import time
import GlobalShareVariable
import TimeSave



class BaseTimer:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def pause(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False

    def resume(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def get_elapsed_time(self):
        if self.running:
            return self.elapsed_time + (time.time() - self.start_time)
        return self.elapsed_time

    def is_running(self):
        return self.running


class SessionTimer(BaseTimer):
    """
    매 실행 시마다 타이머가 0부터 시작되는 타이머
    """
    def __init__(self):
        super().__init__()
        self.reset()


class CumulativeTimer(BaseTimer):
    """
    외부 파일로부터 초기 시간을 불러와서 이어서 작동하는 타이머
    TimeSave 모듈에서 초기 시간 로드 예정
    """
    def __init__(self, initial_time=0):
        super().__init__()
        self.elapsed_time = initial_time  # 외부에서 로드된 값


initial_time = TimeSave.load_time()
session_timer = SessionTimer()
cumulative_timer = CumulativeTimer(initial_time)
_message_value = "" # 타이머가 동작하는 이유를 받아오는 내부용 변수




def pause():
    if not session_timer.is_running() or not cumulative_timer.is_running():
        return  # 둘 중 하나라도 이미 정지중이면 탈출
    
    session_timer.pause()
    cumulative_timer.pause()

def resume():
    if session_timer.is_running() and cumulative_timer.is_running():
        return  # 둘 중 하나라도 이미 작동중이면 탈출
    
    session_timer.resume()
    cumulative_timer.resume()

'''======================================================================'''

def get_session_timer(): #main_gui에서 최초 한번 선언함
    return session_timer

def get_cumulative_timer():
    return cumulative_timer

def reset_cumulativeTimer():
    cumulative_timer.reset()

def reset_session_timer():
    session_timer.reset()

def is_all_timer_running():
    return session_timer.is_running() and cumulative_timer.is_running()




def get_session_elapsed():# 세션 타이머 값 반환
    return session_timer.get_elapsed_time()

def get_cumulative_elapsed():# 누적 타이머 값 반환
    return cumulative_timer.get_elapsed_time()

def set_cumulative_elapsed(seconds):
    if seconds is None:
        return
    cumulative_timer.elapsed_time = seconds
    if cumulative_timer.is_running():
        cumulative_timer.start_time = time.time()

def set_session_elapsed(seconds):
    if seconds is None:
        return
    session_timer.elapsed_time = seconds
    if session_timer.is_running():
        session_timer.start_time = time.time()



def evaluate_timer_state(): # 타이머 상태 설정
    if GlobalShareVariable.history_open:
         timer_state_print("타이머 일시정지 - 기록창 열림")
         pause()
    elif GlobalShareVariable.editor_open:
        timer_state_print("타이머 일시정지 - 수정창 열림")
        pause()
    elif GlobalShareVariable.idle_state:
        timer_state_print("타이머 일시정지 - 잠수중")
        pause()
    elif not GlobalShareVariable.working_state:
        timer_state_print("타이머 일시 정지 - 포그라운드 불일치")
        pause()
    else:
        try:
            timer_state_print("타이머 작동 - 조건 만족")
            resume()
        except Exception as e:
            timer_state_print(f"타이머 동작 실패: {e}")

# 상태 메세지 출력이 1초마다 출력하는걸 방지하는 함수
def timer_state_print(reason=""):
    global _message_value #처음에 "" 로 초기화
    state_message = reason # 값 받아주고 

    if state_message != _message_value: # 이전과 다른지 비교해서 다르면 메세지 출력
            print(f"[TimerCore] {reason}")
    _message_value = reason # 출력값과 같게 조정