# import vari
import tkinter as tk
from time import time
from . import frames as frm
from .canvas import PygameCanvas
from .graphics import CreaturesD, ChunkD
from . import var
import os
from math import ceil


class BaseTkWindow(tk.Tk):
    FRAMES = None
    TITLE = None

    def __init__(self, father):
        super(BaseTkWindow, self).__init__()
        self.father = father
        self.windows = list()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(self.TITLE)
        self.frames = {}

    def on_closing(self):
        self.destroy()

    def destroy(self):
        for i in self.windows:
            i.destroy()
        self.father.windows.remove(self)
        super(BaseTkWindow, self).destroy()

    def get_widget(self, frame, widget):
        return self.frames[frame].get_widget(widget)

    def get_frame(self, frame):
        return self.frames[frame]

    def frames_load(self):
        for i in self.FRAMES:
            new = self.FRAMES[i][0](self, **self.FRAMES[i][1])
            new.grid(**self.FRAMES[i][2])
            self.frames[i] = new

    def new_window_creation(self, wind_class, *args, **kwargs):
        new = wind_class(self, *args, **kwargs)
        self.windows.append(new)

    def update(self):
        for i in self.windows:
            i.update()
        super(BaseTkWindow, self).update()


class MainMenuWindow(BaseTkWindow):
    TITLE = "(R)Evolution Simulator"

    def __init__(self, father):
        self.FRAMES = {'logo': (frm.Logo, {}, {'row': 0, 'column': 0}),
                       'options': (frm.MainMenuOptions, {'windows': (self,)}, {'row': 1, 'column': 0})}
        super(MainMenuWindow, self).__init__(father)
        self.frames_load()
        self.windows = list()
        self.canvas = None

    def new_sim_window(self):
        self.new_window_creation(NewSimWindow)

    def load_sim_window(self):
        self.new_window_creation(LoadSimWindow)


class NewSimWindow(BaseTkWindow):
    TITLE = "New Simulation"

    def __init__(self, father):
        self.FRAMES = {'new': (frm.NewSim, {}, {'row': 0, 'column': 0})}
        super(NewSimWindow, self).__init__(father)
        self.frames_load()


class LoadSimWindow(BaseTkWindow):
    """Loading interface for simulation replay"""
    TITLE = "Load Simulation"

    def __init__(self, father):
        self.FRAMES = {'load': (frm.LoadSim, {'windows': (self,)}, {'row': 0, 'column': 0})}
        super(LoadSimWindow, self).__init__(father)
        self.frames_load()

    def simulation_file_load(self):
        """method which upload the data of the simulation"""
        sim_name = self.get_widget('load', 'entry').get()
        self.destroy()
        self.father.new_window_creation(ControlWindow, sim_name)


