import tkinter as tk
from time import time
from . import frames as frm
from .canvas import PygameCanvas
from .graphics import CreaturesD, ChunkD
from . import var
from . import utility as utl
import os
from math import ceil


class BaseTkWindow(tk.Tk):
    """
    Template for windows classes
    """
    FRAMES = None
    TITLE = None

    def __init__(self, father):
        """
        Creates a new window

        :param father: the father of the window
        :type father: BaseTkWindow
        """
        super(BaseTkWindow, self).__init__()
        self.father = father
        self.windows = list()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title(self.TITLE)
        self.frames = {}

    def destroy(self):
        """
        Destroys all dependent windows and then the window itself

        :return:
        """
        for i in self.windows:
            i.destroy()
        self.father.windows.remove(self)
        super(BaseTkWindow, self).destroy()

    def get_widget(self, frame, widget):
        """
        Returns the widget object given the frame name and its name

        :param frame: the name of the frame in which the widget is
        :type frame: str
        :param widget: the name of the widget
        :type widget: str
        :return:
        """
        return self.frames[frame].get_widget(widget)

    def get_frame(self, frame):
        """
        Returns the frame object given the frame name

        :param frame: the name of the frame
        :type frame: str
        :return:
        """
        return self.frames[frame]

    def frames_load(self):
        """
        Initializes the frames inside the window

        :return:
        """
        for i in self.FRAMES:
            new = self.FRAMES[i][0](self, **self.FRAMES[i][1])
            new.grid(**self.FRAMES[i][2])
            self.frames[i] = new

    def new_window_creation(self, wind_class, *args, **kwargs):
        """
        Creates a new dependent window and adds it to windows list

        :param wind_class: the class of the window to create
        :type wind_class: type
        :param args: args to pass to window __init__
        :param kwargs: kwargs to pass to window __init__
        :return:
        """
        new = wind_class(self, *args, **kwargs)
        self.windows.append(new)

    def update(self):
        """
        Updates all dependent windows and the the window itself

        :return:
        """
        for i in self.windows:
            i.update()
        super(BaseTkWindow, self).update()


class MainMenuWindow(BaseTkWindow):
    """
    Main menu window class
    """
    TITLE = "(R)Evolution Simulator"

    def __init__(self, father):
        """
        Creates a new window

        :param father: the father of the window
        :type father: BaseTkWindow
        """
        self.FRAMES = {'logo': (frm.Logo, {}, {'row': 0, 'column': 0}),
                       'options': (frm.MainMenuOptions, {'windows': (self,)}, {'row': 1, 'column': 0})}
        super(MainMenuWindow, self).__init__(father)
        self.frames_load()
        self.windows = list()
        self.canvas = None

    def new_sim_window(self):
        """
        Creates a new dependent NewSimWindow

        :return:
        """
        self.new_window_creation(NewSimWindow)

    def load_sim_window(self):
        """
        Creates a new dependent LoadSimWindow

        :return:
        """
        self.new_window_creation(LoadSimWindow)


class NewSimWindow(BaseTkWindow):
    """
    New simulation window class
    """
    TITLE = "New Simulation"

    def __init__(self, father):
        """
        Creates a new simulation window

        :param father: the father of the window
        :type father: BaseTkWindow
        """
        self.FRAMES = {'new': (frm.NewSim, {}, {'row': 0, 'column': 0})}
        super(NewSimWindow, self).__init__(father)
        self.frames_load()


class LoadSimWindow(BaseTkWindow):
    """
    Load simulation window class
    """
    TITLE = "Load Simulation"

    def __init__(self, father):
        """
        Creates a load simulation window

        :param father: the father of the window
        :type father: BaseTkWindow
        """
        self.FRAMES = {'load': (frm.LoadSim, {'windows': (self,)}, {'row': 0, 'column': 0})}
        super(LoadSimWindow, self).__init__(father)
        self.frames_load()

    def simulation_file_load(self):
        """
        Destroys itself and creates a new SimReplayControlWindow dependent from father

        :return:
        """
        sim_name = self.get_widget('load', 'entry').get()
        self.destroy()
        self.father.new_window_creation(SimReplayControlWindow, sim_name)


