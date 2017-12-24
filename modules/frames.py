import tkinter as tk
from . import var
import os
import matplotlib as mpl
from matplotlib.figure import Figure

mpl.use("Tkagg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BaseFrame(tk.Frame):
    WIDGETS = None

    def __init__(self, father):
        super(BaseFrame, self).__init__(father)
        self.widgets = dict()
        self._widgets_load(self.WIDGETS)

    def _widgets_load(self, wid_list):
        for i in wid_list:
            new = wid_list[i][0](self, **wid_list[i][1])
            new.pack(**wid_list[i][2])
            self.widgets[i] = new

    def get_widget(self, widget):
        return self.widgets[widget]


class GridFrame(BaseFrame):
    def _widgets_load(self, wid_list):
        for i in wid_list:
            new = wid_list[i][0](self, **wid_list[i][1])
            new.grid(**wid_list[i][2])
            self.widgets[i] = new


class BaseLabelFrame(tk.LabelFrame, BaseFrame):
    def __init__(self, father):
        super(BaseLabelFrame, self).__init__(father, text=self.NAME)
        self.widgets = dict()
        self._widgets_load(self.WIDGETS)


class BaseSelectFrame(BaseLabelFrame):
    def __init__(self, father, windows):
        for i in self.WIDGETS:
            if self.WIDGETS[i][0] == tk.Radiobutton:
                self.WIDGETS[i][1]['variable'] = windows[0].shows[self.CODE]
                self.WIDGETS[i][1]['command'] = windows[0].update
                self.WIDGETS[i][1]['value'] = i
                self.WIDGETS[i][2] = {'anchor': tk.W}
        windows[0].shows[self.CODE].set(self.START_SHOW)
        super(BaseSelectFrame, self).__init__(father)


class BaseDiagramCanvasFrame(BaseFrame):
    def __init__(self, father, sim_name, subject, subplots=1):
        """funzione per la rappresentazione del canvas dove porre il grafico"""
        self.figure = Figure()
        # ricordati SHOW E DRAW di self.canvas
        self.WIDGETS = {
            'canvas': (FigureCanvasTkAgg, {'figure': self.figure, 'master': self}, {'fill': tk.BOTH, 'expand': True})}
        self.father = father
        self.sim_name = sim_name
        self.subject = subject
        self.widgets = dict()
        self.subplots = []
        self.tick_lines = []
        self.data = None
        self.subplot_creation(subplots)
        super(BaseDiagramCanvasFrame, self).__init__(father)
        self.data_init()
        self.data_calc()
        self.set_subplot()
        self.set_titles()
        self.stat_axes_set(father.father.max_tick)

    def stat_axes_set(self, max_tick):
        for subplot in self.subplots:
            subplot.set_xlim([0, max_tick])

    def data_init(self):
        """funzione per la lettura dei file con i dati"""
        file = open(os.path.join(var.SIMULATIONS_PATH, self.sim_name, f"{self.subject}.csv"))
        self.data = [[] for i in range(len(file.readline().split(';')))]
        file.seek(0)
        for line in file:
            line_list = line.split(';')
            line_list[-1] = line_list[-1][:-1]
            for i in range(len(self.data)):
                self.data[i].append(float(line_list[i]))

    def _widgets_load(self, wid_list):
        for i in wid_list:
            new = wid_list[i][0](**wid_list[i][1])
            new.show()
            wid = new.get_tk_widget()
            wid.pack(**wid_list[i][2])
            self.widgets[i] = new

    def subplot_creation(self, subplots):
        """funzione per la creazione delle coordinate delle linee"""
        for i in range(subplots):
            self.subplots.append(self.figure.add_subplot(subplots, 1, i + 1))

    def dyn_axes_set(self, tick):
        for subplot in self.subplots:
            subplot.set_xlim([tick - self.father.tick_difference, tick])

    def add_show_tick(self, tick):
        for subplot in self.subplots:
            self.tick_lines.append(subplot.axvline(x=tick))

    def remove_show_tick(self):
        for line in self.tick_lines:
            line.remove()
        self.tick_lines = []

    def tick_line_set(self, tick):
        for line in self.tick_lines:
            line.set_xdata(tick)


class Logo(BaseFrame):
    START_LOGO = "data/logo.gif"

    def __init__(self, father):
        self.photo = tk.PhotoImage(file=os.path.join(os.getcwd(), self.START_LOGO))
        self.WIDGETS = {'image': (tk.Label, {'image': self.photo}, {})}
        super(Logo, self).__init__(father)


class MainMenuOptions(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'new': (tk.Button, {'text': "New simulation", 'command': windows[0].new_sim_window}, {}),
                        'load': (tk.Button, {'text': "Load simulation", 'command': windows[0].load_sim_window}, {})
                        }
        super(MainMenuOptions, self).__init__(father)


class LoadSim(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'entry': (tk.Entry, {}, {}),
                        'button': (
                        tk.Button, {'text': "Load", 'command': windows[0].simulation_file_load}, {'side': tk.RIGHT}),
                        'label': (tk.Label, {'text': "Insert simulation name"}, {'side': tk.LEFT})}
        super(LoadSim, self).__init__(father)


class NewSim(GridFrame, BaseFrame):
    def __init__(self, father):
        self.name_var = tk.StringVar()
        self.WIDGETS = {'name_label': (tk.Label, {'text': 'name'}, {'row': 0, 'column': 0}),
                        'name': (tk.Entry, {'textvariable': self.name_var}, {'row': 0, 'column': 1})}
        self.variables = dict()
        self.row = 0
        for i in var.DFEAULT_SIM_VARIABLES:
            self.variables[i] = self._add_widget(i, var.DFEAULT_SIM_VARIABLES[i], 0)
        super(NewSim, self).__init__(father)

    def _add_widget(self, name, object, column):
        self.WIDGETS[f'{name}_label'] = (tk.Label, {'text': name}, {'row': self.row, 'column': column})
        if type(object) == int or type(object) == float:
            variable = tk.StringVar()
            variable.set(str(object))
            self.WIDGETS[name] = (tk.Entry, {'textvariable': variable}, {'row': self.row, 'column': column + 1})
            self.row += 1
        elif type(object) == tuple or type(object) == list:
            variable = list()
            for i in range(len(object)):
                new_variable = tk.StringVar()
                new_variable.set(str(object[i]))
                variable.append(new_variable)
                self.WIDGETS[f'{name}_{i}'] = (
                tk.Entry, {'textvariable': new_variable}, {'row': self.row, 'column': column + i + 1})
            self.row += 1
        else:
            variable = dict()
            for i in object:
                variable[i] = self._add_widget(i, object[i], column + 1)
        return variable


class PlayControl(BaseFrame):
    def __init__(self, father):
        self.WIDGETS = {'play': (tk.Button, {'text': "Play", 'command': father.start_play}, {'side': tk.TOP}),
                        'fps': (tk.Label, {'text': "fps: 00.0"}, {'side': tk.TOP}),
                        'tick_entry': (tk.Spinbox, {'from_': 1, 'to': father.max_tick, 'width': 15}, {'side': tk.TOP}),
                        'tick_button': (tk.Button, {'text': "Set tick", 'command': father.set_tick}, {'side': tk.TOP}),
                        'tick_label': (tk.Label, {'text': "Tick: 1"}, {'side': tk.TOP}),
                        'speed_slider': (
                        tk.Scale, {'orient': tk.HORIZONTAL, 'showvalue': False, 'command': father.speed_change},
                        {'side': tk.TOP}),
                        'speed_label': (tk.Label, {'text': f"Tick/s: {father.speed}"}, {'side': tk.TOP}),
                        'inc_zoom': (tk.Button, {'text': "+ 10%", 'command': father.inc_zoom}, {'side': tk.TOP}),
                        'zoom': (tk.Label, {'text': f"zoom: {father.zoom}0%"}, {'side': tk.TOP}),
                        'dec_zoom': (tk.Button, {'text': "- 10%", 'command': father.dec_zoom}, {'side': tk.TOP}), }
        super(PlayControl, self).__init__(father)


class ChunksSet(BaseSelectFrame):
    NAME = "Chunk"
    CODE = 'ch'
    START_SHOW = 'FM'
    WIDGETS = {'FM': [tk.Radiobutton, {'text': "Food Max"}, {}],
               'T': [tk.Radiobutton, {'text': "Temperature"}, {}],
               'F': [tk.Radiobutton, {'text': "Food"}, {}], }


class CreatureColorSet(BaseSelectFrame):
    NAME = "Color"
    CODE = 'cc'
    START_SHOW = 'TR'
    WIDGETS = {'N': [tk.Radiobutton, {'text': "None"}, {}],
               'S': [tk.Radiobutton, {'text': "Sex"}, {}],
               'TR': [tk.Radiobutton, {'text': "Temp Resist"}, {}], }


class CreatureDimSet(BaseSelectFrame):
    NAME = "Dimension"
    CODE = 'cd'
    START_SHOW = 'E'
    WIDGETS = {'N': [tk.Radiobutton, {'text': "None"}, {}],
               'E': [tk.Radiobutton, {'text': "Energy"}, {}],
               'A': [tk.Radiobutton, {'text': "Agility"}, {}],
               'B': [tk.Radiobutton, {'text': "Bigness"}, {}],
               'EC': [tk.Radiobutton, {'text': "Eat Coeff"}, {}],
               'S': [tk.Radiobutton, {'text': "Speed"}, {}],
               'NCG': [tk.Radiobutton, {'text': "Num Control Gene"}, {}], }


class CreatureSet(BaseLabelFrame):
    NAME = "Creatures"

    def __init__(self, father, windows):
        self.WIDGETS = {'cl': (CreatureColorSet, {'windows': windows}, {'side': tk.TOP, 'anchor': tk.NW, 'fill': tk.X}),
                        'dim': (CreatureDimSet, {'windows': windows}, {'side': tk.TOP, 'anchor': tk.NW, 'fill': tk.X}),
                        }
        super(CreatureSet, self).__init__(father)


class DiagramSet(BaseFrame):
    CHOICES = ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed', 'population', 'foodmax',
               'temperature_c', 'temperature_l', 'temperature_N']

    def __init__(self, father, windows):
        self.father = father
        self.WIDGETS = {
            'new': (tk.Button, {'text': "New Diagram", 'command': windows[0].graphics_window_create}, {'anchor': tk.W})}
        self.diagram_choice = windows[0].diagram_choice
        self.diagram_choice.set('agility')
        super(DiagramSet, self).__init__(father)

    def _widgets_load(self, wid_list):
        self.widgets = dict()
        self.widgets['menu'] = tk.OptionMenu(self, self.diagram_choice, *self.CHOICES)
        self.widgets['menu'].pack(anchor=tk.W, fill=tk.X)
        for i in wid_list:
            new = wid_list[i][0](self, **wid_list[i][1])
            new.pack(**wid_list[i][2])
            self.widgets[i] = new


