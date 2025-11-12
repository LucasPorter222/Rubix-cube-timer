import tkinter as tk
from tkinter import ttk
import time
import random
import json
import os

class RubiksCubeTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubik's Cube Timer")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1b4b")
        
        # Variables
        self.is_running = False
        self.is_ready = False
        self.start_time = 0
        self.elapsed_time = 0
        self.times = []
        self.scramble = ""
        self.cube_type = "3x3"
        self.theme = "purple"
        self.show_scramble_viz = True
        self.sound_enabled = True
        self.inspection_time = 15
        self.use_inspection = False
        self.motivational_messages = True
        
        # Color themes
        self.themes = {
            "purple": {"bg": "#1e1b4b", "accent": "#8b5cf6", "secondary": "#3b82f6"},
            "blue": {"bg": "#0c4a6e", "accent": "#3b82f6", "secondary": "#06b6d4"},
            "green": {"bg": "#064e3b", "accent": "#10b981", "secondary": "#14b8a6"},
            "orange": {"bg": "#7c2d12", "accent": "#f97316", "secondary": "#f59e0b"},
            "pink": {"bg": "#831843", "accent": "#ec4899", "secondary": "#f43f5e"}
        }
        
        # Load saved times
        self.load_times()
        
        # Setup UI
        self.setup_ui()
        self.generate_scramble()
        self.update_timer()
        
        # Bind keyboard
        self.root.bind('<space>', self.handle_space_press)
        self.root.bind('<KeyRelease-space>', self.handle_space_release)
    
    def setup_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.themes[self.theme]["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.themes[self.theme]["bg"])
        title_frame.pack(pady=10)
        
        title = tk.Label(title_frame, text="Rubik's Cube Timer", 
                        font=("Arial", 32, "bold"), fg="#60a5fa", 
                        bg=self.themes[self.theme]["bg"])
        title.pack(side=tk.LEFT)
        
        settings_btn = tk.Button(title_frame, text="⚙️ Settings", 
                                font=("Arial", 12, "bold"),
                                bg=self.themes[self.theme]["accent"], 
                                fg="white", command=self.show_settings,
                                relief=tk.FLAT, padx=20, pady=10,
                                borderwidth=0, highlightthickness=0,
                                cursor="hand2")
        settings_btn.pack(side=tk.LEFT, padx=20)
        self.round_button(settings_btn)
        
        subtitle = tk.Label(main_frame, 
                           text=f"Press and hold SPACE to start • {self.cube_type}",
                           font=("Arial", 11), fg="#9ca3af", 
                           bg=self.themes[self.theme]["bg"])
        subtitle.pack()
        
        # Scramble section with rounded corners
        scramble_frame = tk.Frame(main_frame, bg="#1e293b", highlightbackground="#374151", 
                                 highlightthickness=2)
        scramble_frame.pack(fill=tk.X, pady=15)
        self.round_frame(scramble_frame)
        
        scramble_header = tk.Frame(scramble_frame, bg="#1e293b")
        scramble_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(scramble_header, text="🔀 Scramble", font=("Arial", 14, "bold"),
                fg="white", bg="#1e293b").pack(side=tk.LEFT)
        
        new_btn = tk.Button(scramble_header, text="New Scramble", 
                           bg=self.themes[self.theme]["accent"], 
                           fg="white", font=("Arial", 10, "bold"),
                           command=self.generate_scramble, relief=tk.FLAT,
                           padx=20, pady=8, borderwidth=0,
                           cursor="hand2")
        new_btn.pack(side=tk.RIGHT)
        self.round_button(new_btn)
        
        self.scramble_label = tk.Label(scramble_frame, text="", 
                                      font=("Courier", 16, "bold"), fg="#93c5fd",
                                      bg="#1e293b", wraplength=800)
        self.scramble_label.pack(padx=20, pady=(0, 20))
        
        # Timer display with rounded corners
        timer_frame = tk.Frame(main_frame, bg="#1e293b", highlightbackground="#374151",
                              highlightthickness=2)
        timer_frame.pack(fill=tk.X, pady=15)
        self.round_frame(timer_frame)
        
        self.timer_label = tk.Label(timer_frame, text="0:00.00", 
                                    font=("Arial", 80, "bold"), fg="white",
                                    bg="#1e293b")
        self.timer_label.pack(pady=50)
        
        self.status_label = tk.Label(timer_frame, text="Hold SPACE to ready",
                                     font=("Arial", 13), fg="#9ca3af",
                                     bg="#1e293b")
        self.status_label.pack(pady=(0, 30))
        
        # Stats with rounded boxes
        stats_frame = tk.Frame(main_frame, bg=self.themes[self.theme]["bg"])
        stats_frame.pack(fill=tk.X, pady=10)
        
        # First row
        stats_row1 = tk.Frame(stats_frame, bg=self.themes[self.theme]["bg"])
        stats_row1.pack(fill=tk.X, pady=(0, 8))
        
        self.solves_label = self.create_stat_box(stats_row1, "Solves", "0")
        self.best_label = self.create_stat_box(stats_row1, "Best", "--")
        self.avg_label = self.create_stat_box(stats_row1, "Average", "--")
        
        # Second row
        stats_row2 = tk.Frame(stats_frame, bg=self.themes[self.theme]["bg"])
        stats_row2.pack(fill=tk.X)
        
        self.ao5_label = self.create_stat_box(stats_row2, "Ao5", "--")
        self.ao12_label = self.create_stat_box(stats_row2, "Ao12", "--")
        
        # History with rounded corners
        history_frame = tk.Frame(main_frame, bg="#1e293b", highlightbackground="#374151",
                                highlightthickness=2)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.round_frame(history_frame)
        
        history_header = tk.Frame(history_frame, bg="#1e293b")
        history_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(history_header, text="⏱️ Recent Times", 
                font=("Arial", 14, "bold"), fg="white", 
                bg="#1e293b").pack(side=tk.LEFT)
        
        clear_btn = tk.Button(history_header, text="🗑️ Clear All", 
                             bg="#ef4444", fg="white", 
                             font=("Arial", 10, "bold"), command=self.clear_times,
                             relief=tk.FLAT, padx=15, pady=8, borderwidth=0,
                             cursor="hand2")
        clear_btn.pack(side=tk.RIGHT)
        self.round_button(clear_btn)
        
        self.history_listbox = tk.Listbox(history_frame, bg="#0f172a", 
                                         fg="white", font=("Courier", 12),
                                         selectbackground=self.themes[self.theme]["accent"],
                                         relief=tk.FLAT, height=8, borderwidth=0,
                                         highlightthickness=0)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    def round_frame(self, frame):
        """Add visual rounded effect to frame"""
        frame.config(relief=tk.FLAT, borderwidth=0)
        
    def round_button(self, button):
        """Add hover effect to buttons"""
        def on_enter(e):
            button['background'] = self.lighten_color(button['background'])
        
        def on_leave(e):
            button['background'] = button.cget('bg')
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def lighten_color(self, color):
        """Lighten a hex color slightly for hover effect"""
        # Simple lightening by adjusting hex values
        if color == self.themes[self.theme]["accent"]:
            return self.themes[self.theme]["secondary"]
        elif color == "#ef4444":
            return "#f87171"
        return color
    
    def create_stat_box(self, parent, title, value):
        frame = tk.Frame(parent, bg="#1e293b", highlightbackground="#374151",
                        highlightthickness=2)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        self.round_frame(frame)
        
        tk.Label(frame, text=title, font=("Arial", 11, "bold"), 
                fg="#9ca3af", bg="#1e293b").pack(pady=(15, 2))
        
        label = tk.Label(frame, text=value, font=("Arial", 28, "bold"),
                        fg="white", bg="#1e293b")
        label.pack(pady=(2, 15))
        
        return label
    
    def generate_scramble(self):
        moves = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", 
                "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]
        scramble_length = 20
        available_moves = moves
        
        if self.cube_type == "2x2":
            available_moves = ["R", "R'", "R2", "U", "U'", "U2", "F", "F'", "F2"]
            scramble_length = 11
        elif self.cube_type == "4x4":
            available_moves = moves + ["r", "r'", "r2", "l", "l'", "l2", 
                                      "u", "u'", "u2", "d", "d'", "d2",
                                      "f", "f'", "f2", "b", "b'", "b2"]
            scramble_length = 40
        elif self.cube_type == "5x5":
            available_moves = moves + ["r", "r'", "r2", "l", "l'", "l2",
                                      "u", "u'", "u2", "d", "d'", "d2",
                                      "f", "f'", "f2", "b", "b'", "b2"]
            scramble_length = 60
        elif self.cube_type == "pyraminx":
            available_moves = ["U", "U'", "L", "L'", "R", "R'", "B", "B'",
                             "u", "u'", "l", "l'", "r", "r'", "b", "b'"]
            scramble_length = 15
        elif self.cube_type == "skewb":
            available_moves = ["R", "R'", "L", "L'", "U", "U'", "B", "B'"]
            scramble_length = 10
        
        scramble = []
        last_move = ""
        
        for _ in range(scramble_length):
            move = random.choice(available_moves)
            while last_move and (move[0] == last_move[0] or 
                               move[0].upper() == last_move[0].upper()):
                move = random.choice(available_moves)
            scramble.append(move)
            last_move = move
        
        self.scramble = " ".join(scramble)
        self.scramble_label.config(text=self.scramble)
    
    def handle_space_press(self, event):
        if not self.is_running and not self.is_ready:
            self.is_ready = True
            self.timer_label.config(fg="#22c55e")
            self.status_label.config(text="Release to start!")
    
    def handle_space_release(self, event):
        if self.is_ready and not self.is_running:
            self.start_timer()
        elif self.is_running:
            self.stop_timer()
        self.is_ready = False
    
    def start_timer(self):
        self.is_running = True
        self.start_time = time.time()
        self.timer_label.config(fg="#3b82f6")
        self.status_label.config(text="Solving...")
    
    def stop_timer(self):
        self.is_running = False
        final_time = time.time() - self.start_time
        self.times.append(final_time)
        self.save_times()
        self.update_stats()
        self.generate_scramble()
        self.timer_label.config(fg="white")
        
        # Show gratification message based on time
        self.show_gratification_message(final_time)
    
    def show_gratification_message(self, time_seconds):
        """Show encouraging or congratulatory message based on solve time"""
        if not self.motivational_messages:
            self.status_label.config(text="Hold SPACE to ready")
            return
            
        messages_good = [
            "🎉 Excellent solve!",
            "🔥 Amazing time!",
            "⚡ Lightning fast!",
            "🏆 Outstanding!",
            "💪 Keep it up!",
            "✨ Incredible!",
            "🚀 Blazing speed!",
            "👏 Well done!"
        ]
        
        messages_intermediate = [
            "👍 Good job!",
            "💯 Nice solve!",
            "🎯 Solid time!",
            "😊 Getting better!",
            "📈 Making progress!",
            "⭐ Keep going!",
            "💪 Not bad!",
            "🔧 Consistent!"
        ]
        
        messages_encourage = [
            "💪 Keep practicing!",
            "📚 You'll get there!",
            "🎓 Practice makes perfect!",
            "🔄 Try again!",
            "📈 Room for improvement!",
            "🎯 Focus on technique!",
            "🧠 Learn the algorithms!",
            "⏰ Take your time!"
        ]
        
        if time_seconds < 20:
            message = random.choice(messages_good)
            color = "#22c55e"  # Green
        elif time_seconds < 30:
            message = random.choice(messages_intermediate)
            color = "#3b82f6"  # Blue
        else:
            message = random.choice(messages_encourage)
            color = "#f59e0b"  # Orange
        
        self.status_label.config(text=message, fg=color, font=("Arial", 14, "bold"))
        
        # Reset to normal after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(
            text="Hold SPACE to ready", 
            fg="#9ca3af",
            font=("Arial", 13)
        ))
    
    def update_timer(self):
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
        
        if self.is_running or self.elapsed_time > 0:
            minutes = int(self.elapsed_time // 60)
            seconds = int(self.elapsed_time % 60)
            milliseconds = int((self.elapsed_time % 1) * 100)
            time_str = f"{minutes}:{seconds:02d}.{milliseconds:02d}"
            self.timer_label.config(text=time_str)
            
            if not self.is_running and self.elapsed_time > 0:
                self.root.after(1000, lambda: setattr(self, 'elapsed_time', 0))
        
        self.root.after(10, self.update_timer)
    
    def calculate_average_of(self, n):
        """Calculate average of N, removing best and worst times (WCA rules)"""
        if len(self.times) < n:
            return None
        
        last_n = self.times[-n:]
        sorted_times = sorted(last_n)
        # Remove best and worst time
        trimmed = sorted_times[1:-1]
        return sum(trimmed) / len(trimmed)
    
    def format_time(self, seconds):
        """Format time in M:SS.MS format"""
        if seconds is None:
            return "--"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 100)
        return f"{minutes}:{secs:02d}.{milliseconds:02d}"
    
    def update_stats(self):
        self.solves_label.config(text=str(len(self.times)))
        
        if self.times:
            # Overall average
            avg = sum(self.times) / len(self.times)
            self.avg_label.config(text=self.format_time(avg))
            
            # Best time
            best = min(self.times)
            self.best_label.config(text=self.format_time(best))
            
            # Average of 5 (Ao5)
            ao5 = self.calculate_average_of(5)
            if ao5:
                self.ao5_label.config(text=self.format_time(ao5), fg="#22c55e")
            else:
                self.ao5_label.config(text=f"--  ({len(self.times)}/5)", fg="#6b7280")
            
            # Average of 12 (Ao12)
            ao12 = self.calculate_average_of(12)
            if ao12:
                self.ao12_label.config(text=self.format_time(ao12), fg="#3b82f6")
            else:
                self.ao12_label.config(text=f"--  ({len(self.times)}/12)", fg="#6b7280")
            
            # Update history
            self.history_listbox.delete(0, tk.END)
            for i, t in enumerate(reversed(self.times[-20:])):
                time_str = self.format_time(t)
                self.history_listbox.insert(tk.END, 
                    f"#{len(self.times)-i}    {time_str}")
    
    def clear_times(self):
        self.times = []
        self.save_times()
        self.update_stats()
        self.solves_label.config(text="0")
        self.avg_label.config(text="--")
        self.best_label.config(text="--")
        self.ao5_label.config(text="--", fg="white")
        self.ao12_label.config(text="--", fg="white")
        self.history_listbox.delete(0, tk.END)
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("650x600")
        settings_window.configure(bg=self.themes[self.theme]["bg"])
        
        # Make window scrollable
        canvas = tk.Canvas(settings_window, bg=self.themes[self.theme]["bg"], 
                          highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.themes[self.theme]["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title with padding
        title_frame = tk.Frame(scrollable_frame, bg=self.themes[self.theme]["bg"])
        title_frame.pack(pady=25)
        
        tk.Label(title_frame, text="⚙️ Settings", font=("Arial", 28, "bold"),
                fg="white", bg=self.themes[self.theme]["bg"]).pack()
        
        # Main content frame
        content_frame = tk.Frame(scrollable_frame, bg=self.themes[self.theme]["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Cube type section
        cube_section = tk.Frame(content_frame, bg="#1e293b", highlightbackground="#374151",
                               highlightthickness=2)
        cube_section.pack(fill=tk.X, pady=(0, 15))
        self.round_frame(cube_section)
        
        tk.Label(cube_section, text="🧩 Cube Type", font=("Arial", 16, "bold"),
                fg="white", bg="#1e293b").pack(pady=(20, 15))
        
        cube_frame = tk.Frame(cube_section, bg="#1e293b")
        cube_frame.pack(pady=(0, 20))
        
        cube_types = [["2x2", "3x3", "4x4"], ["5x5", "pyraminx", "skewb"]]
        for row in cube_types:
            row_frame = tk.Frame(cube_frame, bg="#1e293b")
            row_frame.pack(pady=5)
            for cube in row:
                btn = tk.Button(row_frame, text=cube.upper(), width=12,
                               bg=self.themes[self.theme]["accent"] if cube == self.cube_type else "#374151",
                               fg="white", font=("Arial", 11, "bold"),
                               command=lambda c=cube: self.change_cube_type(c, settings_window),
                               relief=tk.FLAT, padx=15, pady=12, borderwidth=0,
                               cursor="hand2")
                btn.pack(side=tk.LEFT, padx=5)
                self.round_button(btn)
        
        # Theme section
        theme_section = tk.Frame(content_frame, bg="#1e293b", highlightbackground="#374151",
                                highlightthickness=2)
        theme_section.pack(fill=tk.X, pady=(0, 15))
        self.round_frame(theme_section)
        
        tk.Label(theme_section, text="🎨 Color Theme", font=("Arial", 16, "bold"),
                fg="white", bg="#1e293b").pack(pady=(20, 15))
        
        theme_frame = tk.Frame(theme_section, bg="#1e293b")
        theme_frame.pack(pady=(0, 20))
        
        theme_names = [["purple", "blue", "green"], ["orange", "pink"]]
        for row in theme_names:
            row_frame = tk.Frame(theme_frame, bg="#1e293b")
            row_frame.pack(pady=5)
            for theme_name in row:
                btn = tk.Button(row_frame, text=theme_name.capitalize(), width=12,
                               bg=self.themes[theme_name]["accent"],
                               fg="white", font=("Arial", 11, "bold"),
                               command=lambda t=theme_name: self.change_theme(t, settings_window),
                               relief=tk.FLAT, padx=15, pady=12, borderwidth=0,
                               cursor="hand2")
                btn.pack(side=tk.LEFT, padx=5)
                self.round_button(btn)
        
        # Display Options section
        display_section = tk.Frame(content_frame, bg="#1e293b", highlightbackground="#374151",
                                  highlightthickness=2)
        display_section.pack(fill=tk.X, pady=(0, 15))
        self.round_frame(display_section)
        
        tk.Label(display_section, text="👁️ Display Options", font=("Arial", 16, "bold"),
                fg="white", bg="#1e293b").pack(pady=(20, 15))
        
        # Motivational messages toggle
        msg_frame = tk.Frame(display_section, bg="#1e293b")
        msg_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(msg_frame, text="Motivational Messages", font=("Arial", 12),
                fg="white", bg="#1e293b").pack(side=tk.LEFT)
        
        msg_btn = tk.Button(msg_frame, 
                           text="ON" if self.motivational_messages else "OFF",
                           bg="#22c55e" if self.motivational_messages else "#ef4444",
                           fg="white", font=("Arial", 10, "bold"),
                           command=lambda: self.toggle_setting('motivational_messages', msg_btn),
                           relief=tk.FLAT, padx=20, pady=8, borderwidth=0,
                           cursor="hand2", width=6)
        msg_btn.pack(side=tk.RIGHT)
        self.round_button(msg_btn)
        
        tk.Label(display_section, text="", bg="#1e293b").pack(pady=10)
        
        # Timer Options section
        timer_section = tk.Frame(content_frame, bg="#1e293b", highlightbackground="#374151",
                                highlightthickness=2)
        timer_section.pack(fill=tk.X, pady=(0, 15))
        self.round_frame(timer_section)
        
        tk.Label(timer_section, text="⏱️ Timer Options", font=("Arial", 16, "bold"),
                fg="white", bg="#1e293b").pack(pady=(20, 15))
        
        # Inspection time toggle
        insp_frame = tk.Frame(timer_section, bg="#1e293b")
        insp_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(insp_frame, text="WCA Inspection (15s)", font=("Arial", 12),
                fg="white", bg="#1e293b").pack(side=tk.LEFT)
        
        insp_btn = tk.Button(insp_frame, 
                            text="ON" if self.use_inspection else "OFF",
                            bg="#22c55e" if self.use_inspection else "#ef4444",
                            fg="white", font=("Arial", 10, "bold"),
                            command=lambda: self.toggle_setting('use_inspection', insp_btn),
                            relief=tk.FLAT, padx=20, pady=8, borderwidth=0,
                            cursor="hand2", width=6)
        insp_btn.pack(side=tk.RIGHT)
        self.round_button(insp_btn)
        
        tk.Label(timer_section, text="", bg="#1e293b").pack(pady=10)
        
        # Export/Import section
        export_section = tk.Frame(content_frame, bg="#1e293b", highlightbackground="#374151",
                                 highlightthickness=2)
        export_section.pack(fill=tk.X, pady=(0, 20))
        self.round_frame(export_section)
        
        tk.Label(export_section, text="💾 Data Management", font=("Arial", 16, "bold"),
                fg="white", bg="#1e293b").pack(pady=(20, 15))
        
        export_btn_frame = tk.Frame(export_section, bg="#1e293b")
        export_btn_frame.pack(pady=(0, 20))
        
        export_btn = tk.Button(export_btn_frame, text="📤 Export Times",
                              bg=self.themes[self.theme]["accent"], fg="white",
                              font=("Arial", 11, "bold"), command=self.export_times,
                              relief=tk.FLAT, padx=20, pady=12, borderwidth=0,
                              cursor="hand2")
        export_btn.pack(side=tk.LEFT, padx=5)
        self.round_button(export_btn)
        
        stats_btn = tk.Button(export_btn_frame, text="📊 View Statistics",
                             bg=self.themes[self.theme]["secondary"], fg="white",
                             font=("Arial", 11, "bold"), command=self.show_detailed_stats,
                             relief=tk.FLAT, padx=20, pady=12, borderwidth=0,
                             cursor="hand2")
        stats_btn.pack(side=tk.LEFT, padx=5)
        self.round_button(stats_btn)
        
        algs_btn = tk.Button(export_btn_frame, text="📖 Algorithm Sheet",
                            bg="#10b981", fg="white",
                            font=("Arial", 11, "bold"), command=self.show_algorithm_sheet,
                            relief=tk.FLAT, padx=20, pady=12, borderwidth=0,
                            cursor="hand2")
        algs_btn.pack(side=tk.LEFT, padx=5)
        self.round_button(algs_btn)
    
    def change_cube_type(self, cube_type, window):
        self.cube_type = cube_type
        self.clear_times()
        self.generate_scramble()
        window.destroy()
        self.restart_ui()
    
    def change_theme(self, theme, window):
        self.theme = theme
        self.save_times()
        window.destroy()
        self.restart_ui()
    
    def toggle_setting(self, setting_name, button):
        """Toggle a boolean setting and update button"""
        current_value = getattr(self, setting_name)
        setattr(self, setting_name, not current_value)
        new_value = getattr(self, setting_name)
        
        button.config(
            text="ON" if new_value else "OFF",
            bg="#22c55e" if new_value else "#ef4444"
        )
        self.save_times()
    
    def export_times(self):
        """Export times to a text file"""
        if not self.times:
            return
        
        try:
            filename = f"rubiks_times_{self.cube_type}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"Rubik's Cube Timer Export - {self.cube_type}\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Solves: {len(self.times)}\n")
                f.write(f"Average: {self.format_time(sum(self.times)/len(self.times))}\n")
                f.write(f"Best: {self.format_time(min(self.times))}\n")
                if len(self.times) >= 5:
                    f.write(f"Ao5: {self.format_time(self.calculate_average_of(5))}\n")
                if len(self.times) >= 12:
                    f.write(f"Ao12: {self.format_time(self.calculate_average_of(12))}\n")
                f.write("\n--- All Times ---\n")
                for i, t in enumerate(self.times, 1):
                    f.write(f"{i}. {self.format_time(t)}\n")
            
            # Show success message
            success_window = tk.Toplevel(self.root)
            success_window.title("Export Successful")
            success_window.geometry("400x150")
            success_window.configure(bg="#1e293b")
            
            tk.Label(success_window, text="✅ Export Successful!", 
                    font=("Arial", 16, "bold"), fg="#22c55e",
                    bg="#1e293b").pack(pady=20)
            tk.Label(success_window, text=f"Saved to: {filename}",
                    font=("Arial", 10), fg="white",
                    bg="#1e293b").pack(pady=10)
            
            ok_btn = tk.Button(success_window, text="OK", 
                             bg=self.themes[self.theme]["accent"],
                             fg="white", font=("Arial", 11, "bold"),
                             command=success_window.destroy,
                             relief=tk.FLAT, padx=30, pady=10)
            ok_btn.pack(pady=10)
        except Exception as e:
            print(f"Export error: {e}")
    
    def show_detailed_stats(self):
        """Show detailed statistics window"""
        if not self.times:
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Detailed Statistics")
        stats_window.geometry("500x600")
        stats_window.configure(bg=self.themes[self.theme]["bg"])
        
        tk.Label(stats_window, text="📊 Detailed Statistics", 
                font=("Arial", 24, "bold"), fg="white",
                bg=self.themes[self.theme]["bg"]).pack(pady=20)
        
        stats_frame = tk.Frame(stats_window, bg="#1e293b", 
                              highlightbackground="#374151", highlightthickness=2)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        stats_text = tk.Text(stats_frame, bg="#0f172a", fg="white",
                            font=("Courier", 11), relief=tk.FLAT,
                            padx=20, pady=20, wrap=tk.WORD)
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Calculate statistics
        total = len(self.times)
        avg = sum(self.times) / total
        best = min(self.times)
        worst = max(self.times)
        median = sorted(self.times)[total // 2]
        
        # Write stats
        stats_text.insert(tk.END, f"Cube Type: {self.cube_type.upper()}\n\n")
        stats_text.insert(tk.END, f"Total Solves: {total}\n")
        stats_text.insert(tk.END, f"Average: {self.format_time(avg)}\n")
        stats_text.insert(tk.END, f"Median: {self.format_time(median)}\n")
        stats_text.insert(tk.END, f"Best: {self.format_time(best)}\n")
        stats_text.insert(tk.END, f"Worst: {self.format_time(worst)}\n\n")
        
        if total >= 5:
            stats_text.insert(tk.END, f"Average of 5: {self.format_time(self.calculate_average_of(5))}\n")
        if total >= 12:
            stats_text.insert(tk.END, f"Average of 12: {self.format_time(self.calculate_average_of(12))}\n")
        if total >= 50:
            stats_text.insert(tk.END, f"Average of 50: {self.format_time(self.calculate_average_of(50))}\n")
        if total >= 100:
            stats_text.insert(tk.END, f"Average of 100: {self.format_time(self.calculate_average_of(100))}\n")
        
        # Sub-X stats
        stats_text.insert(tk.END, f"\n--- Time Distribution ---\n")
        sub_15 = sum(1 for t in self.times if t < 15)
        sub_20 = sum(1 for t in self.times if t < 20)
        sub_30 = sum(1 for t in self.times if t < 30)
        sub_60 = sum(1 for t in self.times if t < 60)
        
        stats_text.insert(tk.END, f"Sub-15s: {sub_15} ({sub_15/total*100:.1f}%)\n")
        stats_text.insert(tk.END, f"Sub-20s: {sub_20} ({sub_20/total*100:.1f}%)\n")
        stats_text.insert(tk.END, f"Sub-30s: {sub_30} ({sub_30/total*100:.1f}%)\n")
        stats_text.insert(tk.END, f"Sub-60s: {sub_60} ({sub_60/total*100:.1f}%)\n")
        
        # Last 10 solves
        stats_text.insert(tk.END, f"\n--- Last 10 Solves ---\n")
        for i, t in enumerate(self.times[-10:], 1):
            stats_text.insert(tk.END, f"{total-10+i}. {self.format_time(t)}\n")
        
        stats_text.config(state=tk.DISABLED)
        
        close_btn = tk.Button(stats_window, text="Close",
                             bg=self.themes[self.theme]["accent"],
                             fg="white", font=("Arial", 11, "bold"),
                             command=stats_window.destroy,
                             relief=tk.FLAT, padx=30, pady=10)
        close_btn.pack(pady=10)
    
    def show_algorithm_sheet(self):
        """Show algorithm reference sheet"""
        alg_window = tk.Toplevel(self.root)
        alg_window.title("Algorithm Sheet")
        alg_window.geometry("900x700")
        alg_window.configure(bg=self.themes[self.theme]["bg"])
        
        # Header
        header_frame = tk.Frame(alg_window, bg=self.themes[self.theme]["bg"])
        header_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(header_frame, text="📖 Speedcubing Algorithm Sheet", 
                font=("Arial", 24, "bold"), fg="white",
                bg=self.themes[self.theme]["bg"]).pack()
        
        # Category selector
        category_frame = tk.Frame(alg_window, bg=self.themes[self.theme]["bg"])
        category_frame.pack(fill=tk.X, padx=20, pady=10)
        
        categories = ["F2L", "OLL", "PLL", "2-Look OLL", "2-Look PLL"]
        self.current_alg_category = tk.StringVar(value="F2L")
        
        for cat in categories:
            btn = tk.Button(category_frame, text=cat,
                           bg=self.themes[self.theme]["accent"] if cat == "F2L" else "#374151",
                           fg="white", font=("Arial", 10, "bold"),
                           command=lambda c=cat, w=alg_window: self.switch_alg_category(c, w),
                           relief=tk.FLAT, padx=15, pady=8, borderwidth=0,
                           cursor="hand2")
            btn.pack(side=tk.LEFT, padx=5)
            self.round_button(btn)
        
        # Content area with scroll
        content_frame = tk.Frame(alg_window, bg="#1e293b", 
                                highlightbackground="#374151", highlightthickness=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.alg_text = tk.Text(content_frame, bg="#0f172a", fg="white",
                               font=("Courier", 10), relief=tk.FLAT,
                               padx=20, pady=20, wrap=tk.WORD)
        
        scrollbar = tk.Scrollbar(content_frame, command=self.alg_text.yview)
        self.alg_text.configure(yscrollcommand=scrollbar.set)
        
        self.alg_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial content
        self.load_alg_content("F2L")
        
        # Close button
        close_btn = tk.Button(alg_window, text="Close",
                             bg=self.themes[self.theme]["accent"],
                             fg="white", font=("Arial", 11, "bold"),
                             command=alg_window.destroy,
                             relief=tk.FLAT, padx=30, pady=10)
        close_btn.pack(pady=10)
    
    def switch_alg_category(self, category, window):
        """Switch between algorithm categories"""
        self.current_alg_category.set(category)
        self.load_alg_content(category)
        
        # Update button colors
        for widget in window.winfo_children()[1].winfo_children():
            if isinstance(widget, tk.Button):
                if widget.cget('text') == category:
                    widget.config(bg=self.themes[self.theme]["accent"])
                else:
                    widget.config(bg="#374151")
    
    def load_alg_content(self, category):
        """Load algorithm content for selected category"""
        self.alg_text.config(state=tk.NORMAL)
        self.alg_text.delete(1.0, tk.END)
        
        alg_data = {
            "F2L": """
═══════════════════════════════════════════════════════════════
                        F2L (First Two Layers)
═══════════════════════════════════════════════════════════════

BASIC F2L CASES (Corner in U, Edge in U)
─────────────────────────────────────────────────────────────

Case 1: Both pieces oriented correctly
  └─ U R U' R'                                          (4 moves)

Case 2: Edge flipped
  └─ y' U' L' U L                                       (4 moves)
  └─ R U R' U' R U R'                                   (7 moves)

Case 3: Corner flipped
  └─ U' R U' R' U R U R'                                (8 moves)
  └─ y' U L' U L U' L' U' L                             (8 moves)

Case 4: Both pieces flipped
  └─ R U' R' U R U' R'                                  (7 moves)
  └─ y' L' U L U' L' U L                                (7 moves)

ADVANCED F2L CASES
─────────────────────────────────────────────────────────────

Split Pair (Corner front, Edge back)
  └─ R U R' U' R U R' U' R U R'                        (11 moves)

Weird Case (Corner facing out)
  └─ R U' R' U2 R U' R'                                 (7 moves)

Edge in Slot, Corner in U
  └─ R U' R' U' R U R' U R U' R'                       (11 moves)
""",
            "OLL": """
═══════════════════════════════════════════════════════════════
                    OLL (Orientation Last Layer)
═══════════════════════════════════════════════════════════════

T-SHAPES
─────────────────────────────────────────────────────────────

OLL 33 - T-Shape
  └─ R U R' U' R' F R F'                                (8 moves)

OLL 45 - T-Shape ⭐ FASTEST
  └─ F R U R' U' F'                                     (6 moves)

SQUARES
─────────────────────────────────────────────────────────────

OLL 5 - Square
  └─ r' U2 R U R' U r                                   (7 moves)

OLL 6 - Square
  └─ r U2 R' U' R U' r'                                 (7 moves)

L-SHAPES
─────────────────────────────────────────────────────────────

OLL 47 - L-Shape ⭐ BETTER
  └─ R' U' R' F R F' U R                                (8 moves)

OLL 48 - L-Shape
  └─ F R U R' U' R U R' U' F'                          (10 moves)

P-SHAPES
─────────────────────────────────────────────────────────────

OLL 43 - P-Shape
  └─ F' U' L' U L F                                     (6 moves)

OLL 44 - P-Shape
  └─ F U R U' R' F'                                     (6 moves)

SUNE & ANTI-SUNE (Most Common!)
─────────────────────────────────────────────────────────────

OLL 27 - Sune
  └─ R U R' U R U2 R'                                   (7 moves)

OLL 26 - Anti-Sune
  └─ R U2 R' U' R U' R'                                 (7 moves)

LIGHTNING BOLTS
─────────────────────────────────────────────────────────────

OLL 7 - Lightning
  └─ r U R' U R U2 r'                                   (7 moves)

OLL 8 - Lightning
  └─ r' U' R U' R' U2 r                                 (7 moves)

FISH SHAPES
─────────────────────────────────────────────────────────────

OLL 9 - Fish
  └─ R U R' U' R' F R2 U R' U' F'                      (11 moves)

OLL 37 - Fish
  └─ F R U' R' U' R U R' F'                             (9 moves)

DOT CASES (All Edges Flipped)
─────────────────────────────────────────────────────────────

OLL 1 - Dot
  └─ R U2 R2 F R F' U2 R' F R F'                       (11 moves)

OLL 2 - Dot ⭐ BETTER
  └─ r U r' U2 R U2 R' U2 r U' r'                      (11 moves)

OLL 3 - Dot
  └─ f R U R' U' f' U' F R U R' U' F'                  (13 moves)

OLL 4 - Dot
  └─ f R U R' U' f' U F R U R' U' F'                   (13 moves)

FULL LIST: 57 OLL cases total. Practice recognition!
""",
            "PLL": """
═══════════════════════════════════════════════════════════════
                   PLL (Permutation Last Layer)
═══════════════════════════════════════════════════════════════

U PERMS (Edge Swaps)
─────────────────────────────────────────────────────────────

Ua Perm - 3 edges clockwise ⭐ FASTEST
  └─ M2 U M U2 M' U M2                                  (7 moves)
  └─ R U' R U R U R U' R' U' R2                        (11 moves)

Ub Perm - 3 edges counter-clockwise ⭐ FASTEST
  └─ M2 U' M U2 M' U' M2                                (7 moves)
  └─ R2 U R U R' U' R' U' R' U R'                      (11 moves)

H Perm - Opposite edges swap ⭐ FASTEST
  └─ M2 U M2 U2 M2 U M2                                 (7 moves)

Z Perm - Adjacent edges swap
  └─ M2 U M2 U M' U2 M2 U2 M'                           (9 moves)

A PERMS (Corner Swaps)
─────────────────────────────────────────────────────────────

Aa Perm - 3 corners clockwise ⭐ BETTER
  └─ R' F R' B2 R F' R' B2 R2                           (9 moves)
  └─ x R' U R' D2 R U' R' D2 R2 x'                     (10 moves)

Ab Perm - 3 corners counter-clockwise ⭐ BETTER
  └─ R B' R F2 R' B R F2 R2                             (9 moves)
  └─ x R2 D2 R U R' D2 R U' R x'                       (10 moves)

E Perm - Both edge pairs swap ⭐ BETTER
  └─ R B' R' F R B R' F' R B R' F R B' R' F'          (16 moves)

T, J, R, F PERMS (Adjacent Swaps)
─────────────────────────────────────────────────────────────

T Perm ⭐ STANDARD
  └─ R U R' U' R' F R2 U' R' U' R U R' F'              (14 moves)

Ja Perm ⭐ NO ROTATION
  └─ R' U L' U2 R U' R' U2 R L U'                      (11 moves)
  └─ x R2 F R F' R U2 r' U r U2 x'                     (11 moves)

Jb Perm ⭐ STANDARD
  └─ R U R' F' R U R' U' R' F R2 U' R' U'              (14 moves)

Ra Perm ⭐ BETTER
  └─ L U2 L' U2 L F' L' U' L U L F L2 U                (14 moves)

Rb Perm ⭐ STANDARD
  └─ R' U2 R U2 R' F R U R' U' R' F' R2 U'             (14 moves)

F Perm ⭐ STANDARD
  └─ R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R   (18 moves)

V, Y, N PERMS (Diagonal Swaps)
─────────────────────────────────────────────────────────────

V Perm
  └─ R' U R' U' y R' F' R2 U' R' U R' F R F           (14 moves)

Y Perm ⭐ STANDARD
  └─ F R U' R' U' R U R' F' R U R' U' R' F R F'       (17 moves)

Na Perm ⭐ BETTER
  └─ z U R' D R2 U' R D' U R' D R2 U' R D' z'          (14 moves)

Nb Perm ⭐ BETTER
  └─ z D' R U' R2 D R' U D' R U' R2 D R' U z'          (14 moves)

G PERMS (Most Complex - All 15 moves)
─────────────────────────────────────────────────────────────

Ga Perm ⭐ STANDARD
  └─ R2 U R' U R' U' R U' R2 D U' R' U R D'            (15 moves)

Gb Perm ⭐ STANDARD
  └─ R' U' R U D' R2 U R' U R U' R U' R2 D            (15 moves)

Gc Perm ⭐ STANDARD
  └─ R2 U' R U' R U R' U R2 D' U R U' R' D            (15 moves)

Gd Perm ⭐ STANDARD
  └─ R U R' U' D R2 U' R U' R' U R' U R2 D'           (15 moves)

TOTAL: 21 PLL cases. Master recognition for sub-15 times!
""",
            "2-Look OLL": """
═══════════════════════════════════════════════════════════════
              2-LOOK OLL (Beginner Friendly Method)
═══════════════════════════════════════════════════════════════

STEP 1: ORIENT EDGES (Make Yellow Cross)
─────────────────────────────────────────────────────────────

Dot (No edges oriented)
  └─ F R U R' U' F'                                     (6 moves)

L-Shape (2 adjacent edges)
  └─ F U R U' R' F'                                     (6 moves)

Line (2 opposite edges)
  └─ F R U R' U' F'                                     (6 moves)

STEP 2: ORIENT CORNERS
─────────────────────────────────────────────────────────────

Sune (1 or 2 corners oriented) ⭐ MOST COMMON
  └─ R U R' U R U2 R'                                   (7 moves)

Anti-Sune
  └─ R U2 R' U' R U' R'                                 (7 moves)

H (2 opposite corners need flip)
  └─ R U R' U R U' R' U R U2 R'                        (11 moves)

Pi (No corners oriented)
  └─ R U2 R2 U' R2 U' R2 U2 R                           (9 moves)

L (All 4 corners need orientation)
  └─ F R U R' U' F' f R U R' U' f'                     (12 moves)

TIPS:
• Only 7 algorithms to learn!
• Much easier than full OLL
• Perfect for beginners
• Can get sub-20 times with this
""",
            "2-Look PLL": """
═══════════════════════════════════════════════════════════════
              2-LOOK PLL (Beginner Friendly Method)
═══════════════════════════════════════════════════════════════

STEP 1: PERMUTE CORNERS (Look for "Headlights")
─────────────────────────────────────────────────────────────

Aa Perm (Headlights on left)
  └─ x R' U R' D2 R U' R' D2 R2 x'                     (10 moves)

Ab Perm (Headlights on right)
  └─ x R2 D2 R U R' D2 R U' R x'                       (10 moves)

E Perm (No headlights - both diagonal swaps)
  └─ x' R U' R' D R U R' D' R U R' D R U' R' D' x'    (17 moves)

STEP 2: PERMUTE EDGES
─────────────────────────────────────────────────────────────

Ua Perm (3 edges clockwise) ⭐ FASTEST
  └─ M2 U M U2 M' U M2                                  (7 moves)
  └─ R U' R U R U R U' R' U' R2                        (11 moves)

Ub Perm (3 edges counter-clockwise) ⭐ FASTEST
  └─ M2 U' M U2 M' U' M2                                (7 moves)
  └─ R2 U R U R' U' R' U' R' U R'                      (11 moves)

H Perm (Opposite edges swap) ⭐ FASTEST
  └─ M2 U M2 U2 M2 U M2                                 (7 moves)

Z Perm (Adjacent edges swap)
  └─ M2 U M2 U M' U2 M2 U2 M'                           (9 moves)

TIPS:
• Only 7 algorithms total!
• Very beginner friendly
• Focus on corner permutation first
• "Headlights" = two matching colors next to each other
• Can achieve sub-30 times easily with this method

LEARNING PATH:
1. Master 2-Look OLL/PLL first
2. Then learn full PLL (21 cases)
3. Finally tackle full OLL (57 cases)
"""
        }
        
        content = alg_data.get(category, "Content not available")
        self.alg_text.insert(tk.END, content)
        self.alg_text.config(state=tk.DISABLED)
    
    def restart_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_stats()
    
    def save_times(self):
        data = {
            'times': self.times,
            'cube_type': self.cube_type,
            'theme': self.theme,
            'motivational_messages': self.motivational_messages,
            'use_inspection': self.use_inspection
        }
        try:
            with open('rubiks_timer_data.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def load_times(self):
        try:
            if os.path.exists('rubiks_timer_data.json'):
                with open('rubiks_timer_data.json', 'r') as f:
                    data = json.load(f)
                    self.times = data.get('times', [])
                    self.cube_type = data.get('cube_type', '3x3')
                    self.theme = data.get('theme', 'purple')
                    self.motivational_messages = data.get('motivational_messages', True)
                    self.use_inspection = data.get('use_inspection', False)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RubiksCubeTimer(root)
    root.mainloop()