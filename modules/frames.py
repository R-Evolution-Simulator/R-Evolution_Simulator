"""
This modulo contains classes for the frames used to allow the user to creat,
represent and control a simulation
"""

import tkinter as tk
from . import var
from . import utility as utl
import os
import matplotlib as mpl
from matplotlib.figure import Figure
from tkinter import ttk
mpl.use("Tkagg")
mpl.use('agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BaseFrame(tk.Frame):
    """general class of a frame"""
    WIDGETS = None  # list of the widgets present in the frame

    def __init__(self, father):
        """
        creates a new frame

        :param father: the father window
        """
        super(BaseFrame, self).__init__(father)
        self.widgets = dict()  # dictionary with all the widget
        self._widgets_load(self.WIDGETS)

    def _widgets_load(self, wid_list):
        """
        it loads the widget in the frame

        :param wid_list: list with all the widgets to be added

        :return:
        """
        for i in wid_list:
            new = wid_list[i][0](self, **wid_list[i][1])
            new.pack(**wid_list[i][2])
            self.widgets[i] = new

    def get_widget(self, widget):
        """
        it used to get a certain form the frame

        :param widget: widget to be got
        :return: the widget considered
        """
        return self.widgets[widget]


class GridFrame(BaseFrame):
    """
    class derived from BaseFrame which uses the method .grid instead of .pack
    when placing a widget in the frame
    """

    def _widgets_load(self, wid_list):
        """
        it loads the widget in the frame

        :param wid_list: list with all the widgets to be added

        :return:
        """
        for i in wid_list:
            new = wid_list[i][0](self, **wid_list[i][1])
            new.grid(**wid_list[i][2])
            self.widgets[i] = new


class BaseLabelFrame(tk.LabelFrame, BaseFrame):
    """
    class with a frame for the label widget
    """

    def __init__(self, father):
        """
        it creates the frame

        :param father: father window
        """
        super(BaseLabelFrame, self).__init__(father, text=self.NAME)
        self.widgets = dict()
        self._widgets_load(self.WIDGETS)


class BaseSelectFrame(BaseLabelFrame):
    """
    class used for frames with selection widget
    """

    def __init__(self, father, windows):
        """
        it creates the frame

        :param father: the father window
        :param windows:
        """
        for i in self.WIDGETS:
            if self.WIDGETS[i][0] == tk.Radiobutton:
                self.WIDGETS[i][1]['variable'] = windows[0].shows[self.CODE]
                self.WIDGETS[i][1]['command'] = windows[0].update
                self.WIDGETS[i][1]['text'] = self.WIDGETS[i][1]['value']
                self.WIDGETS[i][2] = {'anchor': tk.W}
        windows[0].shows[self.CODE].set(self.START_SHOW)
        super(BaseSelectFrame, self).__init__(father)


class Logo(BaseFrame):
    """
    frame used to place the logo of the project
    """
    START_LOGO = os.path.join(var.DATA_PATH, "logo.gif")

    def __init__(self, father):
        """
        it creates the frame

        :param father: father window
        """
        self.photo = tk.PhotoImage(file=os.path.join(os.getcwd(), self.START_LOGO))
        self.WIDGETS = {'image': (tk.Label, {'image': self.photo}, {})}
        super(Logo, self).__init__(father)


class MainMenuOptions(BaseFrame):
    """
    class for the options in the main menu: creating a new simulation or loading some already done
    """

    def __init__(self, father, windows):
        """
        created the menu

        :param father: the father window
        :param windows:
        """
        self.WIDGETS = {'new': (tk.Button, {'text': "New simulation", 'command': windows[0].new_sim_window}, {}),
                        'load': (tk.Button, {'text': "Load simulation", 'command': windows[0].load_sim_window}, {})
                        }
        super(MainMenuOptions, self).__init__(father)


class LoadSim(BaseFrame):
    """
    frame used to load a simulation (by inserting the name)
    """

    def __init__(self, father, windows):
        """
        created the frame

        :param father: the father window
        :param windows:
        """
        self.WIDGETS = {'entry': (tk.Entry, {}, {}),
                        'button': (
                            tk.Button, {'text': "Load", 'command': windows[0].simulation_file_load}, {'side': tk.RIGHT}),
                        'label': (tk.Label, {'text': "Insert simulation name"}, {'side': tk.LEFT})}
        super(LoadSim, self).__init__(father)
        self.widgets['entry'].focus_set()


class NewSim(GridFrame, BaseFrame):
    """
    class used to start a new simulation
    """

    def __init__(self, father):
        """
        it creates the frame

        :param father: the father window
        :param load_choice: list of the possible templates already created
        """
        super(BaseFrame, self).__init__(father)
        self.WIDGETS = dict()
        self.sim_variables = dict()
        self.load_choice = tk.StringVar(master=self)  # list of the possible templates
        self.load_choice.set('-')
        self.WIDGETS['name_label'] = (tk.Label, {'text': 'name'}, {'row': 0, 'column': 0})
        self.sim_name = tk.Entry(self)  # entry for chosing the name of the simulation
        self.sim_name.grid(row=0, column=1)
        self.WIDGETS['start_button'] = (tk.Button, {'text': "Start", 'command': father.start_simulation}, {'row': 0, 'column': 2})
        self.row = 1
        # for all the variables, the program adds the widgets
        for i in var.DEFAULT_SIM_VARIABLES:
            self.sim_variables[i] = self._add_widget(i, var.DEFAULT_SIM_VARIABLES[i], 0)
            self.row += 1
        # widget used to load a new template or to save another one just created
        self.WIDGETS['load_button'] = (tk.Button, {'text': "Load template", 'command': father.load_template}, {'row': self.row, 'column': 1})
        self.save_choice = tk.Entry(self)
        self.save_choice.grid(row=self.row, column=2)
        self.WIDGETS['save_button'] = (tk.Button, {'text': "Save template", 'command': father.save_template}, {'row': self.row, 'column': 3})
        self.widgets = dict()
        self._widgets_load(self.WIDGETS)

    def _add_widget(self, name, object, column):
        """
        function which adds a couple of widgets for every parameter of the world created

        :param name: name to be written in the label
        :param object: object that has to be inserted in the widgets
        :param column: column where the entry and label has to be placed (it increases with dict or list)
        :return: the entry where you can place the values
        """
        self.WIDGETS[f'{name}_label'] = (tk.Label, {'text': name}, {'row': self.row, 'column': column})
        if type(object) == int or type(object) == float:
            variable = tk.Entry(self)
            variable.grid(row=self.row, column=column + 1)
        elif type(object) == tuple or type(object) == list:
            variable = list()
            for i in range(len(object)):
                new_variable = tk.Entry(self)
                new_variable.grid(row=self.row, column=column + 1 + i)
                variable.append(new_variable)
        else:
            variable = dict()
            for i in object:
                variable[i] = self._add_widget(i, object[i], column + 1)
        self.row += 1
        return variable

    def _get_template_choices(self):
        """
        function to get the possible templates already created from the folder

        :return: the list of the templates
        """
        return os.listdir(var.TEMPLATES_PATH)

    def _widgets_load(self, wid_list):
        """
        it loads the widget in the frame

        :param wid_list: list with all the widgets to be added

        :return:
        """
        self.widgets = dict()
        self.widgets['load_options'] = tk.OptionMenu(self, self.load_choice, *self._get_template_choices())
        self.widgets['load_options'].grid(row=self.row, column=0)
        super(NewSim, self)._widgets_load(wid_list)


class PlayControl(BaseFrame):
    """
    class for the frame used to control the simulation
    """

    def __init__(self, father):
        """
        it creates the frame with all the widgets used

        :param father: th father window
        """
        self.WIDGETS = {'play': (tk.Button, {'text': "Play", 'command': father.start_play}, {'side': tk.TOP}),
                        'fps': (tk.Label, {'text': "fps: 00.0"}, {'side': tk.TOP}),
                        'tick_entry': (tk.Spinbox, {'from_': 1, 'to': father.lifetime, 'width': 15}, {'side': tk.TOP}),
                        'tick_button': (tk.Button, {'text': "Set tick", 'command': father.set_tick}, {'side': tk.TOP}),
                        'tick_label': (tk.Label, {'text': "Tick: 1"}, {'side': tk.TOP}),
                        'speed_slider': (
                            tk.Scale, {'orient': tk.HORIZONTAL, 'showvalue': False, 'command': father.set_speed},
                            {'side': tk.TOP}),
                        'speed_label': (tk.Label, {'text': f"Tick/s: {father.speed}"}, {'side': tk.TOP}),
                        'inc_zoom': (tk.Button, {'text': "+ 10%", 'command': father.inc_zoom}, {'side': tk.TOP}),
                        'zoom': (tk.Label, {'text': f"zoom: {father.zoom}0%"}, {'side': tk.TOP}),
                        'dec_zoom': (tk.Button, {'text': "- 10%", 'command': father.dec_zoom}, {'side': tk.TOP}), }
        super(PlayControl, self).__init__(father)


class ChunksSet(BaseSelectFrame):
    """
    class used in PlayControl for controlling the chunks' representation
    """
    NAME = "Chunk"
    CODE = 'ch'
    START_SHOW = 'foodmax'
    WIDGETS = {'FM': [tk.Radiobutton, {'value': "foodmax"}, {}],
               'T': [tk.Radiobutton, {'value': "temperature"}, {}],
               'F': [tk.Radiobutton, {'value': "food"}, {}], }


class CreatureColorSet(BaseSelectFrame):
    """
    class used in PlayControl for controlling the creatures' representation (for the color of the circles)
    """
    NAME = "Color"
    CODE = 'cc'
    START_SHOW = 'temp_resist'
    WIDGETS = {'N': [tk.Radiobutton, {'value': "none"}, {}],
               'S': [tk.Radiobutton, {'value': "sex"}, {}],
               'TR': [tk.Radiobutton, {'value': "temp_resist"}, {}],
               'MC': [tk.Radiobutton, {'value': "mndl_control"}, {}], }


class CreatureDimSet(BaseSelectFrame):
    """
    class used in PlayControl for controlling the creatures' representation (for the dimension of the circles)
    """
    NAME = "Dimension"
    CODE = 'cd'
    START_SHOW = 'energy'
    WIDGETS = {'N': [tk.Radiobutton, {'value': "none"}, {}],
               'E': [tk.Radiobutton, {'value': "energy"}, {}],
               'A': [tk.Radiobutton, {'value': "agility"}, {}],
               'B': [tk.Radiobutton, {'value': "bigness"}, {}],
               'S': [tk.Radiobutton, {'value': "speed"}, {}],
               'NCG': [tk.Radiobutton, {'value': "num_control"}, {}], }


class CreatureSet(BaseLabelFrame):
    """
    class used to place CreatureColorSet and CreatureDimSet
    """
    NAME = "Creatures"

    def __init__(self, father, windows):
        self.WIDGETS = {'cl': (CreatureColorSet, {'windows': windows}, {'side': tk.TOP, 'anchor': tk.NW, 'fill': tk.X}),
                        'dim': (CreatureDimSet, {'windows': windows}, {'side': tk.TOP, 'anchor': tk.NW, 'fill': tk.X}),
                        }
        super(CreatureSet, self).__init__(father)


class DiagramSet(BaseFrame):
    """
    class used to create the different types of graphs
    """

    SUPPORTED_FILES = ['numeric_analysis', 'spreading_analysis', 'demographic_analysis']

    def __init__(self, father, windows):
        """
        the frame is created

        :param father: the father window
        :param windows:
        """
        self.father = father
        self.windows = windows
        self.WIDGETS = {
            'new': (tk.Button, {'text': "New Diagram", 'command': self.windows[0].diagram_window_create}, {'anchor': tk.W})}
        self.diagram_choice = self.windows[0].diagram_choice
        self.diagram_choice.set('-')
        super(DiagramSet, self).__init__(father)

    def _get_choices(self):
        """
        it gets the possible characteristics that can be represented

        :return: the list of the possible choices
        """
        files = os.listdir(self.windows[0].directories['analysis'])
        choices = list()
        for file in files:
            ext = file.split('.')[-1]
            for i in self.SUPPORTED_FILES:
                if ext == var.FILE_EXTENSIONS[i]:
                    choices.append(file)
        return choices

    def _widgets_load(self, wid_list):
        """
        it loads the widget in the frame

        :param wid_list: list with all the widgets to be added

        :return:
        """
        self.widgets = dict()
        self.widgets['menu'] = tk.OptionMenu(self, self.diagram_choice, *self._get_choices())
        self.widgets['menu'].pack(anchor=tk.W, fill=tk.X)
        super(DiagramSet, self)._widgets_load(wid_list)


class SetSuperFrame(BaseFrame):
    """
    it is a frame for the set of widget divided by topic
    """

    def __init__(self, father, windows):
        """
        the frame is created

        :param father: the father window
        :param windows:
        """
        self.WIDGETS = {'ch': (ChunksSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'cr': (CreatureSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'dgrm': (DiagramSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X})
                        }
        super(SetSuperFrame, self).__init__(father)


class TakeScreenshot(BaseFrame):
    def __init__(self, father, windows):
        """
        the frame is created

        :param father: the father window
        :param windows:
        """
        self.WIDGETS = {'take_screen': (tk.Button, {'text': "Take screenshot", 'command': windows[0].take_screenshot}, {'anchor': tk.W}),
                        }
        super(TakeScreenshot, self).__init__(father)


class DiagramCommandBar(BaseFrame):
    """
    frame used to control a diagram (if it as to follow the etc.)
    """

    def __init__(self, father, windows, tick_interval):
        """
        the frame is created

        :param father: the father window
        :param windows:
        :param tick_interval: how many tick has to be represented
        """
        self.WIDGETS = {'follow_play': (tk.Checkbutton, {'text': "Follow play", 'command': windows[0].toggle_follow_play}, {'side': tk.LEFT}),
                        'graph_width': (tk.Spinbox, {'from_': tick_interval, 'to': windows[1].lifetime, 'increment': tick_interval, 'command': windows[0].graph_width_set}, {'side': tk.LEFT}),
                        'show_tick': (tk.Checkbutton, {'text': "Show tick", 'command': windows[0].change_show_tick}, {'side': tk.LEFT}),
                        'save_diagram': (tk.Button, {'text': "Save diagram", 'command': windows[0].save_diagram}, {'side': tk.LEFT})
                        }
        super(DiagramCommandBar, self).__init__(father)


class BaseDiagramCanvasFrame(BaseFrame):
    """
    class for the base canvas where has to placed a diagram
    """

    SUBPLOTS = 1

    def __init__(self, father, directories, subject, params):
        """
        Frame for Matplotlib diagrams

        :param father: the father window
        :param directory: the directory of the file
        :param subject: the subject of the diagram
        :param params: the analysis parameters of the simulation
        """
        self.figure = Figure()
        self.WIDGETS = {
            'canvas': (FigureCanvasTkAgg, {'figure': self.figure, 'master': self}, {'fill': tk.BOTH, 'expand': True})}
        self.father = father
        self.directories = directories
        self.subject = subject
        self.TITLE = subject.split('.')[0]
        self.params = params
        self.widgets = dict()
        self.subplots = []
        self.tick_lines = []
        self.data = None
        for i in range(self.SUBPLOTS):
            self.subplots.append(self.figure.add_subplot(self.SUBPLOTS, 1, i + 1))
        super(BaseDiagramCanvasFrame, self).__init__(father)
        self._data_init()
        self._data_calc()
        self._set_subplots()
        self._set_titles()
        self.stat_axes_set(father.father.lifetime)

    def _data_init(self):
        """
        Loads data form the analysis file

        :return:
        """
        raw_data = list()
        file = open(os.path.join(self.directories['analysis'], self.subject))
        for line in file:
            raw_data.append(utl.get_from_string(line, 0, None))
        self.data = [[raw_data[j][i] for j in range(len(raw_data))] for i in range(len(raw_data[0]))]

    def _data_calc(self):
        """
        Data elaboration

        :return:
        """
        pass

    def _set_subplots(self):
        """
        Sets up subplots

        :return:
        """
        pass

    def _set_titles(self):
        """
        Sets up titles

        :return:
        """
        pass

    def _widgets_load(self, wid_list):
        """
        it loads the widget in the frame

        :param wid_list: list with all the widgets to be added

        :return:
        """
        for i in wid_list:
            new = wid_list[i][0](**wid_list[i][1])
            new.show()
            wid = new.get_tk_widget()
            wid.pack(**wid_list[i][2])
            self.widgets[i] = new

    def stat_axes_set(self, max_tick):
        """
        function which limits the x axes of the plot in the static configuration

        :param max_tick: max tick represented in the plot

        :return:
        """
        for subplot in self.subplots:
            subplot.set_xlim([0, max_tick])

    def dyn_axes_set(self, tick):
        """
        function which limits the x axes of the plot in the dynamic configuration

        :param tick: tick considered

        :return:
        """
        for subplot in self.subplots:
            subplot.set_xlim([tick - self.father.graph_width, tick])

    def add_show_tick(self, tick):
        """
        function which represent a vertical line which indicates the actual tick

        :param tick: the tick considered

        :return:
        """
        for subplot in self.subplots:
            self.tick_lines.append(subplot.axvline(x=tick))

    def remove_show_tick(self):
        """
        it removes the line showing the actual tick

        :return:
        """
        for line in self.tick_lines:
            line.remove()
        self.tick_lines = []

    def tick_line_set(self, tick):
        """

        :param tick:
        :return:
        """
        for line in self.tick_lines:
            line.set_xdata(tick)

    def save_diagram(self):
        self.remove_show_tick()
        self.figure.savefig(os.path.join(self.directories['images'], "diagrams", self.subject + ".jpeg"))


class GeneDiagram(BaseDiagramCanvasFrame):
    """
    class for the diagrams of genes
    """

    COLOURS = ['dimgray', 'red', 'darkgray', 'lightgrey']
    TEXTS = [["", "Tick", ""]]
    LABELS = ["Average", "{percent}th percentile"]

    def _set_subplots(self):
        """
        it creates the subplots considering the number of percentile parts inserted

        :return:
        """
        parts = self.params['percentile_parts']
        for part in range(parts + 2):
            self.subplots[0].plot(self.data[0], self.data[part + 1], color=self._get_colour(part), label=self._get_label(part))

    def _get_colour(self, part):
        """
        function which returns the color of a certain line (percentile fixed)

        :param part: the part considered

        :return: the color
        """
        parts = self.params['percentile_parts']
        if part == 0 or part == parts:
            return self.COLOURS[0]
        elif part == parts + 1:
            return self.COLOURS[1]
        elif part == parts / 2:
            return self.COLOURS[2]
        else:
            return self.COLOURS[3]

    def _get_label(self, part):
        """
        it returns the label used it the legend

        :param part: percentile part considered

        :return: the string to be written in the label
        """
        parts = self.params['percentile_parts']
        if part == parts + 1:
            return self.LABELS[0]
        else:
            return self.LABELS[1].format(percent=(part / parts) * 100)

    def _set_titles(self):
        """
        function which sets the titles in the diagram

        :return:
        """
        self.subplots[0].set_title(self.TITLE)
        self.subplots[0].set_xlabel(self.TEXTS[0][1])
        self.subplots[0].set_ylabel(self.TITLE)
        handles, labels = self.subplots[0].get_legend_handles_labels()
        self.subplots[0].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)


class PopulationDiagram(BaseDiagramCanvasFrame):
    """
    class for the population diagram
    """
    COLOURS = [['darkgreen', 'saddlebrown'], ['peru', 'lightskyblue', 'lightgreen']]
    TEXTS = [["Births and Deaths", "Tick", "Number of Creatures"], ["Causes of Death", "Tick", "Number of Creatures"]]
    LABELS = [["Births", "Deaths"], ["Starvation", "Temperature", "Old Age"]]
    SUBPLOTS = 2

    def _data_calc(self):
        """
        function which evaluates the data to be represented

        :return:
        """
        self.data.append(list())
        for i in range(len(self.data[0])):
            self.data[5].append(self.data[2][i] + self.data[3][i] + self.data[4][i])

    def _set_subplots(self):
        """
        function which creates the subplots of the diagram

        :return:
        """
        self.subplots[0].plot(self.data[0], self.data[1], color=self.COLOURS[0][0], label=self.LABELS[0][0])
        self.subplots[0].plot(self.data[0], self.data[5], color=self.COLOURS[0][1], label=self.LABELS[0][1])
        for i in range(3):
            self.subplots[1].plot(self.data[0], self.data[i + 2], color=self.COLOURS[1][i], label=self.LABELS[1][i])

    def _set_titles(self):
        """
        function which creates the titles

        :return:
        """
        for i in range(2):
            self.subplots[i].set_title(self.TEXTS[i][0])
            self.subplots[i].set_xlabel(self.TEXTS[i][1])
            self.subplots[i].set_ylabel(self.TEXTS[i][2])
            self.subplots[i].legend(loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)


class SpreadDiagram(BaseDiagramCanvasFrame):
    """
    class for spreading diagrams
    """
    TEXTS = [["Spreading of ", "Tick", "Number of Creatures in 100 chunks"],
             ["Percentual spreading of ", "Tick", "Percentage of Creatures"]]
    SUBPLOTS = 2

    def _data_init(self):
        """
        Loads data form the analysis file

        :return:
        """
        raw_data = list()
        file = open(os.path.join(self.directories['analysis'], self.subject))
        for line in file:
            raw_data.append(utl.get_from_string(line, 0, None))
        self.chunk_attribute = raw_data[0][:-1]
        raw_data = raw_data[1:]
        self.data = [[raw_data[j][i] for j in range(len(raw_data))] for i in range(len(raw_data[0]))]

    def _data_calc(self):
        """
        elaborates the data

        :return:
        """
        parts = self.params['parts']
        for i in range(parts):
            self.data.append([])
        for i in range(len(self.data[0])):
            for j in range(parts + 1, 2 * parts):
                self.data[j + 1][i] += self.data[j][i]
            for j in range(parts + 1, 2 * parts + 1):
                try:
                    self.data[j + parts].append(self.data[j][i] / self.data[2 * parts][i] * 100)
                except ZeroDivisionError:
                    self.data[j + parts].append(0)

    def _set_subplots(self):
        """
        creates the subplots

        :return:
        """
        parts = self.params['parts']
        for subplot in range(2):
            self.subplots[subplot].fill_between(self.data[0], self.data[(subplot + 1) * parts + 1], color=self._get_colour(0), label=self._get_label(0))
            for part in range(1, parts):
                self.subplots[subplot].fill_between(self.data[0], self.data[(subplot + 1) * parts + 1 + part], self.data[(subplot + 1) * parts + part],
                                                    color=self._get_colour(part), label=self._get_label(part))

    def _get_colour(self, part):
        """
        gets the colour depending on what is represented

        :param part: the part considered

        :return: the RGB 3 numbers for the colour
        """
        parts = self.params['parts']
        if self.chunk_attribute == 'temperature':
            half = (parts - 1) / 2
            if part > half:
                return 1, ((parts - 1) - part) / half, ((parts - 1) - part) / half
            else:
                return part / half, part / half, 1
        elif self.chunk_attribute == 'foodmax':
            return 0, part / (parts - 1), 0

    def _get_label(self, part):
        """
        creates the string to be written in the legend

        :param part: the part considered

        :return: the string
        """
        parts = self.params['parts']
        max = self.father.father.chunks_vars[f'{self.chunk_attribute}_max']
        section = max / parts
        if self.chunk_attribute == 'temperature':
            section *= 2
            return f"{(section*part)-max} <> {(section*(part+1))-max}"
        elif self.chunk_attribute == 'foodmax':
            return f"{(section*part)} <> {(section*(part+1))}"

    def _set_titles(self):
        """
        function which creates the titles

        :return:
        """
        for i in range(2):
            self.subplots[i].set_title(f"{self.TEXTS[i][0]}{self.TITLE}")
            self.subplots[i].set_xlabel(self.TEXTS[i][1])
            self.subplots[i].set_ylabel(self.TEXTS[i][2])
            handles, labels = self.subplots[i].get_legend_handles_labels()
            self.subplots[i].legend(reversed(handles), reversed(labels), loc=2, fontsize=7)
        self.figure.subplots_adjust(hspace=.5)


class ProgressStatus(BaseFrame):
    """
    class to create the of the progress status
    """

    def __init__(self, father, status, details, percent, eta):
        """

        :param father: the father window
        :param status: status of the simulation
        :param details: what th program is doing
        :param percent: how much has already done
        :param eta: how many time it needs to finish
        """
        self.WIDGETS = {'status_label': (tk.Label, {'textvariable': status}, {'side': tk.TOP}),
                        'details_label': (tk.Label, {'textvariable': details}, {'side': tk.TOP}),
                        'percent_label': (tk.Label, {'textvariable': percent}, {'side': tk.TOP}),

                        'prograss_bar': (ttk.Progressbar, {}, {'side': tk.TOP}),
                        'eta_label': (tk.Label, {'textvariable': eta}, {'side': tk.TOP}),
                        'cancel_button': (tk.Button, {'text': 'Cancel', 'command': father.destroy}, {'side': tk.TOP}),
                        }
        super(ProgressStatus, self).__init__(father)