class SetSuperFrame(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'ch': (ChunksSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'cr': (CreatureSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'dgrm': (DiagramSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X})
                        }
        super(SetSuperFrame, self).__init__(father)


class DiagramCommandBar(BaseFrame):
    TICK_DIFFERENCE_FROM = 100
    TICK_DIFFERENCE_INCREMENT = 100

    def __init__(self, father, windows):
        self.WIDGETS = {'follow_play': (
        tk.Checkbutton, {'text': "Follow play", 'command': windows[0].change_follow_play}, {'side': tk.LEFT}),
                        'tick_difference': (tk.Spinbox, {'from_': self.TICK_DIFFERENCE_FROM, 'to': windows[1].max_tick,
                                                         'increment': self.TICK_DIFFERENCE_INCREMENT,
                                                         'command': windows[0].tick_difference_set}, {'side': tk.LEFT}),
                        'show_tick': (tk.Checkbutton, {'text': "Show tick", 'command': windows[0].change_show_tick},
                                      {'side': tk.LEFT}),
                        }
        super(DiagramCommandBar, self).__init__(father)


class GeneDiagram(BaseDiagramCanvasFrame):
    COLOURS = ['dimgray', 'lightgrey', 'darkgray', 'lightgrey', 'dimgray', 'red']
    TEXTS = [["", "Tick", ""]]
    LABELS = ["Minimum", "25% percentile", "Median", "75% percentile", "Maximum", "Average"]

    def data_calc(self):
        pass

    def set_subplot(self):
        for i in range(len(self.data) - 1):
            self.subplots[0].plot(self.data[0], self.data[i + 1], color=self.COLOURS[i], label=self.LABELS[i])

    def set_titles(self):
        self.subplots[0].set_title(self.subject)
        self.subplots[0].set_xlabel(self.TEXTS[0][1])
        self.subplots[0].set_ylabel(self.subject)
        handles, labels = self.subplots[0].get_legend_handles_labels()
        self.subplots[0].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)


