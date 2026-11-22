import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sqlite3

# Button macros
NAV_BTN_WIDTH_RATIO = 0.2
NAV_BTN_HEIGHT_RATIO = 0.08

BACK_BTN_WIDTH_RATIO = 0.12
BACK_BTN_HEIGHT_RATIO = 0.08

# Graph frame macros
GRAPH_FRAME_WIDTH_RATIO = 1
GRAPH_FRAME_HEIGHT_RATIO = 1 - BACK_BTN_HEIGHT_RATIO * 2

# Carousel button macros
LEFT = -1
RIGHT = 1
INITIAL = 0
CAROUSEL_BTN_Y = BACK_BTN_HEIGHT_RATIO + GRAPH_FRAME_HEIGHT_RATIO
CAROUSEL_RIGHT_BTN = 1 - BACK_BTN_WIDTH_RATIO

# Graph Indices
GRAPH_1 = 0
GRAPH_2 = 1
GRAPH_3 = 2
GRAPH_4 = 3
GRAPH_5 = 4

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
        for Scene in (MainMenuScene, DataGraphScene, QueryScene, HelpScene):
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
        btn_datagraph.place(relx=0.5, rely=0.4, anchor='center', relwidth=NAV_BTN_WIDTH_RATIO, relheight=NAV_BTN_HEIGHT_RATIO)
        
        btn_query = ttk.Button(
            self, text="Querying",
            command=lambda: manager.show_scene("QueryScene"),
            style='app.TButton'
        )
        btn_query.place(relx=0.5, rely=0.5, anchor='center', relwidth=NAV_BTN_WIDTH_RATIO, relheight=NAV_BTN_HEIGHT_RATIO)

        btn_help = ttk.Button(
            self, text="Help",
            command=lambda: self.manager.show_scene("HelpScene"),
            style='help.TButton'
        )
        btn_help.place(relx=0.5, rely=0.7, anchor='center', relwidth=NAV_BTN_WIDTH_RATIO, relheight=NAV_BTN_HEIGHT_RATIO)
        
        btn_quit = ttk.Button(
            self, text="QUIT",
            command=lambda: self.exit_program(),
            style='quit.TButton'
        )
        btn_quit.place(relx=0.5, rely=0.8, anchor='center', relwidth=NAV_BTN_WIDTH_RATIO, relheight=NAV_BTN_HEIGHT_RATIO)
        
        self.bind("g", lambda e: self.manager.show_scene("DataGraphScene"))
        self.bind("q", lambda e: self.manager.show_scene("QueryScene"))
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
        btn_back.place(relx=0, rely=0, relwidth=BACK_BTN_WIDTH_RATIO, relheight=BACK_BTN_HEIGHT_RATIO)
        
        figure_frame = tk.Frame(self)
        figure_frame.place(relx=0, rely=BACK_BTN_HEIGHT_RATIO, relwidth=GRAPH_FRAME_WIDTH_RATIO, relheight=GRAPH_FRAME_HEIGHT_RATIO)
    
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

        self.set_graph(INITIAL) # Initial graph load-up
        
        btn_left = ttk.Button(
            master=self, text='<<',
            command=lambda: self.set_graph(LEFT),
            style='app.TButton'
        )
        btn_left.place(relx=0, rely=CAROUSEL_BTN_Y, relwidth=BACK_BTN_WIDTH_RATIO, relheight=BACK_BTN_HEIGHT_RATIO)

        btn_right = ttk.Button(
            master=self, text='>>',
            command=lambda: self.set_graph(RIGHT),
            style='app.TButton'
        )
        btn_right.place(relx=CAROUSEL_RIGHT_BTN, rely=CAROUSEL_BTN_Y, relwidth=BACK_BTN_WIDTH_RATIO, relheight=BACK_BTN_HEIGHT_RATIO)

        # Keybinds
        self.bind("<Left>", lambda e: self.set_graph(LEFT))
        self.bind("<Right>", lambda e: self.set_graph(RIGHT))
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
        
    def set_graph(self, direction):
        
        self.graph_idx = (self.graph_idx + direction) % len(self.graph_data)
        
        chosen_graph = self.graph_data[self.graph_idx]
        
        self.ax.clear()
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        df = pd.read_sql(chosen_graph["sql"], self.conn)
        
        if self.graph_idx == GRAPH_1:
            days = df["Day"]
            lows = df["low_counts"]
            highs = df["high_counts"]
            
            self.ax.bar(x=days, height=lows, label="Low", color="#de1414")
            self.ax.bar(x=days, height=highs, bottom=lows, label="High", color="#14de79")
            
            self.ax.legend()
        
        elif self.graph_idx == GRAPH_2:
            self.ax.scatter(x=df["Studying (Minutes)"], y=df["Programming (Minutes)"])
        
        elif self.graph_idx == GRAPH_3:
            hours = df["Sleep (Hours)"]
            lows = df["low_counts"]
            mods = df["mod_counts"]
            highs = df["high_counts"]
            
            self.ax.bar(x=hours, height=lows, label="Low", color='#de1414')
            self.ax.bar(x=hours, height=mods, bottom=lows, label="Moderate", color="#dede14")
            self.ax.bar(x=hours, height=highs, bottom=mods, label="High", color="#14de79")
            
            self.ax.legend()
        
        elif self.graph_idx == GRAPH_4:
            xs = [i for i in range(len(df))]
            self.ax.plot(xs, df["Reading (Minutes)"], marker='o', color="#14de79")
        
        elif self.graph_idx == GRAPH_5:
            self.ax.pie(x=df["counts"], labels=df["Productivity"], colors=["#14de79", "#de1414", "#dede14"],
                        autopct="%1.1f%%", startangle=90
            )
            self.ax.set_aspect("equal")
            
        self.ax.set_title(chosen_graph["title"])
        if self.graph_idx != GRAPH_5: # Because graph 5 is a pie chart
            self.ax.set_xlabel(chosen_graph["xlabel"])
            self.ax.set_ylabel(chosen_graph["ylabel"])
        
        self.canvas.draw_idle()
        
        
class QueryScene(tk.Frame, DBConnection):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager

        btn_back = ttk.Button(
            self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='app.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=BACK_BTN_WIDTH_RATIO, relheight=BACK_BTN_HEIGHT_RATIO)
        
        # Keybinds
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
        
        
class HelpScene(tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#5d5d5d")
        self.manager = manager

        btn_back = ttk.Button(
            self, text='Back',
            command=lambda: self.manager.show_scene("MainMenuScene"),
            style='help.TButton'
        )
        btn_back.place(relx=0, rely=0, relwidth=BACK_BTN_WIDTH_RATIO, relheight=BACK_BTN_HEIGHT_RATIO)
        
        # Keybinds
        self.bind("<Escape>", lambda e: self.manager.show_scene("MainMenuScene"))
    