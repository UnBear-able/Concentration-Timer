import tkinter as tk
from datetime import datetime, timedelta

# 전역 설정 상수
BAR_WIDTH = 7
SPACING = 55
MAX_HEIGHT = 100
BASE_Y = 120
SESSIONS_PER_PAGE = 10


class Tooltip:
    def __init__(self, canvas):
        self.canvas = canvas
        self.current_sessions = []
        self.current_page = 0

        self.frame = tk.Toplevel(canvas)
        self.frame.withdraw()
        self.frame.overrideredirect(True)
        self.frame.attributes("-topmost", True)

        self.inner = tk.Frame(self.frame, bg="lightyellow", bd=1, relief="solid")
        self.inner.pack(padx=1, pady=1)

        self.inner.bind("<Button-1>", self.prev_page)
        self.inner.bind("<Button-3>", self.next_page)

    def show(self, x, y, sessions):
        self.current_sessions = sessions
        self.current_page = 0
        self._render()
        self.frame.geometry(f"+{x}+{y}")
        self.frame.deiconify()

    def hide(self, event=None):
        self.frame.withdraw()

    def next_page(self, event=None):
        total_pages = (len(self.current_sessions) - 1) // SESSIONS_PER_PAGE + 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._render()

    def prev_page(self, event=None):
        if self.current_page > 0:
            self.current_page -= 1
            self._render()

    def _render(self):
        for widget in self.inner.winfo_children():
            widget.destroy()

        if not self.current_sessions:
            tk.Label(self.inner, text="세션 없음", font=("Consolas", 10), bg="lightyellow").pack(pady=5)
            return

        start = self.current_page * SESSIONS_PER_PAGE
        end = start + SESSIONS_PER_PAGE
        visible = self.current_sessions[start:end]

        for session in visible:
            try:
                st = session["start"][:5]
                et = session["end"][:5]
                duration = self._format_duration(session["start"], session["end"])
                row = tk.Frame(self.inner, bg="lightyellow")
                row.pack(anchor="w", padx=5, pady=1)
                tk.Label(row, text=f"{st} ~ {et}", width=14, anchor="w", bg="lightyellow", font=("Consolas", 9)).pack(side="left")
                tk.Label(row, text=f"({duration})", width=8, anchor="e", bg="lightyellow", font=("Consolas", 9)).pack(side="left")
            except:
                continue

        total_pages = (len(self.current_sessions) - 1) // SESSIONS_PER_PAGE + 1
        tk.Label(self.inner, text=f"{self.current_page + 1} / {total_pages} 페이지", font=("Consolas", 8), bg="lightyellow", fg="gray").pack(pady=(5, 2))

    def _format_duration(self, start, end):
        delta = datetime.strptime(end, "%H:%M:%S") - datetime.strptime(start, "%H:%M:%S")
        if delta.days < 0:
            delta += timedelta(days=1)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes}m"


def draw_log_to_canvas(canvas, log_data, today_str=None):
    canvas.delete("all")
    canvas.update_idletasks()

    tooltip = Tooltip(canvas)

    daily_hours = {}
    for date, sessions in log_data.items():
        total_seconds = 0
        for s in sessions:
            try:
                start = datetime.strptime(s["start"], "%H:%M:%S")
                end = datetime.strptime(s["end"], "%H:%M:%S")
                if end < start:
                    end += timedelta(days=1)
                total_seconds += (end - start).total_seconds()
            except:
                pass
        daily_hours[date] = round(total_seconds / 3600, 1)

    sorted_items = sorted(daily_hours.items(), key=lambda x: x[0])
    visible_width = canvas.winfo_width()
    left_margin = visible_width // 2 - SPACING * 2
    graph_width = max(len(sorted_items) * (BAR_WIDTH + SPACING) + left_margin * 2, visible_width)

    canvas.create_line(0, BASE_Y, graph_width, BASE_Y, fill="gray", width=1)
    canvas.configure(scrollregion=(0, 0, graph_width, BASE_Y + 100))

    today_index = len(sorted_items) - 1
    for i, (label_text, hours) in enumerate(sorted_items):
        if label_text == today_str:
            today_index = i
        x0 = i * (BAR_WIDTH + SPACING) + left_margin
        x1 = x0 + BAR_WIDTH
        bar_height = int((hours / 14) * MAX_HEIGHT)
        if bar_height < 2:
            bar_height = 2
        y0 = BASE_Y - bar_height
        y1 = BASE_Y

        day_sessions = log_data.get(label_text, [])

        bar_tag = f"bar-{label_text}"
        canvas.create_rectangle(x0, y0, x1, y1, fill="black", tags=(bar_tag,))

        trigger_tag = f"trigger-{label_text}"
        trigger_x0 = x0 - 10
        trigger_x1 = x1 + 10
        trigger_y0 = y0 - 10
        trigger_y1 = BASE_Y + 10
        rect_id = canvas.create_rectangle(trigger_x0, trigger_y0, trigger_x1, trigger_y1, fill="", outline="")
        canvas.itemconfig(rect_id, tags=(trigger_tag,))

        for tag in [trigger_tag, bar_tag]:
            canvas.tag_bind(tag, "<Enter>", lambda e, s=day_sessions: tooltip.show(e.x_root + 10, e.y_root + 10, s))
            canvas.tag_bind(tag, "<Leave>", tooltip.hide)
            canvas.tag_bind(tag, "<Button-1>", tooltip.prev_page)
            canvas.tag_bind(tag, "<Button-3>", tooltip.next_page)

        time_text_tag = f"time-text-{label_text}"
        canvas.create_text((x0 + x1) // 2, y0 - 12, text=f"{hours}h", font=("Arial", 13, "bold"), tags=(time_text_tag,))
        canvas.tag_bind(time_text_tag, "<Enter>", lambda e, s=day_sessions: tooltip.show(e.x_root + 10, e.y_root + 10, s))
        canvas.tag_bind(time_text_tag, "<Leave>", tooltip.hide)
        canvas.tag_bind(time_text_tag, "<Button-1>", tooltip.prev_page)
        canvas.tag_bind(time_text_tag, "<Button-3>", tooltip.next_page)

        label_color = "blue" if label_text == today_str else "black"
        date_text_tag = f"date-text-{label_text}"
        canvas.create_text((x0 + x1) // 2 - 15, BASE_Y + 18, text=label_text[5:], font=("Arial", 13), fill=label_color, angle=43, anchor="n", tags=(date_text_tag,))
        canvas.tag_bind(date_text_tag, "<Enter>", lambda e, s=day_sessions: tooltip.show(e.x_root + 10, e.y_root + 10, s))
        canvas.tag_bind(date_text_tag, "<Leave>", tooltip.hide)
        canvas.tag_bind(date_text_tag, "<Button-1>", tooltip.prev_page)
        canvas.tag_bind(date_text_tag, "<Button-3>", tooltip.next_page)

    return today_index, graph_width, left_margin
