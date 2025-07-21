import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import os
import json
import TimerCore
import GlobalShareVariable
import GraphCanvas
from TimeEditor import format_seconds_hhmmss

def open_history_window(root):
    print("[History] 기록 창 열림 ")
    is_timer_running = TimerCore.is_all_timer_running()
    if is_timer_running:
        GlobalShareVariable.history_open = True
        TimerCore.evaluate_timer_state()
    else:
        GlobalShareVariable.history_open = True

    displayed_elapsed_time = TimerCore.get_cumulative_elapsed()
    elapsed_updater = None

    dim = tk.Frame(root, bg="gray")
    dim.place(relx=0, rely=0, relwidth=1, relheight=1)
    dim.lift()

    history_window = tk.Toplevel(root)
    history_window.title("⏱ 총 타이머 기록")
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()
    history_window.geometry(f"600x400+{x}+{y}")
    history_window.resizable(False, False)
    history_window.transient(root)
    history_window.grab_set()
    history_window.lift()

    top_frame = tk.LabelFrame(history_window, text="누적 타이머", labelanchor='n', bd=2, relief="groove", padx=20, pady=15)
    top_frame.pack(pady=(0, 15))

    line_frame = tk.Frame(history_window)
    line_frame.pack(fill="x", padx=20, pady=(20, 0))
    tk.Frame(line_frame, bg="gray", height=1).pack(side="left", fill="x", expand=True, padx=(0, 10))
    tk.Label(line_frame, text="타이머 작동 기록", font=("Malgun Gothic", 9)).pack(side="left")
    tk.Frame(line_frame, bg="gray", height=1).pack(side="left", fill="x", expand=True, padx=(10, 0))

    outer_frame = tk.Frame(history_window)
    outer_frame.pack(fill="both", expand=True)

    formatted = str(format_seconds_hhmmss(seconds=int(displayed_elapsed_time)))
    timer_display = tk.Label(top_frame, text=formatted, font=("Courier", 36, "bold"))
    timer_display.pack()

    def update_elapsed_label():
        nonlocal elapsed_updater
        formatted = str(format_seconds_hhmmss(seconds=int(displayed_elapsed_time)))
        timer_display.config(text=formatted)
        elapsed_updater = timer_display.after(1000, update_elapsed_label)

    update_elapsed_label()

    canvas = tk.Canvas(outer_frame, bg="white", height=170, highlightthickness=0)
    h_scroll = ttk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=h_scroll.set)
    canvas.pack(side="top", fill="x")
    h_scroll.pack(side="top", fill="x")

    log_path = os.path.join(os.getenv("APPDATA"), "NungTimer", "log_current.json")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    else:
        log_data = {}

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_index, graph_width, left_margin = GraphCanvas.draw_log_to_canvas(canvas, log_data, today_str)
    canvas_width = canvas.winfo_width()
    history_window.after(100, lambda: canvas.xview_moveto((today_index * (GraphCanvas.BAR_WIDTH + GraphCanvas.SPACING) + left_margin - canvas_width // 2) / graph_width))

    def _on_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_close():
        if elapsed_updater is not None:
            timer_display.after_cancel(elapsed_updater)
        print("[History] 기록 창 닫힘")
        canvas.unbind_all("<MouseWheel>")
        dim.destroy()
        history_window.destroy()
        GlobalShareVariable.history_open = False

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    history_window.protocol("WM_DELETE_WINDOW", on_close)

    log_files = []
    bottom_frame = tk.Frame(history_window)
    bottom_frame.pack(side="bottom", fill="x", padx=20, pady=10)

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            current_data = json.load(f)
        if current_data:
            start_date = sorted(current_data.keys())[0]
            label = f"[{start_date} ~ 현재]*"
        else:
            label = "[현재 로그]*"
        log_files.append((label, log_path))

    logs_dir = os.path.join(os.getenv("APPDATA"), "NungTimer", "logs")
    def extract_end_date(filename):
        try:
            name = filename.replace("log_", "").replace(".json", "")
            parts = name.split("~")
            return datetime.strptime(parts[1], "%Y-%m-%d") if len(parts) == 2 else datetime.min
        except:
            return datetime.min

    if os.path.exists(logs_dir):
        files = [f for f in os.listdir(logs_dir) if f.endswith(".json")]
        sorted_files = sorted(files, key=extract_end_date, reverse=True)
        for fname in sorted_files:
            label = fname.replace("log_", "[").replace(".json", "]").replace("~", " ~ ")
            log_files.append((label, os.path.join(logs_dir, fname)))

    combo_frame = tk.Frame(bottom_frame)
    combo_frame.pack(side="right", padx=10)

    selected_log_var = tk.StringVar()
    log_combobox = ttk.Combobox(combo_frame, textvariable=selected_log_var, state="readonly", height=9, width=27)
    log_combobox["values"] = [label for label, _ in log_files]
    log_combobox.current(0)
    log_combobox.pack(side="left", padx=(0, 0))

    reset_btn = ttk.Button(bottom_frame, text="초기화", command=lambda: reset_logs() if log_combobox.current() == 0 else None)
    reset_btn.pack(side="left")

    def update_reset_btn_state():
        if log_combobox.current() == 0:
            reset_btn.state(["!disabled"])
            reset_btn.config(style="TButton")
        else:
            reset_btn.state(["disabled"])
            reset_btn.config(style="Disabled.TButton")

    style = ttk.Style()
    style.configure("Disabled.TButton", foreground="#888888")

    def on_log_select(event):
        nonlocal displayed_elapsed_time
        update_reset_btn_state()
        selection = selected_log_var.get()
        for label, path in log_files:

            if path != log_path:
                top_frame.config(text="이전 로그 기록 시간")
            else:
                top_frame.config(text="누적 타이머")

            if label == selection:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        selected_data = json.load(f)
                except:
                    return

                if path != log_path and "cumulative_total" in selected_data:
                    displayed_elapsed_time = selected_data["cumulative_total"]
                else:
                    displayed_elapsed_time = TimerCore.get_cumulative_elapsed()

                formatted = str(format_seconds_hhmmss(seconds=int(displayed_elapsed_time)))
                timer_display.config(text=formatted)

                canvas.delete("all")
                today_str = datetime.now().strftime("%Y-%m-%d") if path == log_path else None
                filtered_data = {k: v for k, v in selected_data.items() if k != "cumulative_total"}
                today_index, graph_width, left_margin = GraphCanvas.draw_log_to_canvas(canvas, filtered_data, today_str)
                canvas_width = canvas.winfo_width()
                canvas.xview_moveto((today_index * (GraphCanvas.BAR_WIDTH + GraphCanvas.SPACING) + left_margin - canvas_width // 2) / graph_width)
                break



    log_combobox.bind("<<ComboboxSelected>>", on_log_select)
    update_reset_btn_state()

    def reset_logs():
            nonlocal log_files

            if not messagebox.askokcancel("초기화 확인", "정말 타이머와 로그를 초기화 하시겠습니까?\n현재까지 기록된 타이머 값과 로그는 별도로 저장됩니다."):
                return
            backup_dir = os.path.join(os.getenv("APPDATA"), "NungTimer", "logs")
            os.makedirs(backup_dir, exist_ok=True)

            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        old_log_data = json.load(f)
                        start_dates = list(old_log_data.keys())
                        if start_dates:
                            start_date = start_dates[0].replace(":", "-").replace("/", "-")
                        else:
                            start_date = "unknown"
                except:
                    start_date = "unknown"
                end_date = datetime.now().strftime("%Y-%m-%d")
                base_name = f"log_{start_date}~{end_date}"
                backup_filename = base_name + ".json"
                backup_path = os.path.join(backup_dir, backup_filename)

                count = 1
                while os.path.exists(backup_path):
                    backup_filename = f"{base_name} ({count}).json"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    count += 1

                with open(log_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    old_data["cumulative_total"] = int(TimerCore.get_cumulative_elapsed())
                    with open(backup_path, "w", encoding="utf-8") as b:
                        json.dump(old_data, b, indent=2)

                os.remove(log_path)

            with open(log_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            TimerCore.reset_cumulativeTimer()
            TimerCore.reset_session_timer()

            # 콤보박스 갱신
            with open(log_path, "r", encoding="utf-8") as f:
                new_log_data = json.load(f)

            if new_log_data:
                start_date = sorted(new_log_data.keys())[0]
                label = f"[{start_date} ~ 현재]*"
            else:
                label = "[현재 로그]*"

            log_files.clear()
            log_files.append((label, log_path))

            if os.path.exists(logs_dir):
                files = [f for f in os.listdir(logs_dir) if f.endswith(".json")]
                sorted_files = sorted(files, key=extract_end_date, reverse=True)
                for fname in sorted_files:
                    label = fname.replace("log_", "[").replace(".json", "]").replace("~", " ~ ")
                    log_files.append((label, os.path.join(logs_dir, fname)))

            log_combobox["values"] = [label for label, _ in log_files]
            log_combobox.current(0)

            canvas.delete("all")
            with open(log_path, "r", encoding="utf-8") as f:
                new_log_data = json.load(f)
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_index, graph_width, left_margin = GraphCanvas.draw_log_to_canvas(canvas, new_log_data, today_str)
            canvas_width = canvas.winfo_width()
            canvas.xview_moveto((today_index * (GraphCanvas.BAR_WIDTH + GraphCanvas.SPACING) + left_margin - canvas_width // 2) / graph_width)

            elapsed = TimerCore.get_cumulative_elapsed()
            formatted = str(format_seconds_hhmmss(seconds=int(elapsed)))
            timer_display.config(text=formatted)

            log_combobox.current(0)
            log_combobox.event_generate("<<ComboboxSelected>>")

    tooltip_container = tk.LabelFrame(bottom_frame, bd=1, relief="solid", padx=5, pady=2)
    tooltip_container.pack(side="left", padx=0)

    def show_info_tooltip(event):
        info_tip = tk.Toplevel(history_window)
        info_tip.overrideredirect(True)
        info_tip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(info_tip, text="누적 타이머 값과 로그를 저장한 후 초기화 합니다", background="#ffffe0", relief="solid", borderwidth=1, font=("TkDefaultFont", 9), justify="left")
        label.pack(ipadx=10, ipady=3)
        event.widget._tooltip = info_tip

    def hide_info_tooltip(event):
        if hasattr(event.widget, "_tooltip"):
            event.widget._tooltip.destroy()
            del event.widget._tooltip

    info_label = tk.Label(bottom_frame, text="[ℹ]", font=("Arial", 11), cursor="hand2")
    info_label.pack(side="left", padx=(5, 15))
    info_label.bind("<Enter>", show_info_tooltip)
    info_label.bind("<Leave>", hide_info_tooltip)
