# import vari
from tkinter import *

import matplotlib

matplotlib.use("Tkagg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from time import time
from PIL import ImageDraw, Image as Img
from math import ceil

MAX_SPEED = 100


class MainWindow(Tk):
    """class of the main window"""
    def __init__(self, sim_name=""):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title("Simulation Load")  # titolo prima finestra: "Simulation Load"
        self.sim_name_entry = Entry(self)
        self.sim_name_entry.pack()
        self.sim_name_button = Button(self, text="Load", command=self.simulation_file_load)  # Button che carica la simulazione
        self.sim_name_button.pack(side=RIGHT)
        self.sim_name_info = Label(self, text="Insert simulation name")  # Label dove inserire il nome della simulazione da rappresentare
        self.sim_name_info.pack(side=LEFT)
        if sim_name != "":
            self.simulation_file_load(sim_name)
        self.mainloop()

    def simulation_file_load(self, sim_name=""):
        """method which upload the data of the simulation"""
        if sim_name == "":
            self.sim_name = self.sim_name_entry.get()
        else:
            self.sim_name = sim_name
            # aperti i file della simulazione
        self.file = {}
        try:
            for i in ['simulationData', 'chunkData', 'creaturesData', 'agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'population', 'speed']:
                self.file[i] = open(f"{self.sim_name}/{i}.csv")

            for i in ['foodmax', 'temperature_c', 'temperature_l', 'temperature_N']:
                self.file[i] = open(f"{self.sim_name}/spread_{i}.csv")
        except FileNotFoundError:
            self.sim_name_info.config(text="Simulation not found", fg="firebrick")
        else:
            # cambio finestra
            self.sim_name_entry.destroy()
            self.sim_name_button.destroy()
            self.sim_name_info.config(text="Simulation loading...", fg="black")
            self.sim_name_info.pack(anchor=CENTER)
            self.update()
            self.simulation_start()

    def simulation_start(self):
        """method which creates the graphic interface"""
        # setup finestra
        sim_data = self.file['simulationData'].readline().split(';')
        self.title(sim_data[0])
        self.sim_width = int(sim_data[1])
        self.sim_height = int(sim_data[2])
        self.max_tick = int(sim_data[3])
        self.chunk_dim = int(sim_data[5])
        
        # setup chunk
        self.chunk_list = []
        self.sim_name_info.config(text="Chunks loading...", fg="black")
        self.update()

        for line in self.file['chunkData']:
            self.chunk_list.append(ChunkD(line))

        # setup creatures
        self.sim_name_info.config(text="Creatures loading...", fg="black")
        self.update()
        self.creature_list = set()
        for line in self.file['creaturesData']:
            self.creature_list.add(CreaturesD(line))

        # cambio finestra
        self.sim_name_info.config(text="Simulation starting...", fg="black")
        self.update()
        self.sim_name_info.destroy()

        # visualizzazione iniziale
        self.ch_show = StringVar()
        self.ch_show.set("FM")
        self.creatures_color_show = StringVar()
        self.creatures_color_show.set("TR")
        self.creatures_dim_show = StringVar()
        self.creatures_dim_show.set("E")
        self.graph_tick = 100
        self.tick = 1.0
        self.zoom = 10
        self.speed = 1
        self.diagram_windows = []
        self.isPlaying = False
        self.last_frame_time = time()

        # finestra ambiente
        self.world_map = Canvas(self, width=self.sim_width * self.zoom / 10, height=self.sim_height * self.zoom / 10)
        self.world_map.grid()

        # Button per controllo simulazione
        self.play_control_frame = Frame(self)
        self.play_control_frame.grid(row=1, column=0)

        self.play_button = Button(self.play_control_frame, text="Play", command=self.start_play)
        self.play_button.pack(side=LEFT)
        self.fps_label = Label(self.play_control_frame, text="fps: 00.0")
        self.fps_label.pack(side=LEFT)

        self.set_tick_entry = Spinbox(self.play_control_frame, from_=1, to=self.max_tick, width=15)
        self.set_tick_entry.pack(side=LEFT)
        self.set_tick_button = Button(self.play_control_frame, text="Set tick", command=self.set_tick)
        self.set_tick_button.pack(side=LEFT)
        self.tick_label = Label(self.play_control_frame, text="Tick: 1")
        self.tick_label.pack(side=LEFT)
        self.speed_label = Label(self.play_control_frame, text=f"Tick/s: {self.speed}")
        self.speed_label.pack(side=LEFT)
        self.speed_slider = Scale(self.play_control_frame, orient=HORIZONTAL, showvalue=False, command=self.speed_change)
        self.speed_slider.pack(side=LEFT)
        self.dec_zoom_button = Button(self.play_control_frame, text="- 10%", command=self.dec_zoom)
        self.dec_zoom_button.pack(side=LEFT)
        self.zoom_label = Label(self.play_control_frame, text=f"zoom: {self.zoom}0%")
        self.zoom_label.pack(side=LEFT)
        self.inc_zoom_button = Button(self.play_control_frame, text="+ 10%", command=self.inc_zoom)
        self.inc_zoom_button.pack(side=LEFT)

        # Button per visualizzazione Chunk
        self.ch_cr_set_frame = Frame(self)
        self.ch_cr_set_frame.grid(row=0, column=1)

        self.ch_set_labelframe = LabelFrame(self.ch_cr_set_frame, text="Chunk")
        self.ch_set_labelframe.pack(anchor=W, fill=X)
        self.ch_FM_button = Radiobutton(self.ch_set_labelframe, text="Food Max", variable=self.ch_show, value="FM", command=self.world_map_update)
        self.ch_FM_button.pack(anchor=W)
        self.ch_T_button = Radiobutton(self.ch_set_labelframe, text="Temperature", variable=self.ch_show, value="T", command=self.world_map_update)
        self.ch_T_button.pack(anchor=W)
        self.ch_F_button = Radiobutton(self.ch_set_labelframe, text="Food", variable=self.ch_show, value="F", command=self.world_map_update)
        self.ch_F_button.pack(anchor=W)

        self.cr_set_labelframe = LabelFrame(self.ch_cr_set_frame, text="Creatures")
        self.cr_set_labelframe.pack(anchor=W)
        self.cr_color_labelframe = LabelFrame(self.cr_set_labelframe, text="Color")
        self.cr_color_labelframe.pack(side=LEFT, anchor=NW, fill=Y)
        self.cr_N_button = Radiobutton(self.cr_color_labelframe, text="None", variable=self.creatures_color_show, value="N", command=self.world_map_update)
        self.cr_N_button.pack(anchor=W)
        self.cr_S_button = Radiobutton(self.cr_color_labelframe, text="Sex", variable=self.creatures_color_show, value="S", command=self.world_map_update)
        self.cr_S_button.pack(anchor=W)
        self.cr_TR_button = Radiobutton(self.cr_color_labelframe, text="Temp Resist", variable=self.creatures_color_show, value="TR", command=self.world_map_update)
        self.cr_TR_button.pack(anchor=W)

        self.cr_dim_labelframe = LabelFrame(self.cr_set_labelframe, text="Dimension")
        self.cr_dim_labelframe.pack(side=LEFT, anchor=NW, fill=Y)
        self.cr_N_button = Radiobutton(self.cr_dim_labelframe, text="None", variable=self.creatures_dim_show, value="N", command=self.world_map_update)
        self.cr_N_button.pack(anchor=W)
        self.cr_E_button = Radiobutton(self.cr_dim_labelframe, text="Energy", variable=self.creatures_dim_show, value="E", command=self.world_map_update)
        self.cr_E_button.pack(anchor=W)
        self.cr_A_button = Radiobutton(self.cr_dim_labelframe, text="Agility", variable=self.creatures_dim_show, value="A", command=self.world_map_update)
        self.cr_A_button.pack(anchor=W)
        self.cr_B_button = Radiobutton(self.cr_dim_labelframe, text="Bigness", variable=self.creatures_dim_show, value="B", command=self.world_map_update)
        self.cr_B_button.pack(anchor=W)
        self.cr_EC_button = Radiobutton(self.cr_dim_labelframe, text="Eat Coeff", variable=self.creatures_dim_show, value="EC", command=self.world_map_update)
        self.cr_EC_button.pack(anchor=W)
        self.cr_S_button = Radiobutton(self.cr_dim_labelframe, text="Speed", variable=self.creatures_dim_show, value="S", command=self.world_map_update)
        self.cr_S_button.pack(anchor=W)
        self.cr_NCG_button = Radiobutton(self.cr_dim_labelframe, text="Num Control Gene", variable=self.creatures_dim_show, value="NCG", command=self.world_map_update)
        self.cr_NCG_button.pack(anchor=W)

        choices = ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed', 'population', 'foodmax', 'temperature_c', 'temperature_l', 'temperature_N']
        self.diagram_chioce = StringVar()
        self.diagram_chioce.set('agility')
        self.diagram_chioce_optionmenu = OptionMenu(self.ch_cr_set_frame, self.diagram_chioce, *choices)
        self.diagram_chioce_optionmenu.pack(anchor=W, fill=X)
        self.new_diagram_button = Button(self.ch_cr_set_frame, text="New diagram", command=self.graphics_window_create)
        self.new_diagram_button.pack(anchor=W)

        self.background_creation()
        self.set_zoom()

    def background_creation(self):
        """method which creates the background of the world"""
        imageFood = Img.new("RGB", (int(self.sim_width / 10), int(self.sim_height / 10)))
        drawFood = ImageDraw.Draw(imageFood)
        imageTemp = Img.new("RGB", (int(self.sim_width / 10), int(self.sim_height / 10)))
        drawTemp = ImageDraw.Draw(imageTemp)

        for chunk in self.chunk_list:
            drawFood.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                               fill=(0, int(chunk.foodMax * 255 / 100), 0))
            if chunk.temperature > 0:
                drawTemp.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                                   fill=(255, int(255 - (chunk.temperature / 100 * 255)), int(255 - (chunk.temperature / 100 * 255))))
            else:
                drawTemp.rectangle((chunk.coord[0] * self.chunk_dim / 10, chunk.coord[1] * self.chunk_dim / 10, (chunk.coord[0] + 1) * self.chunk_dim / 10, (chunk.coord[1] + 1) * self.chunk_dim / 10),
                                   fill=(int(255 + (chunk.temperature / 100 * 255)), int(255 + (chunk.temperature / 100 * 255)), 255))

        imageFood.save(f"{self.sim_name}/backgroundFM.gif", "GIF")
        imageTemp.save(f"{self.sim_name}/backgroundT.gif", "GIF")

        self.FM_background = PhotoImage(file=f"{self.sim_name}/backgroundFM.gif")
        self.T_background = PhotoImage(file=f"{self.sim_name}/backgroundT.gif")
        del imageTemp, imageFood, drawFood, drawTemp

    def speed_change(self, speed_cursor):
        """
        method which allow to change the speed of the simulation reproduction
        """
        self.speed = int(MAX_SPEED ** (float(speed_cursor) / 100))
        self.speed_label.config(text=f"T/s: {self.speed:02d}")

    def dec_zoom(self):
        """method which decrease the zoom"""
        self.zoom = max(1, self.zoom - 1)
        self.set_zoom()

    def inc_zoom(self):
        """method which increase the zoom"""
        self.zoom += 1
        self.set_zoom()

    def set_zoom(self):
        """method which set to selected zoom"""
        self.dysplayed_FM_background = self.FM_background.zoom(self.zoom)
        self.dysplayed_T_background = self.T_background.zoom(self.zoom)
        self.zoom_label.configure(text=f"zoom: {self.zoom}0%")
        self.world_map.configure(width=self.sim_width * self.zoom / 10, height=self.sim_height * self.zoom / 10)
        self.world_map_update()

    def start_play(self):
        """method which starts or stops the reproduction of the simulation"""
        self.isPlaying = not (self.isPlaying)
        if self.isPlaying:
            self.play_button.config(text="Pause")
            self.play()
        else:
            self.play_button.config(text="Play")

    # update simulazione
    def play(self):
        """
        method which reproduces the simulation, updating the screen
        """
        while self.isPlaying:
            self.last_frame_time = time()
            self.world_map_update()
            time_diff = time() - self.last_frame_time
            self.tick += time_diff * self.speed
            self.tick = min(self.tick, self.max_tick)
            if int(self.tick) == self.max_tick:
                self.start_play()
            fps = round(1.0 / time_diff, 1)
            self.fps_label.config(text=f"fps: {fps:04.1f}")

    def set_tick(self):
        """
        function which imposts a particular tick
        """
        try:
            self.tick = int(self.set_tick_entry.get())
        except ValueError:
            pass
        self.world_map_update()

    def world_map_update(self):
        """function which updates the screen"""
        self.world_map.delete("all")
        self.chunk_display()  # rappresentazione chunk
        self.creatures_display()
        new_graph_tick = ceil(int(self.tick) / 100) * 100
        for window in self.diagram_windows:
            if window.show_tick:
                window.tick_line_set()
        if new_graph_tick != self.graph_tick:
            self.graph_tick = new_graph_tick
            for window in self.diagram_windows:
                if window.follow_play:
                    window.dyn_axes_set()
        self.tick_label.config(text=f"Tick: {int(self.tick):04d}")
        self.update()

    def chunk_display(self):
        """function which rapresents the chunks"""
        if self.ch_show.get() == "FM":  # con il cibo al massimo
            self.world_map.create_image(0, 0, image=self.dysplayed_FM_background, anchor=NW)
        elif self.ch_show.get() == "T":  # con la temperatura
            self.world_map.create_image(0, 0, image=self.dysplayed_T_background, anchor=NW)
        elif self.ch_show.get() == "F":  # con il cibo in un certo momento
            for chunk in self.chunk_list:
                self.world_map.create_rectangle(chunk.coord[0] * self.chunk_dim * self.zoom / 10, chunk.coord[1] * self.chunk_dim * self.zoom / 10, (chunk.coord[0] + 1) * self.chunk_dim * self.zoom / 10,
                                                (chunk.coord[1] + 1) * self.chunk_dim * self.zoom / 10,
                                                fill=('#%02x%02x%02x' % (0, int(chunk.foodHistory[int(self.tick) - 1] * 255 / 100), 0)))

    def creatures_display(self):
        """function which rapresents the creatures"""
        def tick_creature_list():
            L = []
            for i in self.creature_list:
                if i.birthTick <= int(self.tick) and i.deathTick >= int(self.tick):
                    L.append(i)
            return L

        cr_col = self.creatures_color_show.get()
        cr_dim = self.creatures_dim_show.get()

        for i in tick_creature_list():
            birth = max(i.birthTick, 1)
            coord = (i.tickHistory[int(self.tick) - birth][0], i.tickHistory[int(self.tick) - birth][1])

            # display secondo il sesso
            if cr_col == "N":
                color = (255, 255, 255)
            elif cr_col == "S":
                if i.sex == 0:
                    color = (255, 255, 0)
                else:
                    color = (0, 255, 255)

            # display secondo la capacità di resistere alla temperatura
            elif cr_col == "TR":
                if i.tempResist == "c":
                    color = (255, 0, 0)
                elif i.tempResist == "l":
                    color = (0, 0, 255)
                elif i.tempResist == "N":
                    color = (128, 128, 128)
                elif i.tempResist == "n":
                    color = (255, 255, 255)

            if cr_dim == "N":
                dim = 7
            elif cr_dim == "E":
                dim = i.tickHistory[int(self.tick) - birth][2] / 10
            elif cr_dim == "A":
                dim = i.agility / 5
            elif cr_dim == "B":
                dim = i.bigness / 7
            elif cr_dim == "EC":
                dim = i.eatCoeff * 42
            elif cr_dim == "NCG":
                dim = i.numControlGene / 9
            elif cr_dim == "S":
                dim = i.speed * 5

            self.world_map.create_oval((coord[0] - dim / 2) * self.zoom / 10, (coord[1] - dim / 2) * self.zoom / 10, (coord[0] + dim / 2) * self.zoom / 10, (coord[1] + dim / 2) * self.zoom / 10, fill=('#%02x%02x%02x' % color))

    def graphics_window_create(self):
        """function which creates a graphic window"""
        new_graph_subj = self.diagram_chioce.get()
        if new_graph_subj in ['agility', 'bigness', 'eatCoeff', 'fertility', 'numControlGene', 'speed']:
            new_window = GeneGraphicsWindow(self.file, new_graph_subj, self)
        elif new_graph_subj in ['foodmax', 'temperature_c', 'temperature_l', 'temperature_N']:
            new_window = SpreadGraphicsWindow(self.file, new_graph_subj, self)
        elif new_graph_subj == 'population':
            new_window = PopulationGraphicsWindow(self.file, new_graph_subj, self)
        self.diagram_windows.append(new_window)
        new_window.mainloop()

    def on_closing(self):
        """function which closes the graphic window"""
        for window in self.diagram_windows:
            window.destroy()
        self.destroy()


class GraphicsWindow(Tk):
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
        self.figure.subplots_adjust(hspace=.5)


class ChunkD:
    def __init__(self, chunkDataLine):
        chunkData = chunkDataLine.split(';')
        self.coord = [int(chunkData[0]), int(chunkData[1])]
        self.foodMax = float(chunkData[2])
        self.growthRate = float(chunkData[3])
        self.temperature = float(chunkData[4])
        self.foodHistory = chunkData[5].split(',')
        for i in range(len(self.foodHistory)):
            self.foodHistory[i] = int(self.foodHistory[i])


class CreaturesD:
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