class SimReplayControlWindow(BaseTkWindow):
    """
    Simulation replay control window class
    """
    FILES_TO_LOAD = ['simulationData', 'chunkData', 'creaturesData']
    START_GRAPH_TICK = 100
    START_TICK = 1.0
    START_ZOOM = 10
    START_SPEED = 1
    SHOWS = ['ch', 'cc', 'cd']
    MAX_SPEED = 100

    def __init__(self, father, sim_name):
        """
        Creates a new simulation replay control window

        :param father: the father of the window
        :type father: BaseTkWindow
        :param sim_name: the name of the simulation to load
        :type sim_name: str
        """
        self.FRAMES = {'play_control': (frm.PlayControl, {}, {'row': 0, 'column': 0}),
                       'map_set': (frm.SetSuperFrame, {'windows': (self,)}, {'row': 1, 'column': 0}), }
        self.TITLE = sim_name
        super(SimReplayControlWindow, self).__init__(father)
        self.sim_name = sim_name
        self.tick = self.START_TICK
        self.zoom = self.START_ZOOM
        self.speed = self.START_SPEED
        self.max_speed = self.MAX_SPEED
        self.graph_tick = self.START_GRAPH_TICK
        self.is_playing = False
        self._files_load()
        self.sim_width = self.dimension['width'] * self.chunk_dim
        self.sim_height = self.dimension['height'] * self.chunk_dim
        self.shows = dict()
        self.last_frame_time = time()
        for i in self.SHOWS:
            self.shows[i] = tk.StringVar(master=self)
        self.diagram_choice = tk.StringVar(master=self)
        self.frames_load()
        self.canvas = PygameCanvas(self)
        self.resize(0)

    def _files_load(self):
        """
        Loads simulation files

        :return:
        """
        self.files = dict()
        try:
            for i in self.FILES_TO_LOAD:
                self.files[i] = open(os.path.join(var.SIMULATIONS_PATH, self.sim_name, f"{i}.csv"))
        except FileNotFoundError:
            self.destroy()
        sim_data = self.files['simulationData'].readline()
        restored = utl.get_from_string(sim_data, 0, var.TO_RECORD['simulation'])
        self.__dict__.update(restored)

        self.chunk_list = []
        for line in self.files['chunkData']:
            self.chunk_list.append(ChunkD(line))

        self.creature_list = set()
        for line in self.files['creaturesData']:
            self.creature_list.add(CreaturesD(line))

    def update(self):
        if self.is_playing:
            self.tick += self.time_diff * self.speed
            if int(self.tick) >= self.lifetime:
                self.start_play()
                self.tick = self.lifetime
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
        super(SimReplayControlWindow, self).update()

    def resize(self, coeff):
        """method which set to selected zoom"""
        self.zoom = max(1, self.zoom + coeff)
        self.canvas.resize()

    def graphics_window_create(self):
        """function which creates a graphic window"""
        subject = self.diagram_choice.get()
        if subject in ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed']:
            self.new_window_creation(SimGraphicsWindow, subject, frm.GeneDiagram)
        elif subject in ['foodmax', 'temperature_c', 'temperature_l', 'temperature_N']:
            self.new_window_creation(SimGraphicsWindow, subject, frm.SpreadDiagram)
        elif subject == 'population':
            self.new_window_creation(SimGraphicsWindow, subject, frm.PopulationDiagram)

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
        super(SimReplayControlWindow, self).destroy()


class SimGraphicsWindow(BaseTkWindow):
    """
    Simulation graphics window class
    """
    TICK_DIFFERENCE = 100
    START_FOLLOW_PLAY = False
    START_SHOW_TICK = False

    def __init__(self, father, subject, frame):
        self.TITLE = subject
        self.FRAMES = {
            'diagram_canvas': (frame, {'sim_name': father.sim_name, 'subject': subject}, {'row': 0, 'column': 0}),
            'command_bar': (frm.DiagramCommandBar, {'windows': (self, father)}, {'row': 1, 'column': 0}), }
        super(SimGraphicsWindow, self).__init__(father)
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
        self.get_frame('diagram_canvas').stat_axes_set(self.father.lifetime)

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
        super(SimGraphicsWindow, self).update()
