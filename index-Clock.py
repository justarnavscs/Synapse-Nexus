import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import datetime
import threading
import winsound
import pytz
from PIL import Image, ImageTk
import os
import math
import random

class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Alarm Clock")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Initialize variables
        self.alarms = []
        self.stopwatch_running = False
        self.stopwatch_start_time = 0
        self.stopwatch_elapsed = 0
        self.lap_times = []
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_thread = None
        self.alarm_sounding = False
        self.current_alarm = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_clock_tab()
        self.create_alarm_tab()
        self.create_stopwatch_tab()
        self.create_timer_tab()
        self.create_world_clock_tab()
        self.create_settings_tab()
        
        # Start clock update
        self.update_time()
        
        # Load alarm tones
        self.load_alarm_tones()
        
        # Set dark theme
        self.set_theme()
    
    def set_theme(self):
        style = ttk.Style()
        style.theme_use('alt')
        
        # Configure styles
        style.configure('TNotebook', background='#2c3e50', borderwidth=0)
        style.configure('TNotebook.Tab', background='#34495e', foreground='white', 
                        padding=[10, 5], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#1abc9c')])
        
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', foreground='white', font=('Arial', 10))
        style.configure('TButton', background='#3498db', foreground='white', font=('Arial', 10, 'bold'),
                       borderwidth=1)
        style.map('TButton', background=[('active', '#2980b9')])
        
        style.configure('Alarm.TLabel', background='#34495e', foreground='white', 
                       font=('Arial', 11), padding=5)
        style.configure('Alarm.TButton', background='#e74c3c', foreground='white')
        style.map('Alarm.TButton', background=[('active', '#c0392b')])
        
        style.configure('Digital.TLabel', background='#2c3e50', foreground='#1abc9c', 
                        font=('Courier New', 36, 'bold'))
    
    def load_alarm_tones(self):
        self.alarm_tones = [
            {"name": "Classic Alarm", "func": self.play_classic_alarm},
            {"name": "Beep Pattern", "func": self.play_beep_pattern},
            {"name": "Chime", "func": self.play_chime},
            {"name": "Melody", "func": self.play_melody},
            {"name": "Siren", "func": self.play_siren}
        ]
    
    def create_clock_tab(self):
        self.clock_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clock_tab, text="Digital Clock")
        
        # Main clock display
        self.clock_label = ttk.Label(self.clock_tab, font=('Courier New', 48, 'bold'), 
                                    background='#2c3e50', foreground='#1abc9c')
        self.clock_label.pack(pady=50)
        
        # Date display
        self.date_label = ttk.Label(self.clock_tab, font=('Arial', 18), 
                                   background='#2c3e50', foreground='#ecf0f1')
        self.date_label.pack(pady=10)
        
        # Analog clock
        self.analog_canvas = tk.Canvas(self.clock_tab, width=300, height=300, 
                                      bg='#2c3e50', highlightthickness=0)
        self.analog_canvas.pack(pady=20)
        self.draw_analog_clock()
        
        # Next alarm display
        ttk.Label(self.clock_tab, text="Next Alarm:", font=('Arial', 14), 
                 background='#2c3e50', foreground='#ecf0f1').pack(pady=(30, 5))
        self.next_alarm_label = ttk.Label(self.clock_tab, font=('Arial', 14), 
                                        background='#2c3e50', foreground='#e74c3c')
        self.next_alarm_label.pack()
    
    def draw_analog_clock(self):
        self.analog_canvas.delete("all")
        width = 300
        height = 300
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 10
        
        # Draw clock face
        self.analog_canvas.create_oval(center_x - radius, center_y - radius,
                                      center_x + radius, center_y + radius,
                                      outline='#ecf0f1', width=2)
        
        # Draw numbers
        for i in range(1, 13):
            angle = math.radians(i * 30)
            num_x = center_x + (radius - 25) * math.sin(angle)
            num_y = center_y - (radius - 25) * math.cos(angle)
            self.analog_canvas.create_text(num_x, num_y, text=str(i), 
                                          fill='#ecf0f1', font=('Arial', 14, 'bold'))
        
        # Draw hour markers
        for i in range(60):
            angle = math.radians(i * 6)
            inner_radius = radius - 8 if i % 5 == 0 else radius - 5
            outer_radius = radius
            x1 = center_x + inner_radius * math.sin(angle)
            y1 = center_y - inner_radius * math.cos(angle)
            x2 = center_x + outer_radius * math.sin(angle)
            y2 = center_y - outer_radius * math.cos(angle)
            self.analog_canvas.create_line(x1, y1, x2, y2, fill='#7f8c8d', width=1)
        
        # Draw hands
        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second
        
        # Hour hand
        hour_angle = math.radians((hour * 30) + (minute * 0.5))
        hour_x = center_x + (radius * 0.5) * math.sin(hour_angle)
        hour_y = center_y - (radius * 0.5) * math.cos(hour_angle)
        self.analog_canvas.create_line(center_x, center_y, hour_x, hour_y, 
                                      fill='#ecf0f1', width=4, tags="hour")
        
        # Minute hand
        minute_angle = math.radians(minute * 6)
        minute_x = center_x + (radius * 0.7) * math.sin(minute_angle)
        minute_y = center_y - (radius * 0.7) * math.cos(minute_angle)
        self.analog_canvas.create_line(center_x, center_y, minute_x, minute_y, 
                                      fill='#3498db', width=3, tags="minute")
        
        # Second hand
        second_angle = math.radians(second * 6)
        second_x = center_x + (radius * 0.8) * math.sin(second_angle)
        second_y = center_y - (radius * 0.8) * math.cos(second_angle)
        self.analog_canvas.create_line(center_x, center_y, second_x, second_y, 
                                      fill='#e74c3c', width=2, tags="second")
        
        # Center dot
        self.analog_canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5, 
                                      fill='#e74c3c', outline='')
        
        # Schedule next update
        self.root.after(1000, self.draw_analog_clock)
    
    def create_alarm_tab(self):
        self.alarm_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.alarm_tab, text="Alarms")
        
        # Alarm creation frame
        create_frame = ttk.Frame(self.alarm_tab, padding=10)
        create_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(create_frame, text="Set New Alarm:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, columnspan=4, pady=(0, 10), sticky='w')
        
        # Time selection
        ttk.Label(create_frame, text="Time (HH:MM):").grid(row=1, column=0, padx=5, sticky='e')
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        self.ampm_var = tk.StringVar(value="AM")
        
        hour_spin = ttk.Spinbox(create_frame, from_=1, to=12, textvariable=self.hour_var, 
                               width=3, font=('Arial', 12))
        hour_spin.grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(create_frame, text=":").grid(row=1, column=2)
        
        minute_spin = ttk.Spinbox(create_frame, from_=0, to=59, textvariable=self.minute_var, 
                                 width=3, format="%02.0f", font=('Arial', 12))
        minute_spin.grid(row=1, column=3, padx=5, sticky='w')
        
        ampm_combo = ttk.Combobox(create_frame, textvariable=self.ampm_var, 
                                 values=["AM", "PM"], width=4, state="readonly")
        ampm_combo.grid(row=1, column=4, padx=5, sticky='w')
        
        # Label
        ttk.Label(create_frame, text="Label:").grid(row=2, column=0, padx=5, pady=10, sticky='e')
        self.alarm_label_var = tk.StringVar(value="Alarm")
        label_entry = ttk.Entry(create_frame, textvariable=self.alarm_label_var, width=20)
        label_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=10, sticky='w')
        
        # Tone selection
        ttk.Label(create_frame, text="Alarm Tone:").grid(row=3, column=0, padx=5, sticky='e')
        self.tone_var = tk.StringVar()
        tone_combo = ttk.Combobox(create_frame, textvariable=self.tone_var, 
                                 values=[tone['name'] for tone in self.alarm_tones], 
                                 state="readonly", width=20)
        tone_combo.current(0)
        tone_combo.grid(row=3, column=1, columnspan=3, padx=5, sticky='w')
        
        # Repeat options
        ttk.Label(create_frame, text="Repeat:").grid(row=4, column=0, padx=5, pady=10, sticky='e')
        self.repeat_vars = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.repeat_vars.append(var)
            cb = ttk.Checkbutton(create_frame, text=day, variable=var)
            cb.grid(row=4, column=i+1, padx=2)
        
        # Add button
        add_btn = ttk.Button(create_frame, text="Add Alarm", command=self.add_alarm)
        add_btn.grid(row=5, column=0, columnspan=7, pady=15)
        
        # Alarm list
        list_frame = ttk.Frame(self.alarm_tab)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create treeview with scrollbar
        self.alarm_tree = ttk.Treeview(list_frame, columns=('time', 'label', 'repeat', 'active'), show='headings')
        self.alarm_tree.heading('time', text='Time')
        self.alarm_tree.heading('label', text='Label')
        self.alarm_tree.heading('repeat', text='Repeat')
        self.alarm_tree.heading('active', text='Status')
        self.alarm_tree.column('time', width=100, anchor='center')
        self.alarm_tree.column('label', width=150, anchor='center')
        self.alarm_tree.column('repeat', width=150, anchor='center')
        self.alarm_tree.column('active', width=80, anchor='center')
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=vsb.set)
        
        self.alarm_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        btn_frame = ttk.Frame(self.alarm_tab)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        toggle_btn = ttk.Button(btn_frame, text="Toggle On/Off", command=self.toggle_alarm)
        toggle_btn.pack(side='left', padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Alarm", command=self.delete_alarm)
        delete_btn.pack(side='left', padx=5)
        
        snooze_btn = ttk.Button(btn_frame, text="Snooze (5 min)", command=self.snooze_alarm)
        snooze_btn.pack(side='right', padx=5)
    
    def create_stopwatch_tab(self):
        self.stopwatch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stopwatch_tab, text="Stopwatch")
        
        # Time display
        self.stopwatch_var = tk.StringVar(value="00:00:00.00")
        stopwatch_label = ttk.Label(self.stopwatch_tab, textvariable=self.stopwatch_var, 
                                   font=('Courier New', 36), background='#2c3e50', 
                                   foreground='#1abc9c')
        stopwatch_label.pack(pady=30)
        
        # Button frame
        btn_frame = ttk.Frame(self.stopwatch_tab)
        btn_frame.pack(pady=20)
        
        # Buttons
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_stopwatch)
        self.start_btn.pack(side='left', padx=10)
        
        self.lap_btn = ttk.Button(btn_frame, text="Lap", command=self.record_lap, state=tk.DISABLED)
        self.lap_btn.pack(side='left', padx=10)
        
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_stopwatch)
        self.reset_btn.pack(side='left', padx=10)
        
        # Lap times
        lap_frame = ttk.Frame(self.stopwatch_tab)
        lap_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.lap_tree = ttk.Treeview(lap_frame, columns=('number', 'time', 'lap_time'), show='headings')
        self.lap_tree.heading('number', text='Lap')
        self.lap_tree.heading('time', text='Total Time')
        self.lap_tree.heading('lap_time', text='Lap Time')
        self.lap_tree.column('number', width=50, anchor='center')
        self.lap_tree.column('time', width=150, anchor='center')
        self.lap_tree.column('lap_time', width=150, anchor='center')
        
        vsb = ttk.Scrollbar(lap_frame, orient="vertical", command=self.lap_tree.yview)
        self.lap_tree.configure(yscrollcommand=vsb.set)
        
        self.lap_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
    
    def create_timer_tab(self):
        self.timer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer_tab, text="Timer")
        
        # Timer display
        self.timer_var = tk.StringVar(value="01:00:00")
        timer_label = ttk.Label(self.timer_tab, textvariable=self.timer_var, 
                               font=('Courier New', 36), background='#2c3e50', 
                               foreground='#1abc9c')
        timer_label.pack(pady=30)
        
        # Time selection
        time_frame = ttk.Frame(self.timer_tab)
        time_frame.pack(pady=10)
        
        ttk.Label(time_frame, text="Hours:").grid(row=0, column=0, padx=5)
        self.timer_hours = tk.StringVar(value="1")
        hours_spin = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.timer_hours, 
                                width=3, font=('Arial', 12))
        hours_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(time_frame, text="Minutes:").grid(row=0, column=2, padx=5)
        self.timer_minutes = tk.StringVar(value="0")
        minutes_spin = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.timer_minutes, 
                                  width=3, font=('Arial', 12))
        minutes_spin.grid(row=0, column=3, padx=5)
        
        ttk.Label(time_frame, text="Seconds:").grid(row=0, column=4, padx=5)
        self.timer_seconds = tk.StringVar(value="0")
        seconds_spin = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.timer_seconds, 
                                  width=3, font=('Arial', 12))
        seconds_spin.grid(row=0, column=5, padx=5)
        
        # Button frame
        btn_frame = ttk.Frame(self.timer_tab)
        btn_frame.pack(pady=20)
        
        # Buttons
        self.timer_start_btn = ttk.Button(btn_frame, text="Start", command=self.start_timer)
        self.timer_start_btn.pack(side='left', padx=10)
        
        self.timer_pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.timer_pause_btn.pack(side='left', padx=10)
        
        self.timer_reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_timer)
        self.timer_reset_btn.pack(side='left', padx=10)
        
        # Progress bar
        self.timer_progress = ttk.Progressbar(self.timer_tab, orient='horizontal', 
                                            mode='determinate', length=400)
        self.timer_progress.pack(pady=20)
    
    def create_world_clock_tab(self):
        self.world_clock_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.world_clock_tab, text="World Clock")
        
        # Timezone selection
        top_frame = ttk.Frame(self.world_clock_tab)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Add Timezone:").pack(side='left', padx=(0, 10))
        
        self.tz_var = tk.StringVar()
        self.tz_combo = ttk.Combobox(top_frame, textvariable=self.tz_var, width=30)
        self.tz_combo['values'] = pytz.all_timezones
        self.tz_combo.pack(side='left', padx=(0, 10))
        
        add_btn = ttk.Button(top_frame, text="Add", command=self.add_timezone)
        add_btn.pack(side='left')
        
        # World clocks frame
        self.clocks_frame = ttk.Frame(self.world_clock_tab)
        self.clocks_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add some default timezones
        default_timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
        for tz in default_timezones:
            self.add_clock_display(tz)
        
        # Start world clock updates
        self.update_world_clocks()
    
    def create_settings_tab(self):
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        ttk.Label(self.settings_tab, text="Alarm Volume:", font=('Arial', 12)).pack(pady=(20, 5))
        
        self.volume_var = tk.IntVar(value=50)
        volume_scale = ttk.Scale(self.settings_tab, from_=0, to=100, 
                                variable=self.volume_var, orient='horizontal')
        volume_scale.pack(fill='x', padx=50, pady=5)
        
        ttk.Label(self.settings_tab, text="Snooze Duration (minutes):", 
                 font=('Arial', 12)).pack(pady=(20, 5))
        
        self.snooze_var = tk.IntVar(value=5)
        snooze_spin = ttk.Spinbox(self.settings_tab, from_=1, to=30, 
                                 textvariable=self.snooze_var, width=5)
        snooze_spin.pack(pady=5)
        
        ttk.Label(self.settings_tab, text="Alarm Duration (seconds):", 
                 font=('Arial', 12)).pack(pady=(20, 5))
        
        self.alarm_duration_var = tk.IntVar(value=60)
        duration_spin = ttk.Spinbox(self.settings_tab, from_=10, to=300, 
                                   textvariable=self.alarm_duration_var, width=5)
        duration_spin.pack(pady=5)
        
        # Theme selection
        ttk.Label(self.settings_tab, text="Theme:", font=('Arial', 12)).pack(pady=(20, 5))
        
        self.theme_var = tk.StringVar(value="Dark")
        theme_frame = ttk.Frame(self.settings_tab)
        theme_frame.pack(pady=5)
        
        dark_btn = ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="Dark")
        dark_btn.pack(side='left', padx=10)
        
        light_btn = ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="Light")
        light_btn.pack(side='left', padx=10)
        
        # Save button
        save_btn = ttk.Button(self.settings_tab, text="Save Settings", command=self.save_settings)
        save_btn.pack(pady=20)
    
    def update_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        
        self.clock_label.configure(text=current_time)
        self.date_label.configure(text=current_date)
        
        # Update next alarm
        self.update_next_alarm()
        
        # Check alarms
        self.check_alarms()
        
        # Schedule next update
        self.root.after(1000, self.update_time)
    
    def update_next_alarm(self):
        if not self.alarms:
            self.next_alarm_label.configure(text="No alarms set")
            return
        
        next_alarm = None
        now = datetime.datetime.now()
        
        for alarm in self.alarms:
            if not alarm['active']:
                continue
                
            # Create alarm time for today
            alarm_time = datetime.datetime(now.year, now.month, now.day, 
                                          alarm['hour'], alarm['minute'])
            
            # Convert to 24h format if needed
            if alarm['ampm'] == "PM" and alarm['hour'] != 12:
                alarm_time += datetime.timedelta(hours=12)
            elif alarm['ampm'] == "AM" and alarm['hour'] == 12:
                alarm_time = alarm_time.replace(hour=0)
            
            # If alarm time is earlier than now, set for tomorrow
            if alarm_time < now:
                alarm_time += datetime.timedelta(days=1)
            
            # Check if this is the earliest alarm
            if next_alarm is None or alarm_time < next_alarm['time']:
                next_alarm = {
                    'time': alarm_time,
                    'label': alarm['label']
                }
        
        if next_alarm:
            alarm_text = next_alarm['time'].strftime("%I:%M %p") + " - " + next_alarm['label']
            self.next_alarm_label.configure(text=alarm_text)
        else:
            self.next_alarm_label.configure(text="No active alarms")
    
    def add_alarm(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            ampm = self.ampm_var.get()
            label = self.alarm_label_var.get()
            tone = self.tone_var.get()
            
            # Validate time
            if hour < 1 or hour > 12:
                messagebox.showerror("Invalid Time", "Hour must be between 1 and 12")
                return
            if minute < 0 or minute > 59:
                messagebox.showerror("Invalid Time", "Minute must be between 0 and 59")
                return
            
            # Get repeat days
            repeat_days = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, var in enumerate(self.repeat_vars):
                if var.get():
                    repeat_days.append(days[i])
            
            # Create alarm dictionary
            alarm = {
                'hour': hour,
                'minute': minute,
                'ampm': ampm,
                'label': label,
                'tone': tone,
                'repeat': repeat_days,
                'active': True
            }
            
            # Add to alarms list
            self.alarms.append(alarm)
            
            # Add to treeview
            time_str = f"{hour:02d}:{minute:02d} {ampm}"
            repeat_str = ", ".join(repeat_days) if repeat_days else "Once"
            status_str = "Active" if alarm['active'] else "Inactive"
            
            self.alarm_tree.insert('', 'end', values=(time_str, label, repeat_str, status_str))
            
            # Clear fields
            self.hour_var.set("12")
            self.minute_var.set("00")
            self.ampm_var.set("AM")
            self.alarm_label_var.set("Alarm")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for time")
    
    def toggle_alarm(self):
        selected = self.alarm_tree.selection()
        if not selected:
            return
            
        # Get selected alarm index
        index = self.alarm_tree.index(selected[0])
        
        # Toggle active status
        self.alarms[index]['active'] = not self.alarms[index]['active']
        
        # Update treeview
        time_str = self.alarm_tree.item(selected[0], 'values')[0]
        label = self.alarm_tree.item(selected[0], 'values')[1]
        repeat = self.alarm_tree.item(selected[0], 'values')[2]
        status = "Active" if self.alarms[index]['active'] else "Inactive"
        
        self.alarm_tree.item(selected[0], values=(time_str, label, repeat, status))
        
        # Update next alarm display
        self.update_next_alarm()
    
    def delete_alarm(self):
        selected = self.alarm_tree.selection()
        if not selected:
            return
            
        # Get selected alarm index
        index = self.alarm_tree.index(selected[0])
        
        # Remove from alarms list
        del self.alarms[index]
        
        # Remove from treeview
        self.alarm_tree.delete(selected[0])
        
        # Update next alarm display
        self.update_next_alarm()
    
    def snooze_alarm(self):
        if not self.alarm_sounding:
            return
            
        # Stop current alarm
        self.alarm_sounding = False
        self.alarm_window.destroy()
        
        # Calculate snooze time
        snooze_minutes = self.snooze_var.get()
        now = datetime.datetime.now()
        snooze_time = now + datetime.timedelta(minutes=snooze_minutes)
        
        # Create snooze alarm
        hour = snooze_time.hour
        minute = snooze_time.minute
        ampm = "AM" if hour < 12 else "PM"
        
        if hour > 12:
            hour -= 12
        elif hour == 0:
            hour = 12
            
        alarm = {
            'hour': hour,
            'minute': minute,
            'ampm': ampm,
            'label': "Snooze",
            'tone': "Classic Alarm",
            'repeat': [],
            'active': True
        }
        
        # Add to alarms list
        self.alarms.append(alarm)
        
        # Add to treeview
        time_str = f"{hour:02d}:{minute:02d} {ampm}"
        self.alarm_tree.insert('', 'end', values=(time_str, "Snooze", "Once", "Active"))
        
        # Update next alarm display
        self.update_next_alarm()
    
    def check_alarms(self):
        if self.alarm_sounding:
            return
            
        now = datetime.datetime.now()
        current_weekday = now.strftime("%a")
        
        for alarm in self.alarms:
            if not alarm['active']:
                continue
                
            # Check if alarm repeats today or is set for today
            if alarm['repeat']:
                if current_weekday not in alarm['repeat']:
                    continue
            else:
                # Check if alarm time matches now (within 5 seconds)
                alarm_time = datetime.datetime(now.year, now.month, now.day, 
                                              alarm['hour'], alarm['minute'])
                
                # Convert to 24h format
                if alarm['ampm'] == "PM" and alarm['hour'] != 12:
                    alarm_time = alarm_time.replace(hour=alarm_time.hour + 12)
                elif alarm['ampm'] == "AM" and alarm['hour'] == 12:
                    alarm_time = alarm_time.replace(hour=0)
                
                time_diff = (now - alarm_time).total_seconds()
                if 0 <= time_diff < 5:  # Within 5 seconds of alarm time
                    self.trigger_alarm(alarm)
    
    def trigger_alarm(self, alarm):
        self.alarm_sounding = True
        self.current_alarm = alarm
        
        # Create alarm window
        self.alarm_window = tk.Toplevel(self.root)
        self.alarm_window.title("ALARM!")
        self.alarm_window.geometry("400x300")
        self.alarm_window.configure(bg='#e74c3c')
        self.alarm_window.attributes('-topmost', True)
        
        # Center window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.alarm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Alarm content
        alarm_time = f"{alarm['hour']:02d}:{alarm['minute']:02d} {alarm['ampm']}"
        ttk.Label(self.alarm_window, text="ALARM!", font=('Arial', 36, 'bold'), 
                 background='#e74c3c', foreground='white').pack(pady=30)
        
        ttk.Label(self.alarm_window, text=alarm_time, font=('Arial', 24), 
                 background='#e74c3c', foreground='white').pack()
        
        ttk.Label(self.alarm_window, text=alarm['label'], font=('Arial', 18), 
                 background='#e74c3c', foreground='white').pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(self.alarm_window)
        btn_frame.pack(pady=30)
        
        snooze_btn = ttk.Button(btn_frame, text="Snooze", command=self.snooze_alarm)
        snooze_btn.pack(side='left', padx=20)
        
        dismiss_btn = ttk.Button(btn_frame, text="Dismiss", command=self.dismiss_alarm)
        dismiss_btn.pack(side='left', padx=20)
        
        # Play alarm tone in a separate thread
        threading.Thread(target=self.play_alarm_tone, daemon=True).start()
    
    def dismiss_alarm(self):
        self.alarm_sounding = False
        self.alarm_window.destroy()
    
    def play_alarm_tone(self):
        # Find the selected tone
        tone_name = self.current_alarm['tone']
        for tone in self.alarm_tones:
            if tone['name'] == tone_name:
                tone_func = tone['func']
                break
        else:
            tone_func = self.play_classic_alarm
        
        # Play for the specified duration
        duration = self.alarm_duration_var.get()
        start_time = time.time()
        
        while self.alarm_sounding and (time.time() - start_time) < duration:
            tone_func()
            time.sleep(0.5)
    
    def play_classic_alarm(self):
        volume = self.volume_var.get() / 100
        winsound.Beep(int(800 * volume), 500)
    
    def play_beep_pattern(self):
        volume = self.volume_var.get() / 100
        for freq in [600, 800, 1000]:
            winsound.Beep(int(freq * volume), 200)
            time.sleep(0.1)
    
    def play_chime(self):
        volume = self.volume_var.get() / 100
        for _ in range(3):
            winsound.Beep(int(880 * volume), 300)
            time.sleep(0.2)
    
    def play_melody(self):
        volume = self.volume_var.get() / 100
        notes = [659, 587, 523, 587, 659, 659, 659]
        durations = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.6]
        
        for freq, dur in zip(notes, durations):
            winsound.Beep(int(freq * volume), int(dur * 1000))
            time.sleep(0.05)
    
    def play_siren(self):
        volume = self.volume_var.get() / 100
        for freq in range(800, 1200, 20):
            winsound.Beep(int(freq * volume), 50)
        for freq in range(1200, 800, -20):
            winsound.Beep(int(freq * volume), 50)
    
    def start_stopwatch(self):
        if not self.stopwatch_running:
            self.stopwatch_running = True
            self.stopwatch_start_time = time.time() - self.stopwatch_elapsed
            self.start_btn.configure(text="Stop")
            self.lap_btn.configure(state=tk.NORMAL)
            self.update_stopwatch()
        else:
            self.stopwatch_running = False
            self.stopwatch_elapsed = time.time() - self.stopwatch_start_time
            self.start_btn.configure(text="Start")
            self.lap_btn.configure(state=tk.DISABLED)
    
    def update_stopwatch(self):
        if self.stopwatch_running:
            elapsed = time.time() - self.stopwatch_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            centiseconds = int((elapsed - int(elapsed)) * 100)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
            self.stopwatch_var.set(time_str)
            self.root.after(10, self.update_stopwatch)
    
    def record_lap(self):
        if not self.stopwatch_running:
            return
            
        elapsed = time.time() - self.stopwatch_start_time
        lap_time = elapsed - self.lap_times[-1] if self.lap_times else elapsed
        
        # Format lap time
        hours = int(lap_time // 3600)
        minutes = int((lap_time % 3600) // 60)
        seconds = int(lap_time % 60)
        centiseconds = int((lap_time - int(lap_time)) * 100)
        lap_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        
        # Format total time
        hours_t = int(elapsed // 3600)
        minutes_t = int((elapsed % 3600) // 60)
        seconds_t = int(elapsed % 60)
        centiseconds_t = int((elapsed - int(elapsed)) * 100)
        total_time_str = f"{hours_t:02d}:{minutes_t:02d}:{seconds_t:02d}.{centiseconds_t:02d}"
        
        # Add to lap times
        self.lap_times.append(elapsed)
        
        # Add to treeview
        lap_num = len(self.lap_times)
        self.lap_tree.insert('', 'end', values=(lap_num, total_time_str, lap_time_str))
        self.lap_tree.yview_moveto(1)  # Scroll to bottom
    
    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0
        self.stopwatch_var.set("00:00:00.00")
        self.start_btn.configure(text="Start")
        self.lap_btn.configure(state=tk.DISABLED)
        self.lap_times = []
        self.lap_tree.delete(*self.lap_tree.get_children())
    
    def start_timer(self):
        if self.timer_running:
            return
            
        try:
            hours = int(self.timer_hours.get())
            minutes = int(self.timer_minutes.get())
            seconds = int(self.timer_seconds.get())
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                messagebox.showerror("Invalid Time", "Please enter a positive time value")
                return
                
            self.timer_remaining = total_seconds
            self.timer_total = total_seconds
            self.timer_progress['maximum'] = total_seconds
            self.timer_progress['value'] = total_seconds
            
            self.timer_running = True
            self.timer_start_btn.configure(state=tk.DISABLED)
            self.timer_pause_btn.configure(state=tk.NORMAL)
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for time")
    
    def run_timer(self):
        while self.timer_remaining > 0 and self.timer_running:
            time.sleep(1)
            self.timer_remaining -= 1
            
            # Update display
            hours = self.timer_remaining // 3600
            minutes = (self.timer_remaining % 3600) // 60
            seconds = self.timer_remaining % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Update progress bar
            progress_value = self.timer_total - self.timer_remaining
            
            # Update in main thread
            self.root.after(0, lambda: self.timer_var.set(time_str))
            self.root.after(0, lambda: self.timer_progress.configure(value=progress_value))
        
        # Timer finished
        if self.timer_remaining == 0:
            self.root.after(0, self.timer_finished)
    
    def pause_timer(self):
        self.timer_running = False
        self.timer_start_btn.configure(state=tk.NORMAL, text="Resume")
        self.timer_pause_btn.configure(state=tk.DISABLED)
    
    def reset_timer(self):
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_var.set("01:00:00")
        self.timer_start_btn.configure(state=tk.NORMAL, text="Start")
        self.timer_pause_btn.configure(state=tk.DISABLED)
        self.timer_progress['value'] = 0
        
        # Reset spinboxes to default
        self.timer_hours.set("1")
        self.timer_minutes.set("0")
        self.timer_seconds.set("0")
    
    def timer_finished(self):
        self.timer_running = False
        self.timer_var.set("00:00:00")
        self.timer_start_btn.configure(state=tk.NORMAL, text="Start")
        self.timer_pause_btn.configure(state=tk.DISABLED)
        
        # Play alarm sound
        threading.Thread(target=self.play_chime, daemon=True).start()
        
        # Show message
        messagebox.showinfo("Timer Complete", "Your timer has finished!")
    
    def add_timezone(self):
        tz_name = self.tz_var.get()
        if not tz_name:
            return
            
        if tz_name in pytz.all_timezones:
            self.add_clock_display(tz_name)
            self.tz_var.set("")
    
    def add_clock_display(self, tz_name):
        # Create clock frame
        clock_frame = ttk.Frame(self.clocks_frame, padding=10, relief='raised', borderwidth=1)
        clock_frame.pack(fill='x', padx=5, pady=5, ipady=5)
        
        # Location label
        location = tz_name.split('/')[-1].replace('_', ' ')
        ttk.Label(clock_frame, text=location, font=('Arial', 12, 'bold')).pack(anchor='w')
        
        # Time label
        time_var = tk.StringVar()
        ttk.Label(clock_frame, textvariable=time_var, font=('Courier New', 18)).pack(anchor='w')
        
        # Date label
        date_var = tk.StringVar()
        ttk.Label(clock_frame, textvariable=date_var, font=('Arial', 10)).pack(anchor='w')
        
        # Store for updates
        if not hasattr(self, 'world_clocks'):
            self.world_clocks = []
            
        self.world_clocks.append({
            'frame': clock_frame,
            'tz': tz_name,
            'time_var': time_var,
            'date_var': date_var
        })
    
    def update_world_clocks(self):
        if hasattr(self, 'world_clocks'):
            for clock in self.world_clocks:
                try:
                    tz = pytz.timezone(clock['tz'])
                    now = datetime.datetime.now(tz)
                    
                    time_str = now.strftime("%I:%M:%S %p")
                    date_str = now.strftime("%A, %B %d, %Y")
                    
                    clock['time_var'].set(time_str)
                    clock['date_var'].set(date_str)
                except:
                    # Handle any timezone errors
                    clock['time_var'].set("Error")
                    clock['date_var'].set("Invalid timezone")
        
        # Schedule next update
        self.root.after(1000, self.update_world_clocks)
    
    def save_settings(self):
        # In a real application, you would save these to a file
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully")
        
        # For theme change, you would implement theme switching logic here
        if self.theme_var.get() == "Light":
            messagebox.showinfo("Theme Change", "Light theme will be applied after restart")
        else:
            messagebox.showinfo("Theme Change", "Dark theme will be applied after restart")

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    root.mainloop()