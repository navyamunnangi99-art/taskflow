"""
TASKFLOW — A colorful To-Do List desktop app
Python only: uses Tkinter (included with many standard Python installations).

Run:
    python taskflow.py

Tasks are saved locally to taskflow_tasks.json beside this script.
"""

import json
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

APP_TITLE = "TaskFlow"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskflow_tasks.json")

# ---------- Theme ----------
BG = "#F4F6FB"
CARD = "#FFFFFF"
TEXT = "#20243A"
MUTED = "#7D849B"
PURPLE = "#6C63FF"
PURPLE_DARK = "#554BE8"
PURPLE_PALE = "#EFEDFF"
GREEN = "#20A779"
GREEN_PALE = "#E4F8F0"
ORANGE = "#F39A3D"
ORANGE_PALE = "#FFF2E1"
RED = "#E35D6A"
BORDER = "#E8EAF2"
SIDEBAR = "#24243B"
SIDEBAR_MUTED = "#B8B8D0"
FONT = "Segoe UI"


class TaskFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow | Your daily planner")
        self.root.geometry("1120x760")
        self.root.minsize(900, 640)
        self.root.configure(bg=BG)

        self.tasks = self.load_tasks()
        self.active_filter = "All Tasks"
        self.active_category = "Personal"
        self.search_var = tk.StringVar()
        self.task_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Personal")
        self.priority_var = tk.StringVar(value="Medium")
        self.due_var = tk.StringVar(value="Today")
        self.status_text = tk.StringVar(value="Let's make today productive.")

        self.build_layout()
        self.render_tasks()
        self.search_var.trace_add("write", lambda *_: self.render_tasks())

    # ---------- Data ----------
    def load_tasks(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def save_tasks(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=2, ensure_ascii=False)
        except OSError as exc:
            messagebox.showerror("Couldn't save tasks", f"Task changes couldn't be saved.\n\n{exc}")

    # ---------- Reusable UI helpers ----------
    def label(self, parent, text, size=10, color=TEXT, bold=False, **kwargs):
        return tk.Label(
            parent, text=text, bg=kwargs.pop("bg", CARD), fg=color,
            font=(FONT, size, "bold" if bold else "normal"),
            **kwargs
        )

    def button(self, parent, text, command, bg=PURPLE, fg="white",
               active_bg=PURPLE_DARK, padx=14, pady=9, **kwargs):
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=active_bg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=(FONT, 10, "bold"), padx=padx, pady=pady,
            **kwargs
        )

    def card(self, parent, **kwargs):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1, bd=0, **kwargs)

    # ---------- Main layout ----------
    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=228)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(28, 34))
        mark = tk.Label(brand, text="✓", bg=PURPLE, fg="white",
                        font=(FONT, 17, "bold"), width=2, height=1)
        mark.pack(side="left", padx=(0, 10))
        tk.Label(brand, text="TaskFlow", bg=SIDEBAR, fg="white",
                 font=(FONT, 19, "bold")).pack(side="left", anchor="center")

        self.label(self.sidebar, "WORKSPACE", 9, SIDEBAR_MUTED, True,
                   bg=SIDEBAR).pack(anchor="w", padx=24, pady=(0, 12))

        self.nav_buttons = {}
        for title, symbol in [
            ("All Tasks", "▦"),
            ("Today", "☀"),
            ("Upcoming", "◷"),
            ("Completed", "✓"),
        ]:
            btn = tk.Button(
                self.sidebar, text=f"  {symbol}     {title}",
                command=lambda name=title: self.set_filter(name),
                anchor="w", bg=SIDEBAR, fg="white" if title == "All Tasks" else SIDEBAR_MUTED,
                activebackground="#363650", activeforeground="white",
                relief="flat", bd=0, cursor="hand2", padx=16, pady=12,
                font=(FONT, 10, "bold" if title == "All Tasks" else "normal")
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[title] = btn

        self.label(self.sidebar, "CATEGORIES", 9, SIDEBAR_MUTED, True,
                   bg=SIDEBAR).pack(anchor="w", padx=24, pady=(28, 12))

        for name, color in [("Personal", "#F5A65B"), ("College", "#7F8CFF"),
                            ("Work", "#42C9A5"), ("Other", "#E879A9")]:
            row = tk.Frame(self.sidebar, bg=SIDEBAR)
            row.pack(fill="x", padx=26, pady=7)
            tk.Label(row, text="●", fg=color, bg=SIDEBAR,
                     font=(FONT, 11)).pack(side="left")
            tk.Label(row, text=name, fg=SIDEBAR_MUTED, bg=SIDEBAR,
                     font=(FONT, 10)).pack(side="left", padx=10)

        bottom = tk.Frame(self.sidebar, bg="#2D2D47")
        bottom.pack(side="bottom", fill="x", padx=14, pady=16)
        tk.Label(bottom, text="SMALL STEPS, BIG WINS ✨", bg="#2D2D47",
                 fg="#D7D6F7", font=(FONT, 8, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(bottom, text="One task at a time.", bg="#2D2D47",
                 fg=SIDEBAR_MUTED, font=(FONT, 9)).pack(anchor="w", padx=12, pady=(0, 12))

        # Main content area
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        top = tk.Frame(self.main, bg=BG)
        top.grid(row=0, column=0, sticky="ew", padx=34, pady=(27, 16))
        top.grid_columnconfigure(0, weight=1)
        self.heading = tk.Label(top, text="Good day! 👋", bg=BG, fg=TEXT,
                                font=(FONT, 22, "bold"))
        self.heading.grid(row=0, column=0, sticky="w")
        date_text = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(top, text=date_text, bg=BG, fg=MUTED,
                 font=(FONT, 10)).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.button(top, "+  Add New Task", self.focus_new_task, padx=17, pady=11).grid(row=0, column=1, rowspan=2, sticky="e")

        # Summary cards
        stats = tk.Frame(self.main, bg=BG)
        stats.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 18))
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1, uniform="stat")
        self.stat_values = {}
        stat_info = [
            ("Total tasks", "total", PURPLE, PURPLE_PALE, "▦"),
            ("In progress", "pending", ORANGE, ORANGE_PALE, "◷"),
            ("Completed", "completed", GREEN, GREEN_PALE, "✓"),
        ]
        for i, (title, key, color, pale, symbol) in enumerate(stat_info):
            box = self.card(stats)
            box.grid(row=0, column=i, sticky="ew", padx=6, ipady=7)
            inner = tk.Frame(box, bg=CARD)
            inner.pack(fill="both", padx=15, pady=13)
            tk.Label(inner, text=symbol, bg=pale, fg=color,
                     font=(FONT, 15, "bold"), width=3, height=1).pack(side="left", padx=(0, 12))
            text_box = tk.Frame(inner, bg=CARD)
            text_box.pack(side="left", fill="x")
            tk.Label(text_box, text=title, bg=CARD, fg=MUTED,
                     font=(FONT, 9)).pack(anchor="w")
            value = tk.Label(text_box, text="0", bg=CARD, fg=TEXT,
                             font=(FONT, 20, "bold"))
            value.pack(anchor="w", pady=(2, 0))
            self.stat_values[key] = value

        # Progress card
        progress_card = self.card(self.main)
        progress_card.grid(row=2, column=0, sticky="ew", padx=34, pady=(0, 18))
        progress_inner = tk.Frame(progress_card, bg=CARD)
        progress_inner.pack(fill="x", padx=18, pady=14)
        progress_top = tk.Frame(progress_inner, bg=CARD)
        progress_top.pack(fill="x")
        tk.Label(progress_top, text="Daily progress", bg=CARD, fg=TEXT,
                 font=(FONT, 11, "bold")).pack(side="left")
        self.progress_label = tk.Label(progress_top, text="0% complete", bg=CARD,
                                        fg=PURPLE, font=(FONT, 9, "bold"))
        self.progress_label.pack(side="right")
        self.progress_track = tk.Canvas(progress_inner, height=9, bg="#ECECF5",
                                        highlightthickness=0, bd=0)
        self.progress_track.pack(fill="x", pady=(11, 3))

        # Task panel
        task_panel = self.card(self.main)
        task_panel.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 12))
        task_panel.grid_rowconfigure(2, weight=1)
        task_panel.grid_columnconfigure(0, weight=1)

        panel_head = tk.Frame(task_panel, bg=CARD)
        panel_head.grid(row=0, column=0, sticky="ew", padx=18, pady=(17, 12))
        panel_head.grid_columnconfigure(0, weight=1)
        self.task_heading = tk.Label(panel_head, text="Your tasks", bg=CARD, fg=TEXT,
                                     font=(FONT, 14, "bold"))
        self.task_heading.grid(row=0, column=0, sticky="w")
        search = tk.Entry(panel_head, textvariable=self.search_var, width=22,
                          bg="#F7F8FC", fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=(FONT, 10))
        search.grid(row=0, column=1, sticky="e", ipady=8, padx=(8, 0))
        search.insert(0, "")
        tk.Label(panel_head, text="⌕", bg="#F7F8FC", fg=MUTED,
                 font=(FONT, 13)).place(relx=1.0, rely=0.5, x=-12, y=0, anchor="e")

        # Add-task row
        add_row = tk.Frame(task_panel, bg="#FAFAFE")
        add_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        add_row.grid_columnconfigure(0, weight=1)
        self.task_entry = tk.Entry(add_row, textvariable=self.task_var, bg="#FAFAFE",
                                   fg=TEXT, insertbackground=TEXT, relief="flat",
                                   font=(FONT, 10))
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=11)
        self.task_entry.insert(0, "")
        self.task_entry.bind("<Return>", lambda _event: self.add_task())
        tk.Label(add_row, text="New task", bg="#FAFAFE", fg=MUTED,
                 font=(FONT, 9)).grid(row=0, column=0, sticky="w", padx=10)
        # Input overlay label is hidden when typing, and restored when empty.
        self.task_entry.bind("<FocusIn>", lambda _e: self.hide_placeholder())
        self.task_entry.bind("<FocusOut>", lambda _e: self.show_placeholder())
        self.placeholder_active = True
        self.show_placeholder()

        tk.OptionMenu(add_row, self.category_var, "Personal", "College", "Work", "Other").grid(
            row=0, column=1, padx=4, pady=5)
        tk.OptionMenu(add_row, self.priority_var, "Low", "Medium", "High").grid(
            row=0, column=2, padx=4, pady=5)
        self.button(add_row, "Add task", self.add_task, padx=12, pady=8).grid(
            row=0, column=3, padx=(5, 8), pady=5)

        self.list_canvas = tk.Canvas(task_panel, bg=CARD, highlightthickness=0, bd=0)
        self.list_scrollbar = tk.Scrollbar(task_panel, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        self.list_canvas.grid(row=2, column=0, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.list_scrollbar.grid(row=2, column=1, sticky="ns", pady=(0, 8), padx=(0, 8))
        self.task_list_frame = tk.Frame(self.list_canvas, bg=CARD)
        self.canvas_window = self.list_canvas.create_window((0, 0), window=self.task_list_frame, anchor="nw")
        self.task_list_frame.bind("<Configure>", self.update_scroll_region)
        self.list_canvas.bind("<Configure>", self.resize_task_list)

        footer = tk.Label(self.main, textvariable=self.status_text, bg=BG, fg=MUTED,
                          font=(FONT, 9))
        footer.grid(row=4, column=0, sticky="w", padx=36, pady=(0, 8))

    def hide_placeholder(self):
        if getattr(self, "placeholder_active", False):
            self.task_entry.delete(0, "end")
            self.placeholder_active = False

    def show_placeholder(self):
        if not self.task_var.get().strip() and not self.task_entry.focus_get():
            self.placeholder_active = True
            self.task_entry.delete(0, "end")
            self.task_entry.insert(0, "What do you need to get done?")
            self.task_entry.config(fg=MUTED)

    def update_scroll_region(self, _event=None):
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

    def resize_task_list(self, event):
        self.list_canvas.itemconfigure(self.canvas_window, width=event.width)

    def focus_new_task(self):
        self.task_entry.focus_set()
        self.hide_placeholder()

    # ---------- Task actions ----------
    def add_task(self):
        name = self.task_var.get().strip()
        if not name or name == "What do you need to get done?":
            self.status_text.set("Type a task first, then click Add task.")
            self.focus_new_task()
            return
        self.tasks.append({
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "name": name,
            "category": self.category_var.get(),
            "priority": self.priority_var.get(),
            "due": self.due_var.get(),
            "completed": False,
            "created": datetime.now().isoformat(timespec="seconds")
        })
        self.save_tasks()
        self.task_var.set("")
        self.task_entry.delete(0, "end")
        self.task_entry.config(fg=TEXT)
        self.placeholder_active = False
        self.render_tasks()
        self.status_text.set("Task added. You're doing great!")
        self.task_entry.focus_set()

    def toggle_task(self, task):
        task["completed"] = not task.get("completed", False)
        self.save_tasks()
        self.render_tasks()
        self.status_text.set("Nice work — task completed!" if task["completed"] else "Task moved back to pending.")

    def delete_task(self, task):
        if messagebox.askyesno("Delete task", f"Delete this task?\n\n{task['name']}"):
            self.tasks = [item for item in self.tasks if item.get("id") != task.get("id")]
            self.save_tasks()
            self.render_tasks()
            self.status_text.set("Task deleted.")

    def set_filter(self, name):
        self.active_filter = name
        for title, btn in self.nav_buttons.items():
            selected = title == name
            btn.config(bg="#454563" if selected else SIDEBAR,
                       fg="white" if selected else SIDEBAR_MUTED,
                       font=(FONT, 10, "bold" if selected else "normal"))
        headings = {
            "All Tasks": "Your tasks",
            "Today": "Today's tasks",
            "Upcoming": "Upcoming tasks",
            "Completed": "Completed tasks"
        }
        self.task_heading.config(text=headings.get(name, "Your tasks"))
        self.render_tasks()

    def filtered_tasks(self):
        query = self.search_var.get().strip().lower()
        visible = []
        today = datetime.now().date()
        for task in self.tasks:
            completed = task.get("completed", False)
            if self.active_filter == "Completed" and not completed:
                continue
            if self.active_filter in ("Today", "Upcoming") and completed:
                continue
            # This simple app uses a readable due label (Today); tasks marked Today
            # appear in Today. Other labels appear in Upcoming.
            if self.active_filter == "Today" and task.get("due", "Today") != "Today":
                continue
            if self.active_filter == "Upcoming" and task.get("due", "Today") == "Today":
                continue
            if query and query not in task.get("name", "").lower() and query not in task.get("category", "").lower():
                continue
            visible.append(task)
        return visible

    def render_tasks(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.get("completed", False))
        pending = total - completed
        self.stat_values["total"].config(text=str(total))
        self.stat_values["pending"].config(text=str(pending))
        self.stat_values["completed"].config(text=str(completed))
        percent = round(completed / total * 100) if total else 0
        self.progress_label.config(text=f"{percent}% complete")
        self.progress_track.delete("all")
        width = max(self.progress_track.winfo_width(), 200)
        self.progress_track.create_rectangle(0, 0, width, 9, fill="#ECECF5", outline="")
        self.progress_track.create_rectangle(0, 0, width * percent / 100, 9,
                                             fill=PURPLE, outline="")
        self.progress_track.bind("<Configure>", self.redraw_progress)

        visible = self.filtered_tasks()
        if not visible:
            empty = tk.Frame(self.task_list_frame, bg=CARD)
            empty.pack(fill="x", padx=20, pady=35)
            tk.Label(empty, text="✦", bg=CARD, fg=PURPLE,
                     font=(FONT, 28, "bold")).pack()
            tk.Label(empty, text="All clear!", bg=CARD, fg=TEXT,
                     font=(FONT, 14, "bold")).pack(pady=(8, 3))
            tk.Label(empty, text="Add a task above and make your day count.",
                     bg=CARD, fg=MUTED, font=(FONT, 9)).pack()
            return

        for task in visible:
            self.make_task_row(task)

    def redraw_progress(self, event=None):
        self.progress_track.delete("all")
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.get("completed", False))
        percent = completed / total if total else 0
        width = event.width if event else self.progress_track.winfo_width()
        self.progress_track.create_rectangle(0, 0, width, 9, fill="#ECECF5", outline="")
        self.progress_track.create_rectangle(0, 0, width * percent, 9, fill=PURPLE, outline="")

    def make_task_row(self, task):
        row = tk.Frame(self.task_list_frame, bg=CARD, highlightbackground=BORDER,
                       highlightthickness=1)
        row.pack(fill="x", padx=10, pady=4)
        row.grid_columnconfigure(1, weight=1)

        done = task.get("completed", False)
        check_bg = GREEN if done else CARD
        check_fg = "white" if done else PURPLE
        check = tk.Button(row, text="✓" if done else "", command=lambda t=task: self.toggle_task(t),
                          bg=check_bg, fg=check_fg, activebackground=GREEN_PALE,
                          relief="flat", bd=1, highlightbackground=PURPLE,
                          highlightthickness=1, width=2, cursor="hand2",
                          font=(FONT, 10, "bold"))
        check.grid(row=0, column=0, rowspan=2, padx=(12, 12), pady=12)

        name_color = MUTED if done else TEXT
        name_font = (FONT, 10, "normal")
        title = tk.Label(row, text=task.get("name", "Untitled task"), bg=CARD,
                         fg=name_color, font=name_font, anchor="w")
        title.grid(row=0, column=1, sticky="ew", pady=(11, 2))
        if done:
            title.config(font=(FONT, 10, "overstrike"))

        category = task.get("category", "Personal")
        priority = task.get("priority", "Medium")
       
        cat_color = {"Personal": PURPLE, "College": "#6171E8", "Work": GREEN, "Other": "#D65F99"}.get(category, PURPLE)
        meta = tk.Frame(row, bg=CARD)
        meta.grid(row=1, column=1, sticky="w", pady=(0, 10))
        tk.Label(meta, text=f" {category} ", bg=PURPLE_PALE if category == "Personal" else "#F0F1FF",
                 fg=cat_color, font=(FONT, 8, "bold"), padx=3, pady=2).pack(side="left", padx=(0, 6))
        priority_color = RED if priority == "High" else ORANGE if priority == "Medium" else GREEN
        tk.Label(meta, text=f"● {priority}", bg=CARD, fg=priority_color,
                 font=(FONT, 8, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(meta, text=f"Due: {task.get('due', 'Today')}", bg=CARD, fg=MUTED,
                 font=(FONT, 8)).pack(side="left")

        self.button(row, "Delete", lambda t=task: self.delete_task(t),
                    bg="#FFF0F1", fg=RED, active_bg="#FFE0E3",
                    padx=9, pady=6).grid(row=0, column=2, rowspan=2, padx=12)

    # ---------- App close ----------
    def on_close(self):
        self.save_tasks()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TaskFlowApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()