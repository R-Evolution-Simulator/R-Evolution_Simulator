# import vari
import tkinter as tk
from math import ceil
from time import time

import matplotlib
import pygame as pyg
from PIL import ImageDraw, Image as Img

from . import frames as frm
from . import utility as utl

matplotlib.use("Tkagg")


class BaseTkWindow(tk.Tk):
    FRAMES = None
    TITLE = None

    def __init__(self, father):
        super(BaseTkWindow, self).__init__()
        self.father = father
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(self.TITLE)

    def on_closing(self):
        self.destroy()

    def get_widget(self, frame, name):
        return self.frames[frame].widgets[name]

    def frames_load(self):
        self.frames = {}
        for i in self.FRAMES:
            new = self.FRAMES[i][0](self, **self.FRAMES[i][1])
            new.grid(**self.FRAMES[i][2])
            self.frames[i] = new


class LoadWindow(BaseTkWindow):
    """Loading interface for simulation replay"""
    TITLE = "Simulation Load"

    def __init__(self, father, sim_name=None):
        self.FRAMES = {'load': (frm.Load, {'windows': (self,)}, {'row': 0, 'column': 0})}
        super(LoadWindow, self).__init__(father)
        self.frames_load()
        if sim_name:
            self.simulation_file_load(sim_name)

    def simulation_file_load(self, sim_name=None):
        """method which upload the data of the simulation"""
        if sim_name:
            self.sim_name = sim_name
        else:
            self.sim_name = self.get_widget('load', 'entry').get()
        self.father.main_window = CanvasWindow(self.father, self.sim_name)
        self.destroy()


class CanvasWindow(object):
    FILES_TO_LOAD = ['simulationData', 'chunkData', 'creaturesData']
    START_SCREEN = (100, 100)
    START_TICK = 1.0
    START_ZOOM = 10
    START_SPEED = 1
    START_IS_PLAYING = False
    START_SHOWS = {'ch': 'FM', 'cc': 'TR', 'cd': 'E'}
    MAX_SPEED = 100

    def __init__(self, father, sim_name):
        self.father = father
        self.sim_name = sim_name
        self.surface = pyg.display.set_mode(self.START_SCREEN)
        self.tick = self.START_TICK
        self.zoom = self.START_ZOOM
        self.speed = self.START_SPEED
        self.isPlaying = self.START_IS_PLAYING
        self.max_speed = self.MAX_SPEED
        self.last_frame_time = time()
        self._files_load()
        self._background_creation()
        self.control_window = ControlWindow(self)
        self.shows = dict()
        for i in self.START_SHOWS:
            self.shows[i] = tk.StringVar(master=self.control_window)
            self.shows[i].set(self.START_SHOWS[i])
        self.resize(0)
        self.control_window.frames_load()

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

    def _background_creation(self):
        """method which creates the background of the world"""
        image_food = Img.new("RGB", (int(self.sim_width / 10), int(self.sim_height / 10)))
        draw_food = ImageDraw.Draw(image_food)
        image_temp = Img.new("RGB", (int(self.sim_width / 10), int(self.sim_height / 10)))
        draw_temp = ImageDraw.Draw(image_temp)

        for chunk in self.chunk_list:
            draw_food.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                                fill=(0, int(chunk.foodMax * 255 / 100), 0))
            if chunk.temperature > 0:
                draw_temp.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                                    fill=(255, int(255 - (chunk.temperature / 100 * 255)), int(255 - (chunk.temperature / 100 * 255))))
            else:
                draw_temp.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                                    fill=(int(255 + (chunk.temperature / 100 * 255)), int(255 + (chunk.temperature / 100 * 255)), 255))

        image_food.save(f"{self.sim_name}/backgroundFM.gif", "GIF")
        image_temp.save(f"{self.sim_name}/backgroundT.gif", "GIF")

        self.backgrounds = {"FM": utl.img_load(f"{self.sim_name}/backgroundFM.gif"), "T": utl.img_load(f"{self.sim_name}/backgroundT.gif")}
        del image_temp, image_food, draw_food, draw_temp

    def resize(self, coeff):
        """method which set to selected zoom"""
        self.zoom = max(1, self.zoom + coeff)
        self.resized_backgrounds = dict()
        for i in self.backgrounds:
            self.resized_backgrounds[i] = utl.img_resize(self.backgrounds[i], self.zoom)
        self.surface = pyg.display.set_mode((int(self.sim_width * self.zoom / 10), int(self.sim_height * self.zoom / 10)))
        self.update()

    def change_speed(self, speed_exp):
        self.speed = int(self.max_speed ** (float(speed_exp) / 100))
        return self.speed

    def play(self):
        self.last_frame_time = time()
        while self.isPlaying:
            self.update()
            time_diff = time() - self.last_frame_time
            self.last_frame_time = time()
            self.tick += time_diff * self.speed
            if int(self.tick) >= self.max_tick:
                self.control_window.start_play()
                break
            self.control_window.set_fps(round(1.0 / time_diff, 1))
            self.control_window.update()

    def set_tick(self, tick):
        self.tick = tick
        self.update()

    def update(self):
        """function which updates the screen"""
        self.chunk_display()
        self.creatures_display()
        new_graph_tick = ceil(int(self.tick) / 100) * 100
        '''for window in self.diagram_windows:
            if window.show_tick:
                window.tick_line_set()
        if new_graph_tick != self.graph_tick:
            self.graph_tick = new_graph_tick
            for window in self.diagram_windows:
                if window.follow_play:
                    window.dyn_axes_set()'''
        try:
            self.control_window.update_tick(self.tick)
        except AttributeError:
            pass
        pyg.display.update()

    def chunk_display(self):
        """function which rapresents the chunks"""
        to_show = self.shows['ch'].get()
        if to_show == "F":  # con il cibo in un certo momento
            for chunk in self.chunk_list:
                chunk.draw(self.surface, self.tick, self.chunk_dim, self.zoom)
        else:
            self.surface.blit(self.resized_backgrounds[to_show], (0, 0))

    def creatures_display(self):
        """function which rapresents the creatures"""

        def tick_creature_list():
            L = []
            for i in self.creature_list:
                if i.birthTick <= int(self.tick) <= i.deathTick:
                    L.append(i)
            return L

        color = self.shows['cc'].get()
        dim = self.shows['cd'].get()

        for creature in tick_creature_list():
            creature.draw(self.surface, int(self.tick), color, dim, self.zoom)

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

    def on_closing(self):
        """function which closes the graphic window"""
        '''for window in self.diagram_windows:
            window.destroy()
        self.destroy()'''


