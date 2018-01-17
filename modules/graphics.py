import pygame as pyg
from . import var
from . import utility as utl


class ChunkD:
    """
    class to represent a Chunk object on the screen
    """

    def __init__(self, chunk_data):
        """
        creates a new object

        :param chunk_data: string with all the data of the chunk to be represented
        :type chunk_data: str
        """
        restored = utl.get_from_string(chunk_data, 0, var.TO_RECORD['chunk'])
        self.__dict__.update(restored)

    def draw(self, surface, tick, chunk_dim, zoom):
        """
        it draws the chunk

        :param surface: pygame surface
        :param tick: tick considered
        :type tick: int
        :param chunk_dim: dimension of the chunk
        :type chunk_dim: int
        :param zoom: zoom factor
        :type zoom: float

        :return:
        """
        pyg.draw.rect(surface, pyg.Color(0, int(self.food_history[int(tick) - 1] * 255 / 100), 0, 255),
                      pyg.Rect(self.coord[0] * chunk_dim * zoom / 10, self.coord[1] * chunk_dim * zoom / 10,
                               chunk_dim * zoom / 10, chunk_dim * zoom / 10))


class CreaturesD:
    """
    class to represent a Creature object on the screen
    """
    COLORS = var.DEFAULT_CREATURES_COLORS
    DIMS = var.DEFAULT_CREATURES_DIMS
    BORDER = var.DEFAULT_CREATURES_BORDER

    def __init__(self, creature_data):
        """
        creates a new object

        :param creature_data: string with all the data of the chunk to be represented
        :type creature_data: str
        """
        restored = utl.get_from_string(creature_data, 0, var.TO_RECORD['creature'])
        self.__dict__.update(restored)
        self.colors = dict()
        self.dims = dict()
        self.color_dims_creation()

    def color_dims_creation(self):
        """
        saved the dimension of the circle in relation with the characteristic represented

        :return:
        """
        self.colors['N'] = self.COLORS['N']
        self.colors['S'] = self.COLORS['S'][self.sex]
        self.colors['TR'] = self.COLORS['TR'][self.genes['temp_resist']]

        self.dims['N'] = self.DIMS['N']
        for i in self.DIMS:
            if i is not 'N':
                self.dims[i] = self.genes[self.DIMS[i][1]] * self.DIMS[i][0]

    def draw(self, surface, tick, color, dim, zoom):
        """
        Draws the creature

        :param surface: pygame surface
        :param tick: tick considered
        :type tick: int
        :param color: tuple with the RGB color
        :type color: tuple
        :param dim: dimension of the circle
        :type dim: int
        :param zoom: zoom factor
        :type zoom: float

        :return:
        """
        birth = max(self.birth_tick + 1, 1)
        coord = (
            int((self.tick_history[tick - birth][0]) * zoom / 10), int(self.tick_history[tick - birth][1] * zoom / 10))
        if dim == 'E':
            self.draw_shape(surface, self.colors[color], coord,
                            int(self.tick_history[tick - birth][2] / 10 * zoom / 10))
            try:
                self.draw_shape(surface, self.BORDER['color'], coord,
                                int(self.tick_history[tick - birth][2] / 10 * zoom / 10), self.BORDER['width'])
            except ValueError:
                pass
        else:
            self.draw_shape(surface, self.colors[color], coord, int(self.dims[dim] * zoom / 10))
            try:
                self.draw_shape(surface, self.BORDER['color'], coord,
                                int(self.tick_history[tick - birth][2] / 10 * zoom / 10), self.BORDER['width'])
            except ValueError:
                pass

    def draw_shape(self, surface, color, coord, dim, border=0):
        if self.diet == 'H':
            pyg.draw.circle(surface, color, coord, dim, border)
        elif self.diet == 'C':
            pyg.draw.rect(surface, color, (coord[0] - dim, coord[1] - dim, 2 * dim, 2 * dim), border)
        else:
            raise NotImplementedError
