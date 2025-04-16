import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import math
import playsound # For sound playback

# Summoner spell base cooldowns (in seconds)
SPELL_COOLDOWNS = {
    "未选择": 0,
    "闪现": 300,
    "传送": 300,
    "引燃": 180,
    "屏障": 180,
    "净化": 210,
    "虚弱": 210,
    "疾跑": 210,
    "治疗": 240,
    "惩戒": 90
}

SPELL_NAMES = list(SPELL_COOLDOWNS.keys())

# Summoner Haste values
COSMIC_INSIGHT_HASTE = 18
IONIAN_BOOTS_HASTE = 12

class LeagueTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeagueTimer")
        self.root.minsize(600, 400) # Set a minimum size

        # Configure grid layout to be responsive
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # --- Create Frames for Layout --- 
        # Left Column
        self.frame_left = ttk.Frame(root, padding="10")
        self.frame_left.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_rowconfigure(1, weight=1)
        self.frame_left.grid_rowconfigure(2, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)

        # Right Column
        self.frame_right = ttk.Frame(root, padding="10")
        self.frame_right.grid(row=0, column=1, rowspan=2, sticky="nsew") # Only 2 rows needed here
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)

        # --- Create Role Frames --- 
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

    def calculate_cooldown(self, base_cd, has_insight, has_boots):
        """Calculates the final cooldown based on haste."""
        if base_cd == 0:
            return 0
        
        total_haste = 0
        if has_insight:
            total_haste += COSMIC_INSIGHT_HASTE
        if has_boots:
            total_haste += IONIAN_BOOTS_HASTE
            
        final_cd = base_cd * (100 / (100 + total_haste))
        return math.floor(final_cd) # Return integer part

