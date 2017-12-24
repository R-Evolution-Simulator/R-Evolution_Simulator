import pygame as pyg
from . import var
from . import utility as utl
from ast import literal_eval


class ChunkD:
    def __init__(self, chunk_data):
        restored = utl.get_from_string(chunk_data, 0, var.TO_RECORD['chunk'])
        self.__dict__.update(restored)

    def draw(self, surface, tick, chunk_dim, zoom):
        pyg.draw.rect(surface, pyg.Color(0, int(self.food_history[int(tick) - 1] * 255 / 100), 0, 255),
                      pyg.Rect(self.coord[0] * chunk_dim * zoom / 10, self.coord[1] * chunk_dim * zoom / 10,
                               chunk_dim * zoom / 10, chunk_dim * zoom / 10))


class CreaturesD:
    COLORS = var.DEFAULT_CREATURES_COLORS
    DIMS = var.DEFAULT_CREATURES_DIMS
    BORDER = var.DEFAULT_CREATURES_BORDER

    def __init__(self, creature_data):
        restored = utl.get_from_string(creature_data, 0, var.TO_RECORD['creature'])
        self.__dict__.update(restored)

        self.colors = dict()
        self.dims = dict()
        self.color_dims_creation()

    def color_dims_creation(self):
        self.colors['N'] = self.COLORS['N']
        self.colors['S'] = self.COLORS['S'][self.sex]
        self.colors['TR'] = self.COLORS['TR'][self.genes['temp_resist']]

        self.dims['N'] = self.DIMS['N']
        for i in self.DIMS:
            if i is not 'N':
                self.dims[i] = self.genes[self.DIMS[i][1]] * self.DIMS[i][0]

    def draw(self, surface, tick, color, dim, zoom):
        birth = max(self.birth_tick, 1)
        coord = (
            int((self.tick_history[tick - birth][0]) * zoom / 10), int(self.tick_history[tick - birth][1] * zoom / 10))
        if dim == 'E':
            pyg.draw.circle(surface, self.colors[color], coord,
                            int(self.tick_history[tick - birth][2] / 10 * zoom / 10))
            try:
                pyg.draw.circle(surface, self.BORDER['color'], coord,
                                int(self.tick_history[tick - birth][2] / 10 * zoom / 10), self.BORDER['width'])
            except ValueError:
                pass
        else:
            pyg.draw.circle(surface, self.colors[color], coord, int(self.dims[dim] * zoom / 10))
            try:
                pyg.draw.circle(surface, self.BORDER['color'], coord,
                                int(self.tick_history[tick - birth][2] / 10 * zoom / 10), self.BORDER['width'])
            except ValueError:
                pass
