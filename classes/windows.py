# import vari
import tkinter as tk
from time import time
from . import frames as frm
from .pygamecanvas import PygameCanvas, ChunkD, CreaturesD
# import matplotlib
# matplotlib.use("Tkagg")



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

    def get_widget(self, frame, name):
        return self.frames[frame].widgets[name]

    def frames_load(self):
        for i in self.FRAMES:
            new = self.FRAMES[i][0](self, **self.FRAMES[i][1])
            new.grid(**self.FRAMES[i][2])
            self.frames[i] = new

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

    def load_window_creation(self):
        new_load = LoadWindow(self)
        self.windows.append(new_load)

    def start_simulation(self, sim_name):
        new_control = ControlWindow(self, sim_name)
        self.windows.append(new_control)

class LoadWindow(BaseTkWindow):
    """Loading interface for simulation replay"""
    TITLE = "Simulation Load"

    def __init__(self, father):
        self.FRAMES = {'load': (frm.Load, {'windows': (self,)}, {'row': 0, 'column': 0})}
        super(LoadWindow, self).__init__(father)
        self.frames_load()

    def simulation_file_load(self):
        """method which upload the data of the simulation"""
        sim_name = self.get_widget('load', 'entry').get()
        self.destroy()
        self.father.start_simulation(sim_name)

class ControlWindow(BaseTkWindow):
    """class of the main window"""
    TITLE = "Replay Toolbar"
    FILES_TO_LOAD = ['simulationData', 'chunkData', 'creaturesData']
    DEFAULT_GRAPH_TICK = 100
    START_TICK = 1.0
    START_ZOOM = 10
    START_SPEED = 1
    START_SHOWS = {'ch': 'FM', 'cc': 'TR', 'cd': 'E'}
    MAX_SPEED = 100

    def __init__(self, father, sim_name):
        self.father = father
        self.sim_name = sim_name
        self.tick = self.START_TICK
        self.zoom = self.START_ZOOM
        self.speed = self.START_SPEED
        self.max_speed = self.MAX_SPEED
        self.is_playing = False
        self._files_load()
        self.shows = dict()
        self.last_frame_time = time()
        self.FRAMES = {'play_control': (frm.PlayControl, {}, {'row': 0, 'column': 0}),
                       'map_set': (frm.SetSuperFrame, {'windows': (self,)}, {'row': 1, 'column': 0}), }

        super(ControlWindow, self).__init__(father)
        for i in self.START_SHOWS:
            self.shows[i] = tk.StringVar(master=self)
            self.shows[i].set(self.START_SHOWS[i])
        self.frames_load()
        self.canvas = PygameCanvas(self)
        self.resize(0)
        self.graph_tick = self.DEFAULT_GRAPH_TICK
        self.diagram_windows = []

    def _files_load(self):
        self.files = dict()
        try:
            for i in self.FILES_TO_LOAD:
                self.files[i] = open(f"{self.sim_name}/{i}.csv")
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
        '''new_graph_subj = self.diagram_chioce.get()
        if new_graph_subj in ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed']:
            new_window = GeneGraphicsWindow(self.file, new_graph_subj, self)
        elif new_graph_subj in ['foodmax', 'temperature_c', 'temperature_l', 'temperature_N']:
            new_window = SpreadGraphicsWindow(self.file, new_graph_subj, self)
        elif new_graph_subj == 'population':
            new_window = PopulationGraphicsWindow(self.file, new_graph_subj, self)
        self.diagram_windows.append(new_window)
        new_window.mainloop()'''

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


