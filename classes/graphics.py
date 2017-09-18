import pygame as pyg


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
                      pyg.Rect(self.coord[0] * chunk_dim * zoom / 10, self.coord[1] * chunk_dim * zoom / 10,
                               chunk_dim * zoom / 10, chunk_dim * zoom / 10))


class CreaturesD:
    DEFAULT_COLORS = {'N': pyg.Color(255, 255, 255, 255),
                      'S': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                      'TR': {'c': pyg.Color(255, 0, 0, 255), 'l': pyg.Color(0, 0, 255, 255),
                             'N': pyg.Color(128, 128, 128, 255), 'n': pyg.Color(255, 255, 255, 255)}}
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
        coord = (
            int((self.tickHistory[tick - birth][0]) * zoom / 10), int(self.tickHistory[tick - birth][1] * zoom / 10))
        if dim == 'E':
            pyg.draw.circle(surface, self.colors[color], coord, int(self.tickHistory[tick - birth][2] / 10 * zoom / 10))
        else:
            pyg.draw.circle(surface, self.colors[color], coord, int(self.dims[dim] * zoom / 10))