class PopulationDiagram(BaseDiagramCanvasFrame):
    COLOURS = [['darkgreen', 'saddlebrown'], ['peru', 'lightskyblue', 'lightgreen']]
    TEXTS = [["Births and Deaths", "Tick", "Number of Creatures"], ["Causes of Death", "Tick", "Number of Creatures"]]
    LABELS = [["Births", "Deaths"], ["Starvation", "Temperature", "Old Age"]]
    SUBPLOTS = 2

    def __init__(self, father, sim_name, subject):
        super(PopulationDiagram, self).__init__(father, sim_name, subject, self.SUBPLOTS)

    def data_calc(self):
        self.data.append(list())
        for i in range(len(self.data[0])):
            self.data[5].append(self.data[2][i] + self.data[3][i] + self.data[4][i])

    def set_subplot(self):
        self.subplots[0].plot(self.data[0], self.data[1], color=self.COLOURS[0][0], label=self.LABELS[0][0])
        self.subplots[0].plot(self.data[0], self.data[5], color=self.COLOURS[0][1], label=self.LABELS[0][1])
        for i in range(3):
            self.subplots[1].plot(self.data[0], self.data[i + 2], color=self.COLOURS[1][i], label=self.LABELS[1][i])

    def set_titles(self):
        for i in range(2):
            self.subplots[i].set_title(self.TEXTS[i][0])
            self.subplots[i].set_xlabel(self.TEXTS[i][1])
            self.subplots[i].set_ylabel(self.TEXTS[i][2])
            self.subplots[i].legend(loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)


