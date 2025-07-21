# main_gui.py: 프로그램 실행의 진입점이자 GUI 및 타이머, 저장 모듈 연결부

import Consent
if not Consent.has_user_consented():
    Consent.request_user_consent()

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# 내부 타이머 구조 및 상태 공유
import TimerCore
import GlobalShareVariable

# 프로세스 및 유휴 상태 감지
import ProcessTracker
import IdleTracker

# 기록 및 저장 관련
import TimeLogger
import TimeSave
import WorkSave
import WorkChecker

# UI기능
import TimeEditor
import TimeHistory
import SettingUi


class WorkMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("집중도 체크 타이머")
        self.root.geometry("520x500")
        self.root.resizable(False, False)

        self._last_window_list = []


        # ========== 1. 실시간 상태 영역 ==========
        self.status_frame = ttk.LabelFrame(root, text="🔎 실시간 상태", padding=10)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        self.status_grid = ttk.Frame(self.status_frame)
        self.status_grid.pack(fill="x")

        # 실시간 상태 라벨 추가

        self.status_grid.columnconfigure(0, weight=1)  # 현재 창
        self.status_grid.columnconfigure(1, weight=0)  # spacer
        self.status_grid.columnconfigure(2, weight=1)  # 유휴 상태
        self.status_grid.columnconfigure(3, weight=1)  # 타이머 상태

        # 실시간 상태 라벨 4개
        self.current_window_label = ttk.Label(self.status_grid, text="현재 창: -", width=25)
        self.current_window_label.grid(row=0, column=0, sticky="w")

        self.idle_label = ttk.Label(self.status_grid, text="현재 상태: -", width=20)
        self.idle_label.grid(row=0, column=2, sticky="w")
        

        self.previous_window_label = ttk.Label(self.status_grid, text="직전 창: -", width=25)
        self.previous_window_label.grid(row=1, column=0, sticky="w")

        self.timer_label = ttk.Label(self.status_grid, text="타이머 상태: -", width=20)
        self.timer_label.grid(row=1, column=2, sticky="w")
       

        # ========== 2. 타이머 영역 ==========
        
        self.timer_frame = ttk.LabelFrame(root, text="⏱ 세션 타이머", padding=10)
        self.timer_frame.pack(fill="x", padx=10, pady=5)

        self.date_display = ttk.Label(self.timer_frame, text="00:00:00", font=("Courier", 48, "bold"), anchor="center")
        self.date_display.pack(pady=10)

       # 세션 타이머 설정 및 시작 (전역 date_timer 참조)
        # GlobalShareVariable.date_timer = TimerCore.SessionTimer()
        # self.date_timer = GlobalShareVariable.date_timer

        self.date_timer = TimerCore.get_session_timer()

        # 총 타이머 설정 (전역 timer 사용)
        self.All_timer = TimerCore.get_cumulative_timer()

        # 자동 저장 루프 시작
        TimeSave.start_auto_save_loop(self.All_timer.get_elapsed_time)


        # ========== 3. 작업창 관리 영역 ==========
        self.task_frame = ttk.LabelFrame(root, text="⛏️ 작업창 선택", padding=10)
        self.task_frame.pack(fill="both", expand=False, padx=10, pady=5)

        self.task_frame.columnconfigure(0, weight=1)
        self.task_frame.columnconfigure(1, weight=0)
        self.task_frame.columnconfigure(2, weight=1)

        self.available_label = ttk.Label(self.task_frame, text="현재 열린 창", anchor="center")
        self.available_label.grid(row=0, column=0)

        self.registered_label = ttk.Label(self.task_frame, text="감지할 작업 창", anchor="center")
        self.registered_label.grid(row=0, column=2)

        self.available_list = tk.Listbox(self.task_frame, height=7)
        self.available_list.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="nsew")

        self.registered_list = tk.Listbox(self.task_frame, height=7)
        self.registered_list.grid(row=1, column=2, padx=(10, 0), pady=5, sticky="nsew")

         # 등록창 초기값 불러오기
        loaded = WorkSave.load_registered_list()
        for name in loaded:
            self.registered_list.insert(tk.END, name)

        # 감지 기준에도 반영
        WorkChecker.update_registered_list(loaded)

        self.button_frame = ttk.Frame(self.task_frame)
        self.button_frame.grid(row=1, column=1, pady=5)

        self.add_button = ttk.Button(self.button_frame, text="등록 ➡", command=self.work_add, width=10)
        self.add_button.pack(pady=5)

        self.remove_button = ttk.Button(self.button_frame, text="⬅ 삭제", command=self.work_remove, width=10)
        self.remove_button.pack(pady=5)

        self.save_button = ttk.Button(self.button_frame, text="💾 저장", command=self.work_save, width=10)
        self.save_button.pack(pady=5)



        # ========== 4. 하단 버튼 영역 ==========
        self.button_bar = ttk.Frame(root, padding=5)
        self.button_bar.pack(fill="x", padx=10, pady=10)

        # 5칸 구조로 구성 (0~4번 column)
        for i in range(5):
            self.button_bar.columnconfigure(i, weight=1, uniform="equal")

        # 양끝 + 중앙 버튼 배치
        self.reset_button = ttk.Button(self.button_bar, text="🔗 설정", command=self.setting_bt)
        self.reset_button.grid(row=0, column=0, padx=5, sticky="w")  # 왼쪽 정렬

        self.edit_button = ttk.Button(self.button_bar, text="타이머 수정", command=self.edit_bt)
        self.edit_button.grid(row=0, column=2, padx=5)  # self.button_bar 안에 넣어야 함

        self.view_log_button = ttk.Button(self.button_bar, text="📜 기록 보기", command=self.history_bt)
        self.view_log_button.grid(row=0, column=4, padx=5, sticky="e")  # 오른쪽 정렬

        self.root.protocol("WM_DELETE_WINDOW", self.on_close) #윈도우 종료시 창을 닫음 -> end 로그 작성

        self.update_all_ui()


    def update_all_ui(self):
        track_mode = GlobalShareVariable.track_mode
        current = ProcessTracker.get_current_process()
        previous = ProcessTracker.get_previous_process()

        self.current_window_label.config(text=f"현재 창: {current}")

        if track_mode == "dual":
            self.previous_window_label.config(text=f"직전 창: {previous}")
        else:
            self.previous_window_label.config(text="직전 창: -")

        idle = IdleTracker.is_idle()
        idle_text = "잠수 중🐋" if idle else "활동 중"
        self.idle_label.config(text=f"유휴 상태: {idle_text}")

        main_timer = TimerCore.get_cumulative_timer()
        session_timer = TimerCore.get_session_timer()
        if (main_timer and main_timer.is_running()) or (session_timer and session_timer.is_running()):
            self.timer_label.config(text="타이머 상태: ▶ 작동 중")
        else:
            self.timer_label.config(text="타이머 상태: ⏸ 일시정지")

        date_elapsed = self.date_timer.get_elapsed_time()
        formatted_date = TimeEditor.format_seconds_hhmmss(date_elapsed)
        self.date_display.config(text=formatted_date)

        current_set = set(GlobalShareVariable.window_list)
        last_set = set(self._last_window_list)
        if current_set != last_set:
            self.available_list.delete(0, tk.END)
            for name in sorted(current_set):
                self.available_list.insert(tk.END, name)
            self._last_window_list = list(GlobalShareVariable.window_list)

        self._ui_after_id = self.root.after(1000, self.update_all_ui)

        

    def history_bt(self):
        TimeHistory.open_history_window(self.root)

    def edit_bt(self):
        TimeEditor.open_time_editor(self.root)

    def setting_bt(self):
        SettingUi.SettingWindow(self.root)




    # Dummy 메서드 (추후 구현 필요)
    def work_add(self):
        # 현재 available_list에서 선택된 항목 인덱스들 가져오기
        selected_indices = self.available_list.curselection()
        selected_items = [self.available_list.get(i) for i in selected_indices]

        # 중복 없이 registered_list에 추가
        existing = set(self.registered_list.get(0, tk.END))
        new_items = set(selected_items) - existing

        for item in new_items:
            self.registered_list.insert(tk.END, item)

        # 내부 로직 반영 (WorkChecker 갱신)
        new_list = self.registered_list.get(0, tk.END)
        WorkChecker.update_registered_list(new_list)

    def work_remove(self):
        # 선택된 인덱스들을 가져오고 뒤에서부터 삭제 (인덱스 밀림 방지)
        selected_indices = list(self.registered_list.curselection())
        selected_indices.reverse()

        for i in selected_indices:
            self.registered_list.delete(i)

        # 내부 로직 반영 (WorkChecker 갱신)
        new_list = self.registered_list.get(0, tk.END)
        WorkChecker.update_registered_list(new_list)

    def work_save(self):
        items = self.registered_list.get(0, tk.END)
        WorkSave.save_registered_list(items)
        messagebox.showinfo("저장 완료", "목록이 저장되었습니다!")



    # 창이 종료되면 end 로그를 남김
    def on_close(self):
        print(f"[main_gui] 메인창 종료")
        TimeLogger.log_end()

        try:
            LoopManager.stop()
            LoggerCheckLoop.stop()
            FastEndDetector.stop()
        except Exception as e:
            print(f"[루프 종료 실패] {e}")

        self.root.destroy()



if __name__ == "__main__":
    import LoopManager
    LoopManager.start() # 창 추적, 유휴상태 체크 루프 on

    import LoggerCheckLoop
    LoggerCheckLoop.start() # 타이머 상태를 추적해 로그에 기록 신호를 보내는 루프 on

    import FastEndDetector
    FastEndDetector.start() # 빠른 종료와 자원 관리를 위한 적응형 루프 on

    TimeLogger.check_log_recovery() # 로그 로딩중 에러시 복구 코드
    TimeLogger.check_log_backup_recovery()# 백업의 백업코드

    root = tk.Tk()
    app = WorkMonitorApp(root)
    root.mainloop()
