import tkinter as tk
from tkinter import ttk
import time
import GlobalShareVariable
import TimerCore

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("TkDefaultFont", 9), wraplength=450)
        label.pack(ipadx=10, ipady=3)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        if tw:
            tw.destroy()
        self.tipwindow = None


# 타이머를 99:59:59 이상도 누적 시간 형태로 출력하게 해줌.
def format_seconds_hhmmss(seconds):
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(seconds) % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = "gray"
        self.default_fg_color = kwargs.get("fg", "black")

        super().__init__(master, **kwargs)
        self["fg"] = self.default_fg_color

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder and self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg_color

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color

    def get_time_value(self):
        value = self.get().strip()
        if self["fg"] == self.placeholder_color or not value.isdigit():
            return self.placeholder
        return value


def seconds_to_hms(seconds):
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02}:{m:02}:{s:02}"


def hms_to_seconds(hms_str):
    try:
        h, m, s = map(int, hms_str.split(":"))
        return h * 3600 + m * 60 + s
    except (ValueError, TypeError):
        return None


def open_time_editor(root=None):
    if root is None:
        root = tk._default_root

    GlobalShareVariable.editor_open = True
    TimerCore.evaluate_timer_state()
    print("[Editor] 수정 창 열림 - 타이머 일시정지")
    dim = tk.Frame(root, bg="gray")
    dim.place(relx=0, rely=0, relwidth=1, relheight=1)

    editor = tk.Toplevel(root)
    editor.title("타이머 수동 수정")
    # 메인창과 겹치도록 위치 지정
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()
    editor.geometry(f"360x260+{x}+{y}")

    editor.resizable(False, False)
    editor.attributes("-topmost", True)
    # editor.lift(click_blocker_overlay)
    editor.grab_set()

    def save_and_close():
        def parse_time_value(entry):
            val = entry.get_time_value().strip()
            return int(val) if val.isdigit() else 0

        h = parse_time_value(hour_entry)
        m = parse_time_value(minute_entry)
        s = parse_time_value(second_entry)
        hs = session_hour_entry.get_time_value()
        ms = session_minute_entry.get_time_value()
        ss = session_second_entry.get_time_value()

        try:
            all_sec = int(h) * 3600 + int(m) * 60 + int(s)
            session_sec = int(hs) * 3600 + int(ms) * 60 + int(ss)
        except (ValueError, TypeError):
            all_sec = session_sec = None

        TimerCore.set_cumulative_elapsed(all_sec)

        if session_sec is not None:
            timer = TimerCore.get_session_timer()
            timer.elapsed_time = session_sec
            if timer.is_running():
                timer.start_time = time.time()

        GlobalShareVariable.editor_open = False
        print("[Editor] 수정 창 닫힘 - 타이머 값 재설정 완료, 타이머 동작")
        # click_blocker_overlay.destroy()
        dim.destroy()
        editor.destroy()
        TimerCore.evaluate_timer_state()

    def cancel():
        on_close()

    elapsed_all = TimerCore.get_cumulative_elapsed() or 0
    h, m, s = seconds_to_hms(elapsed_all).split(":")

    ttk.Label(editor, text="누적 타이머").pack(pady=(15, 10))
    timer_frame = ttk.Frame(editor)
    timer_frame.pack()

    hour_entry = PlaceholderEntry(timer_frame, placeholder=h, width=5, justify="center", fg="black")
    minute_entry = PlaceholderEntry(timer_frame, placeholder=m, width=5, justify="center", fg="black")
    second_entry = PlaceholderEntry(timer_frame, placeholder=s, width=5, justify="center", fg="black")

    hour_entry.pack(side="left", padx=5)
    ttk.Label(timer_frame, text=":").pack(side="left")
    minute_entry.pack(side="left", padx=5)
    ttk.Label(timer_frame, text=":").pack(side="left")
    second_entry.pack(side="left", padx=5)

    elapsed_session = TimerCore.get_session_elapsed() or 0
    hs, ms, ss = seconds_to_hms(elapsed_session).split(":")

    ttk.Label(editor, text="세션 타이머").pack(pady=(10, 10))
    session_frame = ttk.Frame(editor)
    session_frame.pack()

    session_hour_entry = PlaceholderEntry(session_frame, placeholder=hs, width=5, justify="center", fg="black")
    session_minute_entry = PlaceholderEntry(session_frame, placeholder=ms, width=5, justify="center", fg="black")
    session_second_entry = PlaceholderEntry(session_frame, placeholder=ss, width=5, justify="center", fg="black")

    session_hour_entry.pack(side="left", padx=5)
    ttk.Label(session_frame, text=":").pack(side="left")
    session_minute_entry.pack(side="left", padx=5)
    ttk.Label(session_frame, text=":").pack(side="left")
    session_second_entry.pack(side="left", padx=5)

    btn_frame = ttk.Frame(editor)
    btn_frame.pack(pady=25)

    info_frame = ttk.Frame(editor)
    info_frame.pack()

    ttk.Button(btn_frame, text="저장", command=save_and_close).pack(side="left", padx=10)
    
    info_button = ttk.Label(btn_frame, text="(ℹ)", foreground="gray", font=("Arial", 13))
    info_button.pack(side="left", padx=(0, 10)) 

    ttk.Button(btn_frame, text="취소", command=cancel).pack(side="left", padx=10)

    Tooltip(info_button, 
        "누적 타이머의 시간 수정은 로그 그래프에 영향을 끼치지 않습니다.\n"
        "(최종 저장값엔 적용됨)\n\n"
        "세션 타이머는 매 실행 시 초기화됩니다. 이를 수정하면...\n"
        "그냥 기분이 좋아집니다."
    )

    def on_close():
        GlobalShareVariable.editor_open = False
        print("[Editor] 수정 창 닫힘 - 타이머 동작")

        dim.destroy()
        editor.destroy()
        TimerCore.evaluate_timer_state()

    editor.protocol("WM_DELETE_WINDOW", on_close)
