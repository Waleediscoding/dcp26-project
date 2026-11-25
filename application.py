import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sqlite3

import config

class SceneManager(tk.Tk):
    def __init__(self, title, w, h):
        super().__init__()
        self.geometry(f'{w}x{h}')
        self.title(title)
        
        # Scene holder
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        self.scenes = {}
        
        # Populate scenes to grid
        for Scene in (MainMenuScene, DataGraphScene, QueryScene, InsertScene, HelpScene):
            name = Scene.__name__
            scene = Scene(parent=container, manager=self)
            self.scenes[name] = scene
            
            scene.grid(column=0, row=0, sticky='nsew')
        
        self.show_scene("MainMenuScene")
        
        # Style config
        style = ttk.Style()
        style.theme_use('alt') # For borderless buttons
        
        # Label config
        style.configure('menu.TLabel', foreground='#f2f2f2', background='#d5d5d5', font=("monospace", 30, "bold"))
        style.configure('help.TLabel', foreground='#f2f2f2', background='#2f2f2f', font=("monospace", 12))
        style.configure('fields.TLabel', foreground='#f2f2f2', background='#5d5d5d', font=('monospace', 8))
        
        # Button config - regular
        style.configure('app.TButton', foreground="#f2f2f2", background="#73ca1c", font=("monospace", 18), relief='flat')
        style.map("app.TButton",
                  foreground=[('active', '#73ca1c')],
                  background=[('active', '#f2f2f2')],
                  relief='flat'
        )

        # Button config - help
        style.configure('help.TButton', foreground="#f2f2f2", background="#1c73ca", font=("monospace", 18, "bold"), relief='flat')
        style.map("help.TButton",
                    foreground=[('active', '#1c73ca')],
                    background=[('active', '#f2f2f2')],
                    relief='flat'
        )
        
        # Button config - quit
        style.configure('quit.TButton', foreground="#f2f2f2", background="#ca251c", font=("monospace", 18, "bold"), relief='flat')
        style.map("quit.TButton",
                    foreground=[('active', '#ca251c')],
                    background=[('active', '#f2f2f2')],
                    relief='flat'
        )
        
    def show_scene(self, name):
        scene = self.scenes[name]
        scene.tkraise()
        scene.focus_set()

class DBConnection:
    _shared_conn = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._shared_conn is None:
            self._shared_conn = sqlite3.connect("database/data.db")
        
        self.conn = self._shared_conn
            
    def close(self):
        if self._shared_conn is not None:
            self._shared_conn.close()
            self._shared_conn = None
        