'''class GraphicsWindow(tk.Tk):
    """classe per la rappresentazione dei grafici"""

    def __init__(self, file, subj, father, subplots=1):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.father = father
        self.subject = subj
        self.title(subj)  # titolo prima finestra: "Simulation Load"
        self.file = file[subj]
        self.tick_difference = 100
        self.follow_play = False
        self.show_tick = False
        self.data_init(self.file)
        self.figure = Figure()
        self.subplot_creation(subplots)
        self.canvas_creation()
        self.command_bar_creation()

    def on_closing(self):
        """funzione per la chiusura delle finestre"""
        self.father.diagram_windows.remove(self)
        self.destroy()

    def canvas_creation(self):
        """funzione per la rappresentazione del canvas dove porre il grafico"""
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.show()
        self.canvas_tk = self.canvas.get_tk_widget()
        self.canvas_tk.pack(fill=BOTH, expand=True)

    def subplot_creation(self, n):
        """funzione per la creazione delle coordinate delle linee"""
        self.subplots = []
        self.tick_lines = []
        for i in range(n):
            self.subplots.append(self.figure.add_subplot(n, 1, i + 1))

    def data_init(self, file):
        """funzione per la lettura dei file con i dati"""
        self.data = [[] for i in range(len(self.file.readline().split(';')))]
        self.file.seek(0)
        for line in file:
            linelist = line.split(';')
            linelist[-1] = linelist[-1][:-1]
            for i in range(len(self.data)):
                self.data[i].append(float(linelist[i]))
        file.seek(0)

    def command_bar_creation(self):
        """funzione per la creazione della barra con le opzioni"""
        self.command_frame = Frame(self)
        self.asd = IntVar()
        self.follow_play_checkbutton = Checkbutton(self.command_frame, text="Follow play", command=self.change_follow_play)
        self.follow_play_checkbutton.pack(side=LEFT)
        self.tick_difference_spinbox = Spinbox(self.command_frame, from_=100, to=self.father.max_tick, increment=100, command=self.tick_difference_set)
        self.tick_difference_spinbox.pack(side=LEFT)
        self.show_tick_checkbutton = Checkbutton(self.command_frame, text="Show tick", command=self.change_show_tick)
        self.show_tick_checkbutton.pack(side=LEFT)
        self.command_frame.pack(side=BOTTOM)

    def tick_difference_set(self):
        try:
            self.tick_difference = int(self.tick_difference_spinbox.get())
        except ValueError:
            pass
        if self.follow_play:
            self.dyn_axes_set()

    def change_follow_play(self):
        self.follow_play = not self.follow_play
        if self.follow_play:
            self.dyn_axes_set()
        else:
            self.stat_axes_set()

    def stat_axes_set(self):
        for subplot in self.subplots:
            subplot.set_xlim([0, self.father.max_tick])
        self.canvas.draw()
        self.update()

    def dyn_axes_set(self):
        for subplot in self.subplots:
            subplot.set_xlim([self.father.graph_tick - self.tick_difference, self.father.graph_tick])
        self.canvas.draw()
        self.update()

    def change_show_tick(self):
        self.show_tick = not self.show_tick
        if self.show_tick:
            for subplot in self.subplots:
                self.tick_lines.append(subplot.axvline(x=self.father.tick))
            self.canvas.draw()
            self.update()
        else:
            for line in self.tick_lines:
                line.remove()
            self.tick_lines = []
            self.canvas.draw()
            self.update()

    def tick_line_set(self):
        for line in self.tick_lines:
            line.set_xdata(self.father.tick)
        self.canvas.draw()
        self.update()


class GeneGraphicsWindow(GraphicsWindow):
    COLOURS = ['dimgray', 'lightgrey', 'darkgray', 'lightgrey', 'dimgray', 'red']
    TEXTS = [["", "Tick", ""]]
    LABELS = ["Minimum", "25% percentile", "Median", "75% percentile", "Maximum", "Average"]

    def __init__(self, file, subj, father):
        GraphicsWindow.__init__(self, file, subj, father)
        for i in range(len(self.data) - 1):
            self.subplots[0].plot(self.data[0], self.data[i + 1], color=GeneGraphicsWindow.COLOURS[i], label=GeneGraphicsWindow.LABELS[i])
        self.set_titles()
        self.stat_axes_set()
        self.canvas.draw()
        self.update()

    def set_titles(self):
        self.subplots[0].set_title(self.subject)
        self.subplots[0].set_xlabel(GeneGraphicsWindow.TEXTS[0][1])
        self.subplots[0].set_ylabel(self.subject)
        handles, labels = self.subplots[0].get_legend_handles_labels()
        self.subplots[0].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)


class PopulationGraphicsWindow(GraphicsWindow):
    COLOURS = [['darkgreen', 'saddlebrown'], ['peru', 'lightskyblue', 'lightgreen']]
    TEXTS = [["Births and Deaths", "Tick", "Number of Creatures"], ["Causes of Death", "Tick", "Number of Creatures"]]
    LABELS = [["Births", "Deaths"], ["Starvation", "Temperature", "Old Age"]]

    def __init__(self, file, subj, father):
        GraphicsWindow.__init__(self, file, subj, father, 2)
        self.death_tot_calc()
        self.subplots[0].plot(self.data[0], self.data[1], color=PopulationGraphicsWindow.COLOURS[0][0], label=PopulationGraphicsWindow.LABELS[0][0])
        self.subplots[0].plot(self.data[0], self.data[5], color=PopulationGraphicsWindow.COLOURS[0][1], label=PopulationGraphicsWindow.LABELS[0][1])
        for i in range(3):
            self.subplots[1].plot(self.data[0], self.data[i + 2], color=PopulationGraphicsWindow.COLOURS[1][i], label=PopulationGraphicsWindow.LABELS[1][i])
        self.set_titles()
        self.stat_axes_set()
        self.canvas.draw()
        self.update()

    def death_tot_calc(self):
        self.data.append([])
        for i in range(len(self.data[0])):
            self.data[5].append(self.data[2][i] + self.data[3][i] + self.data[4][i])

    def set_titles(self):
        for i in range(2):
            self.subplots[i].set_title(PopulationGraphicsWindow.TEXTS[i][0])
            self.subplots[i].set_xlabel(PopulationGraphicsWindow.TEXTS[i][1])
            self.subplots[i].set_ylabel(PopulationGraphicsWindow.TEXTS[i][2])
            self.subplots[i].legend(loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)


class SpreadGraphicsWindow(GraphicsWindow):
    COLOURS = [['royalblue', 'dodgerblue', 'skyblue', 'paleturquoise', 'lemonchiffon', 'khaki', 'darkorange', 'orangered'], ['saddlebrown', 'chocolate', 'darkgoldenrod', 'goldenrod', 'olive', 'darkolivegreen', 'forestgreen', 'darkgreen']]
    TEXTS = [["Spreading of ", "Tick", "Number of Creatures in 100 chunks"], ["Percentual spreading of ", "Tick", "Percentage of Creatures"]]
    LABELS = ["-100 <> -75", "-75 <> -50", "-50 <> -25", "-25 <> 0", "0 <> 25", "25 <> 50", "50 <> 75", "75 <> 100"]

    def __init__(self, file, subj, father):
        GraphicsWindow.__init__(self, file, subj, father, 2)
        self.data_setup()
        if self.subject == "foodmax":
            color = 1
        else:
            color = 0
        self.subplots[0].fill_between(self.data[0], self.data[2], color=SpreadGraphicsWindow.COLOURS[color][0], label=SpreadGraphicsWindow.LABELS[0])
        for i in range(1, 8):
            self.subplots[0].fill_between(self.data[0], self.data[(i + 1) * 2], self.data[i * 2], color=SpreadGraphicsWindow.COLOURS[color][i], label=SpreadGraphicsWindow.LABELS[i])
        self.subplots[1].fill_between(self.data[0], self.data[17], color=SpreadGraphicsWindow.COLOURS[color][0], label=SpreadGraphicsWindow.LABELS[0])
        for i in range(17, 24):
            self.subplots[1].fill_between(self.data[0], self.data[i + 1], self.data[i], color=SpreadGraphicsWindow.COLOURS[color][i - 16], label=SpreadGraphicsWindow.LABELS[i - 16])
        self.set_titles()
        self.stat_axes_set()
        self.canvas.draw()
        self.update()

    def data_setup(self):
        for i in range(8):
            self.data.append([])
        for i in range(len(self.data[0])):
            for j in range(4, 17, 2):
                self.data[j][i] += self.data[j - 2][i]
            for j in range(2, 17, 2):
                self.data[int(j / 2) + 16].append(self.data[j][i] / self.data[16][i] * 100)

    def set_titles(self):
        for i in range(2):
            self.subplots[i].set_title(f"{SpreadGraphicsWindow.TEXTS[i][0]}{self.subject}")
            self.subplots[i].set_xlabel(SpreadGraphicsWindow.TEXTS[i][1])
            self.subplots[i].set_ylabel(SpreadGraphicsWindow.TEXTS[i][2])
            handles, labels = self.subplots[i].get_legend_handles_labels()
            self.subplots[i].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)'''


