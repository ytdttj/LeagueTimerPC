import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import math
import playsound
import webbrowser
from PIL import Image, ImageTk

SPELL_COOLDOWNS = {
    "未选择": 0,
    "闪现": 300,
    "传送": 300,
    "引燃": 180,
    "屏障": 180,
    "净化": 240,
    "虚弱": 240,
    "疾跑": 240,
    "治疗": 240,
    "惩戒": 90
}

SPELL_NAMES = list(SPELL_COOLDOWNS.keys())

COSMIC_INSIGHT_HASTE = 18
IONIAN_BOOTS_HASTE = 10

class LeagueTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeagueTimer")
        self.root.minsize(600, 400)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.frame_left = ttk.Frame(root, padding="10")
        self.frame_left.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_rowconfigure(1, weight=1)
        self.frame_left.grid_rowconfigure(2, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.frame_right = ttk.Frame(root, padding="10")
        self.frame_right.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(2, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)

        self.top_frame = RoleFrame(self.frame_left, "Top", "上路", self)
        self.top_frame.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)

        self.mid_frame = RoleFrame(self.frame_left, "Mid", "中路", self)
        self.mid_frame.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)

        self.sup_frame = RoleFrame(self.frame_left, "Sup", "辅助", self)
        self.sup_frame.grid(row=2, column=0, sticky="nsew", pady=5, padx=5)

        self.jug_frame = RoleFrame(self.frame_right, "Jug", "打野", self)
        self.jug_frame.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)

        self.bot_frame = RoleFrame(self.frame_right, "Bot", "下路", self)
        self.bot_frame.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)

        # Link Frame
        self.link_frame = ttk.Frame(self.frame_right)
        self.link_frame.grid(row=2, column=0, sticky="se", pady=10, padx=5)

        # 添加切换为悬浮窗按钮
        float_button = ttk.Button(self.link_frame, text="切换为悬浮窗", command=self.switch_to_mini)
        float_button.pack(side=tk.LEFT, padx=(0, 10))

        github_link = ttk.Label(self.link_frame, text="开源地址", foreground="blue", cursor="hand2")
        github_link.pack(side=tk.LEFT, padx=(0, 10))
        github_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/ytdttj/LeagueTimerPC"))

        weibo_link = ttk.Label(self.link_frame, text="@ytdttj", foreground="blue", cursor="hand2")
        weibo_link.pack(side=tk.LEFT)
        weibo_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://weibo.com/u/2265348910"))

    def calculate_cooldown(self, base_cd, has_insight, has_boots):
        if base_cd == 0:
            return 0
        
        total_haste = 0
        if has_insight:
            total_haste += COSMIC_INSIGHT_HASTE
        if has_boots:
            total_haste += IONIAN_BOOTS_HASTE
            
        final_cd = base_cd * (100 / (100 + total_haste))
        return math.floor(final_cd)
        
    def switch_to_mini(self):
        """销毁当前窗口并启动悬浮窗模式"""
        self.root.destroy()
        try:
            # 尝试直接导入并运行模块（适用于开发环境）
            import league_timer_mini
            import importlib
            importlib.reload(league_timer_mini)
            root = tk.Tk()
            app = league_timer_mini.LeagueTimerApp(root)
            root.mainloop()
        except ImportError:
            # 如果导入失败，尝试使用subprocess启动（适用于打包环境）
            import subprocess
            import os
            import sys
            # 获取当前执行文件的目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                base_dir = os.path.dirname(sys.executable)
                mini_path = os.path.join(base_dir, "league_timer_mini.py")
                subprocess.Popen([sys.executable, mini_path])
            else:
                # 如果是开发环境
                subprocess.Popen([sys.executable, "league_timer_mini.py"])

