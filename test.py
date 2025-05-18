import tkinter as tk
from tkinter import simpledialog, messagebox

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro ve Yapılacaklar")
        self.root.geometry("400x680")
        self.root.configure(bg="#fdf6e3")

        # Süreler (test için saniye)
        self.pomodoro_duration = 25
        self.short_break = 5
        self.long_break = 10

        self.pomodoro_count = 0
        self.timer_running = False
        self.current_time = self.pomodoro_duration
        self.mode = "work"
        self.tasks = []

        self.create_widgets()

    def create_widgets(self):
        # MOD SEKMELERİ
        self.mode_frame = tk.Frame(self.root, bg="#fdf6e3")
        self.mode_frame.pack(pady=(15, 0))

        self.mode_labels = {
            "work": tk.Label(self.mode_frame, text="Pomodoro", font=("Segoe UI", 12, "bold"), bg="#fdf6e3"),
            "short_break": tk.Label(self.mode_frame, text="Kısa Mola", font=("Segoe UI", 12), bg="#fdf6e3"),
            "long_break": tk.Label(self.mode_frame, text="Uzun Mola", font=("Segoe UI", 12), bg="#fdf6e3")
        }

        for label in self.mode_labels.values():
            label.pack(side="left", padx=20)

        self.underline_frame = tk.Frame(self.mode_frame, height=3, bg="#e63946")
        self.update_mode_ui()

        # ANA KUTU
        self.main_card = tk.Frame(self.root, bg="#fff4e6", bd=1, relief="groove", highlightbackground="#e0cfc0", highlightthickness=1)
        self.main_card.pack(padx=20, pady=20, fill="both", expand=True)

        # ZAMANLAYICI
        self.timer_label = tk.Label(self.main_card, text=self.format_time(self.current_time),
                                    font=("Segoe UI", 42, "bold"), fg="#1d3557", bg="#fff4e6")
        self.timer_label.pack(pady=(15, 5))

        # OVAL CANVAS BUTON
        self.button_canvas = tk.Canvas(self.main_card, width=180, height=50, bg="#fff4e6", highlightthickness=0)
        self.button_canvas.pack(pady=10)

        self.oval_id = self.button_canvas.create_oval(0, 0, 180, 50, fill="#e63946", outline="")
        self.button_text = self.button_canvas.create_text(90, 25, text="Başlat", fill="white", font=("Segoe UI", 14, "bold"))

        self.button_canvas.tag_bind(self.oval_id, "<Button-1>", self.toggle_timer_event)
        self.button_canvas.tag_bind(self.button_text, "<Button-1>", self.toggle_timer_event)

        # AKTİF GÖREV
        self.active_task_label = tk.Label(self.main_card, text="Aktif Görev: -", font=("Segoe UI", 12, "bold"),
                                          bg="#fff4e6", fg="#1d3557", anchor="w")
        self.active_task_label.pack(fill="x", padx=20, pady=(10, 10))

        # GÖREV BAŞLIĞI
        self.todo_label = tk.Label(self.main_card, text="Yapılacaklar", font=("Segoe UI", 14, "bold"),
                                   bg="#fff4e6", fg="#1d3557", anchor="w")
        self.todo_label.pack(fill="x", padx=20)

        # GÖREVLER LİSTESİ
        self.canvas = tk.Canvas(self.main_card, bg="#fff4e6", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=(5, 0))

        # + EKLE BUTONU
        self.add_task_button = tk.Button(
            self.main_card, text="+  Ekle", command=self.add_task_popup,
            bg="#fff4e6", fg="#1d3557", font=("Segoe UI", 12, "bold"),
            relief="flat", anchor="w", padx=10, cursor="hand2"
        )
        self.add_task_button.pack(anchor="w", padx=20, pady=(5, 15))

    def toggle_timer_event(self, event=None):
        self.toggle_timer()
        new_text = "Durdur" if self.timer_running else "Başlat"
        self.button_canvas.itemconfig(self.button_text, text=new_text)

    def update_mode_ui(self):
        for mode, label in self.mode_labels.items():
            if mode == self.mode:
                label.config(fg="#e63946", font=("Segoe UI", 12, "bold"))
                self.underline_frame.place(in_=label, relx=0, rely=1.0, relwidth=1.0)
            else:
                label.config(fg="#1d3557", font=("Segoe UI", 12))

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def update_timer(self):
        if self.timer_running and self.current_time > 0:
            self.current_time -= 1
            self.timer_label.config(text=self.format_time(self.current_time))
            self.root.after(1000, self.update_timer)
        elif self.timer_running and self.current_time == 0:
            self.timer_running = False
            self.button_canvas.itemconfig(self.button_text, text="Başlat")
            self.switch_mode_after_timeout()

    def switch_mode_after_timeout(self):
        if self.mode == "work":
            self.pomodoro_count += 1
            if self.pomodoro_count % 4 == 0:
                self.mode = "long_break"
                self.current_time = self.long_break
                messagebox.showinfo("Mola", "Uzun mola zamanı!")
            else:
                self.mode = "short_break"
                self.current_time = self.short_break
                messagebox.showinfo("Mola", "Kısa mola zamanı!")
        else:
            self.mode = "work"
            self.current_time = self.pomodoro_duration
            messagebox.showinfo("Odaklan!", "Odaklanma zamanı!")

        self.update_mode_ui()
        self.timer_label.config(text=self.format_time(self.current_time))

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()
        else:
            self.timer_running = False

    def add_task_popup(self):
        task_text = simpledialog.askstring("Yeni Görev", "Görev nedir?")
        if task_text:
            self.add_task(task_text)

    def add_task(self, text):
        var = tk.BooleanVar()
        self.tasks.append((var, text, False))
        self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

        updated = []
        for (var, text, _) in self.tasks:
            completed = var.get()
            updated.append((var, text, completed))

        updated.sort(key=lambda x: not x[2])
        self.tasks = updated

        for idx, (var, text, _) in enumerate(self.tasks):
            row = tk.Frame(self.canvas, bg="#fff4e6")
            row.pack(anchor="w", fill="x", pady=5)

            cb = tk.Checkbutton(
                row,
                variable=var,
                command=lambda v=var, t=text: [self.refresh_tasks()],
                bg="#fff4e6",
                activebackground="#fff4e6",
                selectcolor="#e0f0ff",
                fg="#1d3557"
            )
            cb.pack(side="left", padx=(0, 8))

            lbl = tk.Label(
                row,
                text=text,
                font=("Segoe UI", 13, "bold" if not var.get() else "overstrike"),
                fg="#6c757d" if var.get() else "#1d3557",
                bg="#fff4e6"
            )
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, t=text: self.set_active_task(t))

    def set_active_task(self, task_text):
        self.active_task_label.config(text=f"Aktif Görev:  {task_text}")

# Uygulama başlat
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
