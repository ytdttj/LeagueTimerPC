import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import math
import playsound
import webbrowser

SPELL_COOLDOWNS = {
    "未选择": 0,
    "闪": 300,  # 闪现
    "T": 300,   # 传送
    "火": 180,  # 引燃
    "盾": 180,  # 屏障
    "净": 240,  # 净化
    "虚": 240,  # 虚弱
    "疾": 240,  # 疾跑
    "治": 240,  # 治疗
    "惩": 90    # 惩戒
}

SPELL_NAMES = list(SPELL_COOLDOWNS.keys())

COSMIC_INSIGHT_HASTE = 18
IONIAN_BOOTS_HASTE = 10


class LeagueTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeagueTimer")
        self.root.geometry("180x450")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        # 设置点击穿透 - 将所有组件背景设为系统透明色
        self.root.wm_attributes('-transparentcolor', 'white')
        # 设置背景颜色为白色
        self.root.configure(bg='white')
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # 拖动区域行
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(5, weight=1)
        
        # 添加半透明拖动区域
        self.drag_frame = tk.Frame(root, height=20, bg='#AAAAAA')
        self.drag_frame.grid(row=0, column=0, sticky="ew")
        # 使用灰色背景模拟半透明效果，因为Frame没有alpha属性
        
        # 添加关闭和锁定按钮
        close_button = ttk.Button(self.drag_frame, text="X", command=self.root.destroy, width=2)
        close_button.pack(side=tk.RIGHT)
        self.lock_button = ttk.Button(self.drag_frame, text="🔓", command=self.toggle_lock, width=2)
        self.lock_button.pack(side=tk.RIGHT, padx=2)
        
        # 只添加上单标签到拖动区域
        self.top_label = ttk.Label(self.drag_frame, text="上路", background='#AAAAAA', font=("Arial", 9, "bold"))
        self.top_label.pack(side=tk.LEFT, padx=2)
        
        # 添加角色框架
        self.top_frame = RoleFrame(root, "Top", "上路", self)
        self.top_frame.grid(row=1, column=0, sticky="nsew", pady=2, padx=2)
        self.jug_frame = RoleFrame(root, "Jug", "打野", self)
        self.jug_frame.grid(row=2, column=0, sticky="nsew", pady=2, padx=2)
        self.mid_frame = RoleFrame(root, "Mid", "中路", self)
        self.mid_frame.grid(row=3, column=0, sticky="nsew", pady=2, padx=2)
        self.bot_frame = RoleFrame(root, "Bot", "下路", self)
        self.bot_frame.grid(row=4, column=0, sticky="nsew", pady=2, padx=2)
        self.sup_frame = RoleFrame(root, "Sup", "辅助", self)
        self.sup_frame.grid(row=5, column=0, sticky="nsew", pady=2, padx=2)
        
        self._offset_x = 0
        self._offset_y = 0
        self.is_locked = False
        self.drag_frame.bind('<Button-1>', self.click_window)
        self.drag_frame.bind('<B1-Motion>', self.drag_window)

    def click_window(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def drag_window(self, event):
        if not self.is_locked:
            x = self.root.winfo_pointerx() - self._offset_x
            y = self.root.winfo_pointery() - self._offset_y
            self.root.geometry(f'+{x}+{y}')
            
    def toggle_lock(self):
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.lock_button.config(text="🔒")
        else:
            self.lock_button.config(text="🔓")

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


class RoleFrame(tk.Frame):
    def __init__(self, parent, role_id, role_name, app_instance):
        super().__init__(parent, padx=2, pady=2, relief="flat", borderwidth=1, bg='white')
        self.role_id = role_id
        self.role_name = role_name
        self.app = app_instance
        self.timers = {}
        self.timer_jobs = {}
        # 确保所有子组件也使用白色背景以实现点击穿透
        self.configure(bg='white')
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=0)
        self.grid_columnconfigure(5, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        # 只有非上路角色才显示角色标签
        if role_id != "Top":
            role_label = ttk.Label(self, text=role_name, font=("Arial", 9, "bold"), background='white')
            role_label.grid(row=0, column=0, columnspan=6, pady=(0, 1), sticky="n")
        self.create_spell_row(1)
        self.create_spell_row(2)

    def create_spell_row(self, spell_index):
        row_num = spell_index
        combo_id = f"spell{self.role_id}{spell_index}"
        combo = ttk.Combobox(self, values=SPELL_NAMES, state="readonly", width=4, font=("Arial", 8), name=combo_id.lower())
        combo.set("未选择")
        combo.grid(row=row_num, column=1, padx=2, pady=1, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda event, idx=spell_index: self.on_spell_selected(event, idx))
        setattr(self, f"combo{spell_index}", combo)
        button_id = f"start{self.role_id}{spell_index}"
        button = ttk.Button(self, text="开", width=3, command=lambda idx=spell_index: self.start_timer(idx), name=button_id.lower())
        button.grid(row=row_num, column=2, padx=2, pady=1)
        setattr(self, f"button{spell_index}", button)
        timer_label_id = f"time{self.role_id}{spell_index}"
        timer_label = ttk.Label(self, text="--:--", font=("Arial", 9, "bold"), width=6, anchor="center", name=timer_label_id.lower(), background='white')
        timer_label.grid(row=row_num, column=3, padx=2, pady=1, sticky="ew")
        setattr(self, f"timer_label{spell_index}", timer_label)
        insight_id = f"insight{self.role_id}{spell_index}"
        insight_var = tk.BooleanVar(name=f"insight_var_{self.role_id}{spell_index}".lower())
        insight_check = ttk.Checkbutton(self, text="", variable=insight_var, name=insight_id.lower())
        insight_check.grid(row=row_num, column=4, padx=2, pady=1)
        setattr(self, f"insight_var{spell_index}", insight_var)
        setattr(self, f"insight_check{spell_index}", insight_check)
        boots_id = f"boots{self.role_id}{spell_index}"
        boots_var = tk.BooleanVar(name=f"boots_var_{self.role_id}{spell_index}".lower())
        boots_check = ttk.Checkbutton(self, text="", variable=boots_var, name=boots_id.lower())
        boots_check.grid(row=row_num, column=5, padx=2, pady=1)
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
        timer_label = getattr(self, f"timer_label{spell_index}")
        if timer_label.winfo_exists():
            timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.timers[timer_id] -= 1
        self.timer_jobs[timer_id] = self.app.root.after(1000, self.update_timer, timer_id, spell_index)

    def timer_finished(self, timer_id, spell_index):
        print(f"Timer {timer_id} finished.")
        try:
            playsound.playsound('notification_sound.mp3', block=False)
        except Exception as e:
            print(f"Error playing sound: {e}")
        timer_label = getattr(self, f"timer_label{spell_index}")
        button = getattr(self, f"button{spell_index}")
        combo = getattr(self, f"combo{spell_index}")
        insight_check = getattr(self, f"insight_check{spell_index}")
        boots_check = getattr(self, f"boots_check{spell_index}")
        if timer_label.winfo_exists():
            timer_label.config(text="完毕", foreground="red")
        if button.winfo_exists():
            button.config(state="normal")
        # 技能选择框和星界洞悉勾选框保持禁用状态
        # 只有按钮和CD鞋勾选框恢复可用状态
        if boots_check.winfo_exists():
            boots_check.config(state="normal")
        if timer_id in self.timers:
            del self.timers[timer_id]
        if timer_id in self.timer_jobs:
            self.app.root.after_cancel(self.timer_jobs[timer_id])
            del self.timer_jobs[timer_id]


if __name__ == "__main__":
    root = tk.Tk()
    app = LeagueTimerApp(root)
    root.mainloop()