class ControlWindow(BaseTkWindow):
    """class of the main window"""
    TITLE = "Replay Toolbar"
    MAX_SPEED = 100
    DEFAULT_GRAPH_TICK = 100

    def __init__(self, canvas):
        self.canvas = canvas
        self.FRAMES = {'play_control': (frm.PlayControl, {'windows': (self, self.canvas)}, {'row': 1, 'column': 0}),
                       'map_set': (frm.SetSuperFrame, {'windows': (self, self.canvas)}, {'row': 0, 'column': 1}), }
        super(ControlWindow, self).__init__(self.canvas)
        self.graph_tick = self.DEFAULT_GRAPH_TICK
        self.diagram_windows = []

    def speed_change(self, speed_cursor):
        """
        method which allow to change the speed of the simulation reproduction
        """
        self.get_widget('play_control', 'speed_label').config(text=f"T/s: {self.canvas.change_speed(speed_cursor):02d}")

    def dec_zoom(self):
        """method which decrease the zoom"""
        self.canvas.resize(-1)
        self.set_zoom()

    def inc_zoom(self):
        """method which increase the zoom"""
        self.canvas.resize(1)
        self.set_zoom()

    def set_zoom(self):
        """method which set to selected zoom"""
        self.get_widget('play_control', 'zoom').configure(text=f"zoom: {self.canvas.zoom}0%")

    def start_play(self):
        """method which starts or stops the reproduction of the simulation"""
        self.canvas.isPlaying = not (self.canvas.isPlaying)
        if self.canvas.isPlaying:
            self.get_widget('play_control', 'play').config(text="Pause")
            self.update()
            self.canvas.play()
        else:
            self.get_widget('play_control', 'play').config(text="Play")
            self.update()

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
            self.canvas.set_tick(int(self.get_widget('play_control', 'tick_entry').get()))
        except ValueError:
            pass

    def update_tick(self, tick):
        self.get_widget('play_control', 'tick_label').config(text=f"Tick: {int(tick):04d}")


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