class ControlWindow(BaseTkWindow):
    """class of the main window"""
    FILES_TO_LOAD = ['simulationData', 'chunkData', 'creaturesData']
    START_GRAPH_TICK = 100
    START_TICK = 1.0
    START_ZOOM = 10
    START_SPEED = 1
    SHOWS = ['ch', 'cc', 'cd']
    MAX_SPEED = 100

    def __init__(self, father, sim_name):
        self.FRAMES = {'play_control': (frm.PlayControl, {}, {'row': 0, 'column': 0}),
                       'map_set': (frm.SetSuperFrame, {'windows': (self,)}, {'row': 1, 'column': 0}), }
        self.TITLE = sim_name
        super(ControlWindow, self).__init__(father)
        self.sim_name = sim_name
        self.tick = self.START_TICK
        self.zoom = self.START_ZOOM
        self.speed = self.START_SPEED
        self.max_speed = self.MAX_SPEED
        self.graph_tick = self.START_GRAPH_TICK
        self.is_playing = False
        self._files_load()
        self.shows = dict()
        self.last_frame_time = time()
        for i in self.SHOWS:
            self.shows[i] = tk.StringVar(master=self)
        self.diagram_choice = tk.StringVar(master=self)
        self.frames_load()
        self.canvas = PygameCanvas(self)
        self.resize(0)

    def _files_load(self):
        self.files = dict()
        try:
            for i in self.FILES_TO_LOAD:
                self.files[i] = open(os.path.join(var.SIMULATIONS_PATH, self.sim_name, f"{i}.csv"))
        except FileNotFoundError:
            print(f"ERROR: couldn't find '{self.sim_name}' files")
            exit(1)
        sim_data = self.files['simulationData'].readline().split(';')
        self.sim_width = int(sim_data[1])
        self.sim_height = int(sim_data[2])
        self.max_tick = int(sim_data[3])
        self.chunk_dim = int(sim_data[5])

        self.chunk_list = []
        for line in self.files['chunkData']:
            self.chunk_list.append(ChunkD(line))

        self.creature_list = set()
        for line in self.files['creaturesData']:
            self.creature_list.add(CreaturesD(line))

    def update(self):
        if self.is_playing:
            self.tick += self.time_diff * self.speed
            if int(self.tick) >= self.max_tick:
                self.start_play()
                self.tick = self.max_tick
            self.graph_tick = ceil(self.tick / 100) * 100
        shows = dict()
        for i in self.shows:
            shows[i] = self.shows[i].get()
        self.canvas.update(int(self.tick), shows)
        self.time_diff = time() - self.last_frame_time
        self.last_frame_time = time()
        try:
            self.set_fps(round(1.0 / self.time_diff, 1))
        except ZeroDivisionError:
            pass
        self.update_tick(int(self.tick))
        super(ControlWindow, self).update()

    def resize(self, coeff):
        """method which set to selected zoom"""
        self.zoom = max(1, self.zoom + coeff)
        self.canvas.resize()

    def graphics_window_create(self):
        """function which creates a graphic window"""
        subject = self.diagram_choice.get()
        if subject in ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed']:
            self.new_window_creation(GraphicsWindow, subject, frm.GeneDiagram)
        elif subject in ['foodmax', 'temperature_c', 'temperature_l', 'temperature_N']:
            self.new_window_creation(GraphicsWindow, subject, frm.SpreadDiagram)
        elif subject == 'population':
            self.new_window_creation(GraphicsWindow, subject, frm.PopulationDiagram)

    def speed_change(self, speed_cursor):
        """
        method which allow to change the speed of the simulation reproduction
        """
        self.speed = int(self.max_speed ** (float(speed_cursor) / 100))
        self.get_widget('play_control', 'speed_label').config(text=f"T/s: {self.speed:02d}")

    def set_tick(self, tick):
        self.tick = tick

    def dec_zoom(self):
        """method which decrease the zoom"""
        self.resize(-1)
        self.set_zoom()

    def inc_zoom(self):
        """method which increase the zoom"""
        self.resize(1)
        self.set_zoom()

    def set_zoom(self):
        """method which set to selected zoom"""
        self.get_widget('play_control', 'zoom').configure(text=f"zoom: {self.zoom}0%")

    def start_play(self):
        """method which starts or stops the reproduction of the simulation"""
        self.is_playing = not (self.is_playing)
        if self.is_playing:
            self.get_widget('play_control', 'play').config(text="Pause")
        else:
            self.get_widget('play_control', 'play').config(text="Play")

    def set_fps(self, fps):
        """
        method which reproduces the simulation, updating the screen
        """
        self.get_widget('play_control', 'fps').config(text=f"fps: {fps:04.1f}")

    def set_tick(self):
        """
        function which imposts a particular tick
        """
        try:
            self.tick = int(self.get_widget('play_control', 'tick_entry').get())
        except ValueError:
            pass

    def update_tick(self, tick):
        self.get_widget('play_control', 'tick_label').config(text=f"Tick: {tick:04d}")

    def destroy(self):
        self.canvas.destroy()
        super(ControlWindow, self).destroy()


class GraphicsWindow(BaseTkWindow):
    """classe per la rappresentazione dei grafici"""
    TICK_DIFFERENCE = 100
    START_FOLLOW_PLAY = False
    START_SHOW_TICK = False

    def __init__(self, father, subject, frame):
        self.TITLE = subject
        self.FRAMES = {
            'diagram_canvas': (frame, {'sim_name': father.sim_name, 'subject': subject}, {'row': 0, 'column': 0}),
            'command_bar': (frm.DiagramCommandBar, {'windows': (self, father)}, {'row': 1, 'column': 0}), }
        super(GraphicsWindow, self).__init__(father)
        self.frames_load()
        self.subject = subject
        self.tick_difference = self.TICK_DIFFERENCE
        self.follow_play = self.START_FOLLOW_PLAY
        self.show_tick = self.START_SHOW_TICK

    def tick_difference_set(self):
        try:
            self.tick_difference = int(self.get_widget('command_bar', 'tick_difference').get())
        except ValueError:
            pass

    def change_follow_play(self):
        self.follow_play = not self.follow_play

    def dyn_axes_set(self):
        self.get_frame('diagram_canvas').dyn_axes_set(self.father.graph_tick)

    def stat_axes_set(self):
        self.get_frame('diagram_canvas').stat_axes_set(self.father.max_tick)

    def change_show_tick(self):
        self.show_tick = not self.show_tick
        if self.show_tick:
            self.get_frame('diagram_canvas').add_show_tick(self.father.tick)
        else:
            self.get_frame('diagram_canvas').remove_show_tick()

    def tick_line_set(self):
        self.get_frame('diagram_canvas').tick_line_set(self.father.tick)

    def update(self):
        self.tick_line_set()
        if self.follow_play:
            self.dyn_axes_set()
        else:
            self.stat_axes_set()
        self.get_widget('diagram_canvas', 'canvas').draw()
        super(GraphicsWindow, self).update()
