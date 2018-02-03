"""
this module contains the instructions to create the graphics of a chunk or a creature
"""

import pygame as pyg
from . import var
from . import utility as utl
import math


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
        pyg.draw.rect(surface, self._get_color(tick), self._get_rect(chunk_dim, zoom))

    def _get_color(self, tick):
        return pyg.Color(0, int(self.food_history[int(tick) - 1] * 255 / 100), 0, 255)

    def _get_rect(self, chunk_dim, zoom):
        fact = chunk_dim * zoom/10
        return pyg.Rect(self.coord[0] * fact, self.coord[1] * fact, fact, fact)


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
        for key in self.COLORS:
            if key == 'none':
                self.colors[key] = self.COLORS[key]
            elif key == 'sex':
                self.colors[key] = self.COLORS[key][self.sex]
            else:
                self.colors[key] = self.COLORS[key][self.genes[key]]

        for key in self.DIMS:
            if key == 'none':
                self.dims[key] = self.DIMS[key]
            elif key != 'energy':
                self.dims[key] = self.genes[key] * self.DIMS[key]

    def draw(self, surface, tick, color, dim_flag, zoom):
        """
        Draws the creature

        :param surface: pygame surface
        :param tick: tick considered
        :type tick: int
        :param color: tuple with the RGB color
        :type color: tuple
        :param dim_flag: dimension of the circle
        :type dim_flag: int
        :param zoom: zoom factor
        :type zoom: float

        :return:
        """
        fact = zoom / 10
        birth = max(self.birth_tick + 1, 1)
        coord = [0, 0]
        for i in range(2):
            try:
                coord[i] = int(self.tick_history[tick - birth][i] * fact)
            except TypeError:
                print(f"{self.ID} - {tick} - {self.tick_history[tick - birth][i]}")
                return

        if dim_flag == 'energy':
            dim = int(self.tick_history[tick - birth][2] / 10 * fact)*self.DIMS['energy']
        else:
            dim = int(self.dims[dim_flag] * fact)

        self._draw_shape(surface, self.colors[color], coord, dim)
        try:
            self._draw_shape(surface, self.BORDER['color'], coord, dim, self.BORDER['width'])
        except ValueError:
            pass

    def _draw_shape(self, surface, color, coord, dim, border=0):
        """
        it draws the creature

        :param surface: pygame surface
        :param color: color of the creature
        :param coord: where to draw the creature
        :param dim: the dimension
        :param border: the border of the shape

        :return:
        """
        if self.diet == 'H':
            pyg.draw.circle(surface, color, coord, int(math.sqrt(dim)), border)
        elif self.diet == 'C':
            pyg.draw.rect(surface, color, (coord[0] - int(math.sqrt(dim)), coord[1] - int(math.sqrt(dim)), 2 * int(math.sqrt(dim)), 2 * int(math.sqrt(dim))), border)
        else:
            raise NotImplementedError
