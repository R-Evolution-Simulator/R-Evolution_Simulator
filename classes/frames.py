import tkinter as tk

class BaseFrame(tk.Frame):
    WIDGETS = None

    def __init__(self, father):
        super(BaseFrame, self).__init__(father)
        self._widgets_load()

    def _widgets_load(self):
        self.widgets = dict()
        for i in self.WIDGETS:
            new = self.WIDGETS[i][0](self, **self.WIDGETS[i][1])
            new.pack(**self.WIDGETS[i][2])
            self.widgets[i] = new


class Load(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'entry': (tk.Entry, {}, {}),
                        'button': (tk.Button, {'text': "Load", 'command': windows[0].simulation_file_load}, {'side': tk.RIGHT}),
                        'label': (tk.Label, {'text': "Insert simulation name"}, {'side': tk.LEFT})}
        super(Load, self).__init__(father)


class PlayControl(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'play': (tk.Button, {'text': "Play", 'command': windows[0].start_play}, {'side': tk.LEFT}),
                        'fps': (tk.Label, {'text': "fps: 00.0"}, {'side': tk.LEFT}),
                        'tick_entry': (tk.Spinbox, {'from_': 1, 'to': windows[1].max_tick, 'width': 15}, {'side': tk.LEFT}),
                        'tick_button': (tk.Button, {'text': "Set tick", 'command': windows[0].set_tick}, {'side': tk.LEFT}),
                        'tick_label': (tk.Label, {'text': "Tick: 1"}, {'side': tk.LEFT}),
                        'speed_label': (tk.Label, {'text': f"Tick/s: {windows[1].speed}"}, {'side': tk.LEFT}),
                        'speed_slider': (tk.Scale, {'orient': tk.HORIZONTAL, 'showvalue': False, 'command': windows[0].speed_change}, {'side': tk.LEFT}),
                        'dec_zoom': (tk.Button, {'text': "- 10%", 'command': windows[0].dec_zoom}, {'side': tk.LEFT}),
                        'zoom': (tk.Label, {'text': f"zoom: {windows[1].zoom}0%"}, {'side': tk.LEFT}),
                        'inc_zoom': (tk.Button, {'text': "+ 10%", 'command': windows[0].inc_zoom}, {'side': tk.LEFT}), }
        super(PlayControl, self).__init__(father)


class BaseLabelFrame(tk.LabelFrame, BaseFrame):
    def __init__(self, father):
        super(BaseLabelFrame, self).__init__(father, text=self.NAME)
        self._widgets_load()


class BaseSelectFrame(BaseLabelFrame):
    def __init__(self, father, windows):
        for i in self.WIDGETS:
            if self.WIDGETS[i][0] == tk.Radiobutton:
                self.WIDGETS[i][1]['variable'] = windows[1].shows[self.CODE]
                self.WIDGETS[i][1]['command'] = windows[1].update
                self.WIDGETS[i][1]['value'] = i
                self.WIDGETS[i][2] = {'anchor': tk.W}
        super(BaseSelectFrame, self).__init__(father)


class ChunksSet(BaseSelectFrame):
    NAME = "Chunk"
    CODE = 'ch'
    WIDGETS = {'FM': [tk.Radiobutton, {'text': "Food Max"}, {}],
               'T': [tk.Radiobutton, {'text': "Temperature"}, {}],
               'F': [tk.Radiobutton, {'text': "Food"}, {}], }


class CreatureColorSet(BaseSelectFrame):
    NAME = "Color"
    CODE = 'cc'
    WIDGETS = {'N': [tk.Radiobutton, {'text': "None"}, {}],
               'S': [tk.Radiobutton, {'text': "Sex"}, {}],
               'TR': [tk.Radiobutton, {'text': "Temp Resist"}, {}], }


class CreatureDimSet(BaseSelectFrame):
    NAME = "Dimension"
    CODE = 'cd'
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
        self.WIDGETS = {'cl': (CreatureColorSet, {'windows': windows}, {'side': tk.LEFT, 'anchor': tk.NW, 'fill': tk.Y}),
                        'dim': (CreatureDimSet, {'windows': windows}, {'side': tk.LEFT, 'anchor': tk.NW, 'fill': tk.Y}),
               }
        super(CreatureSet, self).__init__(father)


class DiagramSet(tk.Frame):
    CHOICES = ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed', 'population', 'foodmax', 'temperature_c', 'temperature_l', 'temperature_N']

    def __init__(self, father, windows):
        super(DiagramSet, self).__init__(father)
        self.father = father
        self.WIDGETS = {'new': (tk.Button, {'text': "New Diagram", 'command': windows[1].graphics_window_create}, {'anchor': tk.W})}
        self.diagram_chioce = tk.StringVar()
        self.diagram_chioce.set('agility')
        self._widgets_load()

    def _widgets_load(self):
        self.widgets = dict()
        self.widgets['menu'] = tk.OptionMenu(self, self.diagram_chioce, *self.CHOICES)
        self.widgets['menu'].pack(anchor=tk.W, fill=tk.X)
        for i in self.WIDGETS:
            new = self.WIDGETS[i][0](self, **self.WIDGETS[i][1])
            new.pack(**self.WIDGETS[i][2])
            self.widgets[i] = new


class SetSuperFrame(BaseFrame):
    def __init__(self, father, windows):
        self.WIDGETS = {'ch': (ChunksSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'cr': (CreatureSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X}),
                        'dgrm': (DiagramSet, {'windows': windows}, {'anchor': tk.W, 'fill': tk.X})
                        }
        super(SetSuperFrame, self).__init__(father)