class RoleFrame(ttk.Frame):
    def __init__(self, parent, role_id, role_name, app_instance):
        super().__init__(parent, padding="5", relief="groove", borderwidth=2)
        self.role_id = role_id
        self.role_name = role_name
        self.app = app_instance # Reference to the main app
        self.timers = {} # Dictionary to store active timer remaining seconds {timer_id: seconds}
        self.timer_jobs = {} # Dictionary to store after job IDs {timer_id: job_id}

        # Configure internal grid weights for responsiveness
        self.grid_columnconfigure(0, weight=0) # Role Label (spans multiple)
        self.grid_columnconfigure(1, weight=2) # Combobox
        self.grid_columnconfigure(2, weight=0) # Button
        self.grid_columnconfigure(3, weight=1) # Timer Label
        self.grid_columnconfigure(4, weight=0) # Insight Checkbox
        self.grid_columnconfigure(5, weight=0) # Boots Checkbox
        self.grid_rowconfigure(1, weight=1) # Spell Row 1
        self.grid_rowconfigure(2, weight=1) # Spell Row 2

        # Role Label
        role_label = ttk.Label(self, text=role_name, font=("Arial", 12, "bold"))
        # Place it above the spell rows, centered horizontally
        role_label.grid(row=0, column=0, columnspan=6, pady=(0, 10), sticky="n") 

        # Spell 1 Controls
        self.create_spell_row(1)
        # Spell 2 Controls
        self.create_spell_row(2)

    def create_spell_row(self, spell_index):
        """Creates the controls for a single spell row."""
        row_num = spell_index # Use spell_index directly for row number (1 or 2)

        # Combobox (Spinner)
        combo_id = f"spell{self.role_id}{spell_index}"
        # Make combobox slightly wider and add name attribute
        combo = ttk.Combobox(self, values=SPELL_NAMES, state="readonly", width=12, name=combo_id.lower()) # Use lowercase name for consistency
        combo.set("未选择")
        combo.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda event, idx=spell_index: self.on_spell_selected(event, idx))
        setattr(self, f"combo{spell_index}", combo)

        # Start Button
        button_id = f"start{self.role_id}{spell_index}"
        button = ttk.Button(self, text="开始计时", command=lambda idx=spell_index: self.start_timer(idx), name=button_id.lower())
        button.grid(row=row_num, column=2, padx=5, pady=2)
        setattr(self, f"button{spell_index}", button)

        # Timer Label (TextView)
        timer_label_id = f"time{self.role_id}{spell_index}"
        # Use a slightly larger font, ensure it's bold, add name attribute
        timer_label = ttk.Label(self, text="--:--", font=("Arial", 10, "bold"), width=6, anchor="center", name=timer_label_id.lower())
        timer_label.grid(row=row_num, column=3, padx=5, pady=2, sticky="ew")
        setattr(self, f"timer_label{spell_index}", timer_label)

        # Cosmic Insight Checkbox
        insight_id = f"insight{self.role_id}{spell_index}"
        # Add name attribute to var and checkbutton
        insight_var = tk.BooleanVar(name=f"insight_var_{self.role_id}{spell_index}".lower())
        insight_check = ttk.Checkbutton(self, text="星界洞悉", variable=insight_var, name=insight_id.lower())
        insight_check.grid(row=row_num, column=4, padx=5, pady=2)
        setattr(self, f"insight_var{spell_index}", insight_var)
        setattr(self, f"insight_check{spell_index}", insight_check)

        # CD Boots Checkbox
        boots_id = f"boots{self.role_id}{spell_index}"
        # Add name attribute to var and checkbutton
        boots_var = tk.BooleanVar(name=f"boots_var_{self.role_id}{spell_index}".lower())
        boots_check = ttk.Checkbutton(self, text="CD鞋", variable=boots_var, name=boots_id.lower())
        boots_check.grid(row=row_num, column=5, padx=5, pady=2)
        setattr(self, f"boots_var{spell_index}", boots_var)
        setattr(self, f"boots_check{spell_index}", boots_check)

    def on_spell_selected(self, event, selected_index):
        """Handles spell selection to update the other combobox."""
        other_index = 3 - selected_index # Gets 1 if 2, gets 2 if 1
        selected_combo = getattr(self, f"combo{selected_index}")
        other_combo = getattr(self, f"combo{other_index}")
        selected_spell = selected_combo.get()
        other_spell = other_combo.get()

        # Filter available spells for the current combobox
        # Exclude '未选择' from being removed
        current_available_spells = [s for s in SPELL_NAMES if s == "未选择" or s != other_spell]
        selected_combo['values'] = current_available_spells
        # If the current selection became invalid (e.g., other box selected it)
        if selected_spell != "未选择" and selected_spell == other_spell:
             selected_combo.set("未选择")

        # Filter available spells for the other combobox
        # Exclude '未选择' from being removed
        other_available_spells = [s for s in SPELL_NAMES if s == "未选择" or s != selected_spell]
        other_combo['values'] = other_available_spells
        # If the other selection became invalid
        if other_spell != "未选择" and other_spell == selected_spell:
            other_combo.set("未选择")


    def start_timer(self, spell_index):
        """Starts the countdown timer for the selected spell."""
        timer_id = f"{self.role_id}_{spell_index}"
        # If a timer is already running for this slot, do nothing
        if timer_id in self.timers:
            print(f"Timer {timer_id} already running.") # Optional: for debugging
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
            # This case handles '未选择' if it somehow gets past the check
            timer_label.config(text="--:--", foreground="black")
            return

        # Disable controls as per requirements
        combo.config(state="disabled")
        insight_check.config(state="disabled")
        button.config(state="disabled")
        boots_check.config(state="disabled")

        # Store remaining time and start countdown
        self.timers[timer_id] = final_cd
        # Reset label style before starting
        timer_label.config(foreground="black") 
        self.update_timer(timer_id, spell_index)

    def update_timer(self, timer_id, spell_index):
        """Recursive function to update the timer label every second."""
        if timer_id not in self.timers:
             # Timer was cancelled or finished elsewhere
            return 

        remaining_time = self.timers[timer_id]
        
        if remaining_time <= 0:
            # Ensure timer_finished is called exactly once
            self.timer_finished(timer_id, spell_index)
            return

        minutes = remaining_time // 60
        seconds = remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        try:
            timer_label = getattr(self, f"timer_label{spell_index}")
            # Check if widget exists before configuring
            if timer_label.winfo_exists():
                timer_label.config(text=time_str)
            else:
                print(f"Label widget for {timer_id} destroyed, stopping timer.")
                self.cancel_timer(timer_id)
                return
        except (tk.TclError, AttributeError) as e: # Handle case where widget might be destroyed or attr missing
            print(f"Error updating label for {timer_id}: {e}. Widget might be destroyed.")
            self.cancel_timer(timer_id)
            return

        self.timers[timer_id] -= 1
        # Schedule next update after 1000ms (1 second) and store job ID
        # Ensure lambda captures current timer_id and spell_index
        job_id = self.app.root.after(1000, lambda tid=timer_id, si=spell_index: self.update_timer(tid, si))
        self.timer_jobs[timer_id] = job_id

    def cancel_timer(self, timer_id):
        """Safely cancels a timer and its associated job."""
        if timer_id in self.timer_jobs:
            try:
                self.app.root.after_cancel(self.timer_jobs[timer_id])
            except (ValueError, tk.TclError):
                pass # Job might have already run or root destroyed
            del self.timer_jobs[timer_id]
        if timer_id in self.timers:
            del self.timers[timer_id]

    def timer_finished(self, timer_id, spell_index):
        """Handles actions when a timer completes."""
        # Prevent multiple calls for the same finished timer
        if timer_id not in self.timers and timer_id not in self.timer_jobs:
            return
            
        # Clean up timer data first
        self.cancel_timer(timer_id) 

        try:
            timer_label = getattr(self, f"timer_label{spell_index}")
            button = getattr(self, f"button{spell_index}")
            boots_check = getattr(self, f"boots_check{spell_index}")
            # Note: Combo and Insight Check remain disabled as per requirement

            # Check if widgets exist before configuring
            if timer_label.winfo_exists():
                timer_label.config(text="冷却完毕", foreground="red")
            if button.winfo_exists():
                button.config(state="normal") # Re-enable button
            if boots_check.winfo_exists():
                boots_check.config(state="normal") # Re-enable boots checkbox

        except (tk.TclError, AttributeError) as e:
            print(f"Error accessing widgets for {timer_id} on finish: {e}")
            return # Exit if widgets are gone

        # Play sound (add error handling)
        try:
            # Make sure 'notification_sound.mp3' is in the same directory 
            # or provide an absolute path if needed.
            playsound.playsound('notification_sound.mp3', block=False)
        except Exception as e:
            # Log error instead of showing a disruptive messagebox
            print(f"Error playing sound: {e}") 
            # Optionally show a non-blocking warning or status bar message
            # messagebox.showwarning("声音播放错误", f"无法播放提示音: {e}\n请确保 'notification_sound.mp3' 文件存在。", parent=self.app.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = LeagueTimerApp(root)
    root.mainloop()