# Scenes
class MainMenuScene(DBConnection, tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager
        
        menu_label = ttk.Label(self, text='Main Menu', foreground='#f2f2f2', background='#5d5d5d', style='menu.TLabel')
        menu_label.place(relx=0.5, rely=0.1, anchor='center')
        
        # Add buttons to menu frame
        btn_datagraph = ttk.Button(
            self, text="Data Graph",
            command=lambda: manager.show_scene("DataGraphScene"),
            style='app.TButton'
        )
        
        btn_datagraph.place(relx=0.5, rely=0.4, anchor='center', relwidth=config.NAV_BTN_WIDTH_RATIO, relheight=config.NAV_BTN_HEIGHT_RATIO)
        
        btn_query = ttk.Button(
            self, text="Querying",
            command=lambda: manager.show_scene("QueryScene"),
            style='app.TButton'
        )
        btn_query.place(relx=0.5, rely=0.5, anchor='center', relwidth=config.NAV_BTN_WIDTH_RATIO, relheight=config.NAV_BTN_HEIGHT_RATIO)

        btn_insert = ttk.Button(
            self, text="Insertion",
            command=lambda: manager.show_scene("InsertScene"),
            style='app.TButton'
        )
        btn_insert.place(relx=0.5, rely=0.6, anchor='center', relwidth=config.NAV_BTN_WIDTH_RATIO, relheight=config.NAV_BTN_HEIGHT_RATIO)

        btn_help = ttk.Button(
            self, text="Help",
            command=lambda: self.manager.show_scene("HelpScene"),
            style='help.TButton'
        )
        btn_help.place(relx=0.5, rely=0.7, anchor='center', relwidth=config.NAV_BTN_WIDTH_RATIO, relheight=config.NAV_BTN_HEIGHT_RATIO)
        
        btn_quit = ttk.Button(
            self, text="QUIT",
            command=lambda: self.exit_program(),
            style='quit.TButton'
        )
        btn_quit.place(relx=0.5, rely=0.8, anchor='center', relwidth=config.NAV_BTN_WIDTH_RATIO, relheight=config.NAV_BTN_HEIGHT_RATIO)
        
        self.bind("g", lambda e: self.manager.show_scene("DataGraphScene"))
        self.bind("q", lambda e: self.manager.show_scene("QueryScene"))
        self.bind("i", lambda e: self.manager.show_scene("InsertScene"))
        self.bind("h", lambda e: self.manager.show_scene("HelpScene"))
        self.bind("<Escape>", lambda e: self.exit_program())
    
    def exit_program(self):
        self.conn.close()
        self.manager.destroy()
        
class DataGraphScene(DBConnection, tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(master=parent, bg="#ffffff")
        self.manager = manager
        self.graph_idx = 0   
        
        btn_back = ttk.Button(
            master=self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='app.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)
        
        figure_frame = tk.Frame(self)
        figure_frame.place(relx=0, rely=config.BACK_BTN_HEIGHT_RATIO, relwidth=config.GRAPH_FRAME_WIDTH_RATIO, relheight=config.GRAPH_FRAME_HEIGHT_RATIO)
    
        self.graph_data = [
            {
                "title": "Count of High and Low Productivity per Day",
                "sql": "SELECT Day, COUNT(*) FILTER (WHERE Productivity = 'LOW') as low_counts, COUNT(*) FILTER (WHERE Productivity = 'HIGH') as high_counts FROM productivity_metrics GROUP BY Day",
                "xlabel": "Days",
                "ylabel": "Count"
            },
            {
                "title": "Programming Against Studying (mins)",
                "sql": 'SELECT "Programming (Minutes)", "Studying (Minutes)" FROM productivity_metrics',
                "xlabel": "Studying",
                "ylabel": "Programming"
            },
            {
                "title": "Count of High and Low Productivity per Hours of Sleep",
                "sql": 'SELECT "Sleep (Hours)", COUNT(*) FILTER (WHERE Productivity = "LOW") as low_counts, COUNT(*) FILTER (WHERE Productivity = "MODERATE") as mod_counts, COUNT(*) FILTER (WHERE Productivity = "HIGH") as high_counts FROM productivity_metrics GROUP BY "Sleep (Hours)"',
                "xlabel": "Sleep Hours",
                "ylabel": "Count"
            },
            {
                "title": "Reading over the days (mins)",
                "sql": 'SELECT Date, "Reading (Minutes)" FROM productivity_metrics',
                "xlabel": "Time (Days)",
                "ylabel": "Minutes"
            },
            {
                "title": "Distribution of Low, Moderate, and High Classes Throughout the Days",
                "sql": 'SELECT Productivity, COUNT(*) as counts FROM productivity_metrics GROUP BY Productivity',
                "label": "Productivity"
            }
            ]
        
        self.fig = Figure(figsize=(10, 4), dpi=100)
        
        self.ax = self.fig.add_subplot(111)
        
        # The binding that converts a matplotlib graph to a canvas in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=figure_frame)
        self.canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1)

        self.set_graph(config.INITIAL) # Initial graph load-up
        
        btn_left = ttk.Button(
            master=self, text='<<',
            command=lambda: self.set_graph(config.LEFT),
            style='app.TButton'
        )
        btn_left.place(relx=0, rely=config.CAROUSEL_BTN_Y, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)

        btn_right = ttk.Button(
            master=self, text='>>',
            command=lambda: self.set_graph(config.RIGHT),
            style='app.TButton'
        )
        btn_right.place(relx=config.CAROUSEL_RIGHT_BTN, rely=config.CAROUSEL_BTN_Y, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)

        # Keybinds
        self.bind("<Left>", lambda e: self.set_graph(config.LEFT))
        self.bind("<Right>", lambda e: self.set_graph(config.RIGHT))
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
        
    def set_graph(self, direction):
        
        self.graph_idx = (self.graph_idx + direction) % len(self.graph_data)
        
        chosen_graph = self.graph_data[self.graph_idx]
        
        self.ax.clear()
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        df = pd.read_sql(chosen_graph["sql"], self.conn)
        
        if self.graph_idx == config.GRAPH_1:
            days = df["Day"]
            lows = df["low_counts"]
            highs = df["high_counts"]
            
            self.ax.bar(x=days, height=lows, label="Low", color="#de1414")
            self.ax.bar(x=days, height=highs, bottom=lows, label="High", color="#14de79")
            
            self.ax.legend()
        
        elif self.graph_idx == config.GRAPH_2:
            self.ax.scatter(x=df["Studying (Minutes)"], y=df["Programming (Minutes)"])
        
        elif self.graph_idx == config.GRAPH_3:
            hours = df["Sleep (Hours)"]
            lows = df["low_counts"]
            mods = df["mod_counts"]
            highs = df["high_counts"]
            
            self.ax.bar(x=hours, height=lows, label="Low", color='#de1414')
            self.ax.bar(x=hours, height=mods, bottom=lows, label="Moderate", color="#ffff22")
            self.ax.bar(x=hours, height=highs, bottom=mods, label="High", color="#14de79")
            
            self.ax.legend()
        
        elif self.graph_idx == config.GRAPH_4:
            xs = [i for i in range(len(df))]
            self.ax.plot(xs, df["Reading (Minutes)"], marker='o', color="#14de79")
        
        elif self.graph_idx == config.GRAPH_5:
            self.ax.pie(x=df["counts"], labels=df["Productivity"], colors=["#14de79", "#de1414", "#ffff22"],
                        autopct="%1.1f%%", startangle=90
            )
            self.ax.set_aspect("equal")
            
        self.ax.set_title(chosen_graph["title"])
        if self.graph_idx != config.GRAPH_5: # Because graph 5 is a pie chart
            self.ax.set_xlabel(chosen_graph["xlabel"])
            self.ax.set_ylabel(chosen_graph["ylabel"])
        
        self.canvas.draw_idle()
        
        
class QueryScene(DBConnection, tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager

        btn_back = ttk.Button(
            self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='app.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)
        
        query_to_insert = "SELECT * FROM productivity_metrics"
        sql_text = tk.Entry(master=self, border=0)
        sql_text.place(relx=0.45, rely=0.5, anchor="center", relwidth=config.TEXTBOX_WIDTH_RATIO, relheight=config.TEXTBOX_HEIGHT_RATIO)
        sql_text.insert(tk.END, query_to_insert)
        
        btn_enter = ttk.Button(
            master=self,
            text="Enter",
            command=lambda: self.execute_query(sql_text),
            style='app.TButton'
        )
        btn_enter.place(relx=config.ENTER_BTN_X, rely=0.5, anchor="center", relwidth=config.ENTER_BTN_WIDTH_RATIO, relheight=config.TEXTBOX_HEIGHT_RATIO)

        # Keybinds
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
        
    def execute_query(self, query_textbox):
        query = query_textbox.get()
        try:
            df = pd.read_sql(query, self.conn)
            
            print(df)

            query_textbox.delete(0, tk.END)
        except sqlite3.Error as e:
            print(f"Error: {e}")

class InsertScene(DBConnection, tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager

        btn_back = ttk.Button(
            self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='app.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)

        fields_label1 = ttk.Label(
            master=self,
            text='Date, Day, "Sleep (Hours)", "Reading (Minutes)", "Gaming (Minutes)"',
            style='fields.TLabel'
        )

        fields_label2 = ttk.Label(
            master=self,
            text='"Studying (Minutes)", "Programming (Minutes)", "Misc Leisure (Minutes)", Productivity',
            style='fields.TLabel'
        )
        
        fields_label1.place(relx=0.5, rely=0.4, anchor='center')
        fields_label2.place(relx=0.5, rely=0.45, anchor='center')
        
        sql_text = tk.Entry(master=self, border=0)
        sql_text.place(relx=0.45, rely=0.5, anchor="center", relwidth=config.TEXTBOX_WIDTH_RATIO, relheight=config.TEXTBOX_HEIGHT_RATIO)
        sql_text.insert(tk.END, "'25/11/2026', 'Wednesday', 7, 30, 60, 120, 90, 45, 'MODERATE'")
        
        btn_enter = ttk.Button(
            master=self,
            text="Enter",
            command=lambda: self.execute_query(sql_text),
            style='app.TButton'
        )
        btn_enter.place(relx=config.ENTER_BTN_X, rely=0.5, anchor="center", relwidth=config.ENTER_BTN_WIDTH_RATIO, relheight=config.TEXTBOX_HEIGHT_RATIO)
        
        # Keybinds
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
    
    def execute_query(self, query_textbox):
        fields = query_textbox.get()
        query = ('INSERT INTO productivity_metrics'
                '(Date, Day, "Sleep (Hours)", "Reading (Minutes)", "Gaming (Minutes)",'
                '"Studying (Minutes)", "Programming (Minutes)", "Misc Leisure (Minutes)", Productivity)'
                f'VALUES ({fields})')
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(query)
            self.conn.commit()
            
            query_textbox.delete(0, tk.END)
        except sqlite3.Error as e:
            print(f"Error: {e}")
    
class HelpScene(tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager

        btn_back = ttk.Button(
            self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='help.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=config.BACK_BTN_WIDTH_RATIO, relheight=config.BACK_BTN_HEIGHT_RATIO)
        
        text_frame = tk.Frame(master=self, bg="#2f2f2f")
        text_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=config.TEXTFRAME_WIDTH_RATIO, relheight=config.TEXTFRAME_HEIGHT_RATIO)
        
        text = """Shortcuts
- G: Go to 'Data Graph'
- Q: Go to 'Query'
- I: Go to 'Insertion'
- H: Go to 'Help'
- Esc: Quit program (if in main menu); Go to 'Main Menu' (if not in main menu)
- Left: Navigate left (in 'Data Graph')
- Right: Navigate right (in 'Data Graph')
- Enter: Submit query (in 'Query'/'Insertion')
"""
        
        label = ttk.Label(master=text_frame, text=text, style='help.TLabel')
        label.place(relx=0, rely=0)
        # Keybinds
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))