class RoleFrame(ttk.Frame):
    def __init__(self, parent, role_id, role_name, app_instance):
        super().__init__(parent, padding="5", relief="groove", borderwidth=2)
        self.role_id = role_id
        self.role_name = role_name
        self.app = app_instance
        self.timers = {}
        self.timer_jobs = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=0)
        self.grid_columnconfigure(5, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        role_label = ttk.Label(self, text=role_name, font=("Arial", 12, "bold"))
        role_label.grid(row=0, column=0, columnspan=6, pady=(0, 10), sticky="n")

        self.create_spell_row(1)
        self.create_spell_row(2)

    def create_spell_row(self, spell_index):
        row_num = spell_index

        combo_id = f"spell{self.role_id}{spell_index}"
        combo = ttk.Combobox(self, values=SPELL_NAMES, state="readonly", width=12, name=combo_id.lower())
        combo.set("未选择")
        combo.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda event, idx=spell_index: self.on_spell_selected(event, idx))
        setattr(self, f"combo{spell_index}", combo)

        button_id = f"start{self.role_id}{spell_index}"
        button = ttk.Button(self, text="开始计时", command=lambda idx=spell_index: self.start_timer(idx), name=button_id.lower())
        button.grid(row=row_num, column=2, padx=5, pady=2)
        setattr(self, f"button{spell_index}", button)

        timer_label_id = f"time{self.role_id}{spell_index}"
        timer_label = ttk.Label(self, text="--:--", font=("Arial", 10, "bold"), width=6, anchor="center", name=timer_label_id.lower())
        timer_label.grid(row=row_num, column=3, padx=5, pady=2, sticky="ew")
        setattr(self, f"timer_label{spell_index}", timer_label)

        insight_id = f"insight{self.role_id}{spell_index}"
        insight_var = tk.BooleanVar(name=f"insight_var_{self.role_id}{spell_index}".lower())
        insight_check = ttk.Checkbutton(self, text="星界洞悉", variable=insight_var, name=insight_id.lower())
        insight_check.grid(row=row_num, column=4, padx=5, pady=2)
        setattr(self, f"insight_var{spell_index}", insight_var)
        setattr(self, f"insight_check{spell_index}", insight_check)

        boots_id = f"boots{self.role_id}{spell_index}"
        boots_var = tk.BooleanVar(name=f"boots_var_{self.role_id}{spell_index}".lower())
        boots_check = ttk.Checkbutton(self, text="CD鞋", variable=boots_var, name=boots_id.lower())
        boots_check.grid(row=row_num, column=5, padx=5, pady=2)
        setattr(self, f"boots_var{spell_index}", boots_var)
        setattr(self, f"boots_check{spell_index}", boots_check)

    def on_spell_selected(self, event, selected_index):
        other_index = 3 - selected_index
        selected_combo = getattr(self, f"combo{selected_index}")
        other_combo = getattr(self, f"combo{other_index}")
        selected_spell = selected_combo.get()
        other_spell = other_combo.get()

        current_available_spells = [s for s in SPELL_NAMES if s == "未选择" or s != other_spell]
        selected_combo['values'] = current_available_spells
        if selected_spell != "未选择" and selected_spell == other_spell:
            selected_combo.set("未选择")

        other_available_spells = [s for s in SPELL_NAMES if s == "未选择" or s != selected_spell]
        other_combo['values'] = other_available_spells
        if other_spell != "未选择" and other_spell == selected_spell:
            other_combo.set("未选择")


    def start_timer(self, spell_index):
        timer_id = f"{self.role_id}_{spell_index}"
        if timer_id in self.timers:
            print(f"Timer {timer_id} already running.")
            return

        combo = getattr(self, f"combo{spell_index}")
        button = getattr(self, f"button{spell_index}")
        timer_label = getattr(self, f"timer_label{spell_index}")
        insight_var = getattr(self, f"insight_var{spell_index}")
        insight_check = getattr(self, f"insight_check{spell_index}")
        boots_var = getattr(self, f"boots_var{spell_index}")
        boots_check = getattr(self, f"boots_check{spell_index}")

        spell_name = combo.get()
        if spell_name == "未选择":
            messagebox.showwarning("未选择技能", "请先选择一个召唤师技能再开始计时。", parent=self.app.root)
            return

        base_cd = SPELL_COOLDOWNS.get(spell_name, 0)
        has_insight = insight_var.get()
        has_boots = boots_var.get()

        final_cd = self.app.calculate_cooldown(base_cd, has_insight, has_boots)

        if final_cd <= 0:
            timer_label.config(text="--:--", foreground="black")
            return

        combo.config(state="disabled")
        insight_check.config(state="disabled")
        button.config(state="disabled")
        boots_check.config(state="disabled")

        self.timers[timer_id] = final_cd
        timer_label.config(foreground="black") 
        self.update_timer(timer_id, spell_index)

    def update_timer(self, timer_id, spell_index):
        if timer_id not in self.timers:
            return 

        remaining_time = self.timers[timer_id]
        
        if remaining_time <= 0:
            self.timer_finished(timer_id, spell_index)
            return

        minutes = remaining_time // 60
        seconds = remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        try:
            timer_label = getattr(self, f"timer_label{spell_index}")
            if timer_label.winfo_exists():
                timer_label.config(text=time_str)
            else:
                print(f"Label widget for {timer_id} destroyed, stopping timer.")
                self.cancel_timer(timer_id)
                return
        except (tk.TclError, AttributeError) as e:
            print(f"Error updating label for {timer_id}: {e}. Widget might be destroyed.")
            self.cancel_timer(timer_id)
            return

        self.timers[timer_id] -= 1
        job_id = self.app.root.after(1000, lambda tid=timer_id, si=spell_index: self.update_timer(tid, si))
        self.timer_jobs[timer_id] = job_id

    def cancel_timer(self, timer_id):
        if timer_id in self.timer_jobs:
            try:
                self.app.root.after_cancel(self.timer_jobs[timer_id])
            except (ValueError, tk.TclError):
                pass
            del self.timer_jobs[timer_id]
        if timer_id in self.timers:
            del self.timers[timer_id]

    def timer_finished(self, timer_id, spell_index):
        if timer_id not in self.timers and timer_id not in self.timer_jobs:
            return
            
        self.cancel_timer(timer_id) 

        try:
            timer_label = getattr(self, f"timer_label{spell_index}")
            button = getattr(self, f"button{spell_index}")
            boots_check = getattr(self, f"boots_check{spell_index}")

            if timer_label.winfo_exists():
                timer_label.config(text="冷却完毕", foreground="red")
            if button.winfo_exists():
                button.config(state="normal")
            if boots_check.winfo_exists():
                boots_check.config(state="normal")

        except (tk.TclError, AttributeError) as e:
            print(f"Error accessing widgets for {timer_id} on finish: {e}")
            return

        try:
            playsound.playsound('notification_sound.mp3', block=False)
        except Exception as e:
            print(f"Error playing sound: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LeagueTimerApp(root)
    root.mainloop()