class ChunkD:
    def __init__(self, chunk_data_line):
        chunk_data = chunk_data_line.split(';')
        self.coord = [int(chunk_data[0]), int(chunk_data[1])]
        self.foodMax = float(chunk_data[2])
        self.growthRate = float(chunk_data[3])
        self.temperature = float(chunk_data[4])
        self.foodHistory = chunk_data[5].split(',')
        for i in range(len(self.foodHistory)):
            self.foodHistory[i] = int(self.foodHistory[i])

    def draw(self, surface, tick, chunk_dim, zoom):
        pyg.draw.rect(surface, pyg.Color(0, int(self.foodHistory[int(tick) - 1] * 255 / 100), 0, 255),
                      pyg.Rect(self.coord[0] * chunk_dim * zoom / 10, self.coord[1] * chunk_dim * zoom / 10, chunk_dim * zoom / 10, chunk_dim * zoom / 10))


class CreaturesD:
    DEFAULT_COLORS = {'N': pyg.Color(255, 255, 255, 255),
                      'S': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                      'TR': {'c': pyg.Color(255, 0, 0, 255), 'l': pyg.Color(0, 0, 255, 255), 'N': pyg.Color(128, 128, 128, 255), 'n': pyg.Color(255, 255, 255, 255)}}
    DEFAULT_DIMS = {'N': 7, 'A': 5, 'B': 7, 'EC': 42, 'NCG': 9, 'S': 5}

    def __init__(self, line):
        data_list = line.split(";")
        self.ID = int(data_list[0])
        self.birthTick = int(data_list[1])
        self.parentsID = (int(data_list[2].split(",")[0]), int(data_list[2].split(",")[1]))
        self.tempResistGen = data_list[3]
        self.agility = float(data_list[4])
        self.bigness = float(data_list[5])
        self.sex = int(data_list[6])
        self.fertility = float(data_list[7])
        self.tempResist = data_list[8]
        self.speed = float(data_list[9])
        self.eatCoeff = float(data_list[10])
        self.numControlGene = float(data_list[11])
        self.deathTick = float(data_list[12])
        self.deathCause = data_list[13]
        data_list[14] = data_list[14].split("/")
        for i in range(len(data_list[14])):
            data_list[14][i] = data_list[14][i].split(",")
            try:
                for j in [0, 1]:
                    data_list[14][i][j] = float(data_list[14][i][j])
                for j in [2, 3]:
                    data_list[14][i][j] = int(data_list[14][i][j])
            except ValueError:
                data_list[14] = [[]]
        self.tickHistory = data_list[14]
        self.colors = dict()
        self.dims = dict()
        self.color_dims_creation()

    def color_dims_creation(self):
        self.colors["N"] = self.DEFAULT_COLORS['N']
        self.colors["S"] = self.DEFAULT_COLORS['S'][self.sex]

        self.colors["TR"] = self.DEFAULT_COLORS['TR'][self.tempResist]

        self.dims["N"] = self.DEFAULT_DIMS['N']
        self.dims["A"] = self.agility / self.DEFAULT_DIMS['A']
        self.dims["B"] = self.bigness / self.DEFAULT_DIMS['B']
        self.dims["EC"] = self.eatCoeff * self.DEFAULT_DIMS['EC']
        self.dims["NCG"] = self.numControlGene / self.DEFAULT_DIMS['NCG']
        self.dims["S"] = self.speed * self.DEFAULT_DIMS['S']

    def draw(self, surface, tick, color, dim, zoom):
        birth = max(self.birthTick, 1)
        coord = (int((self.tickHistory[tick - birth][0]) * zoom / 10), int(self.tickHistory[tick - birth][1] * zoom / 10))
        if dim == 'E':
            pyg.draw.circle(surface, self.colors[color], coord, int(self.tickHistory[tick - birth][2] / 10 * zoom / 10))
        else:
            pyg.draw.circle(surface, self.colors[color], coord, int(self.dims[dim] * zoom / 10))