class SpreadDiagram(BaseDiagramCanvasFrame):
    COLOURS = [
        ['royalblue', 'dodgerblue', 'skyblue', 'paleturquoise', 'lemonchiffon', 'khaki', 'darkorange', 'orangered'],
        ['saddlebrown', 'chocolate', 'darkgoldenrod', 'goldenrod', 'olive', 'darkolivegreen', 'forestgreen',
         'darkgreen']]
    TEXTS = [["Spreading of ", "Tick", "Number of Creatures in 100 chunks"],
             ["Percentual spreading of ", "Tick", "Percentage of Creatures"]]
    LABELS = ["-100 <> -75", "-75 <> -50", "-50 <> -25", "-25 <> 0", "0 <> 25", "25 <> 50", "50 <> 75", "75 <> 100"]
    SUBPLOTS = 2

    def __init__(self, father, sim_name, subject):
        super(SpreadDiagram, self).__init__(father, sim_name, subject, self.SUBPLOTS)

    def data_calc(self):
        for i in range(8):
            self.data.append([])
        for i in range(len(self.data[0])):
            for j in range(4, 17, 2):
                self.data[j][i] += self.data[j - 2][i]
            for j in range(2, 17, 2):
                self.data[int(j / 2) + 16].append(self.data[j][i] / self.data[16][i] * 100)

    def set_subplot(self):
        if self.subject == "foodmax":
            color = 1
        else:
            color = 0
        self.subplots[0].fill_between(self.data[0], self.data[2], color=self.COLOURS[color][0], label=self.LABELS[0])
        for i in range(1, 8):
            self.subplots[0].fill_between(self.data[0], self.data[(i + 1) * 2], self.data[i * 2],
                                          color=self.COLOURS[color][i], label=self.LABELS[i])
        self.subplots[1].fill_between(self.data[0], self.data[17], color=self.COLOURS[color][0], label=self.LABELS[0])
        for i in range(17, 24):
            self.subplots[1].fill_between(self.data[0], self.data[i + 1], self.data[i],
                                          color=self.COLOURS[color][i - 16], label=self.LABELS[i - 16])

    def set_titles(self):
        for i in range(2):
            self.subplots[i].set_title(f"{self.TEXTS[i][0]}{self.subject}")
            self.subplots[i].set_xlabel(self.TEXTS[i][1])
            self.subplots[i].set_ylabel(self.TEXTS[i][2])
            handles, labels = self.subplots[i].get_legend_handles_labels()
            self.subplots[i].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)
