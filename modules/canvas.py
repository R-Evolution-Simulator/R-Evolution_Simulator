"""
this modulo is used to created the canvas where pygame will represent the
world, especially the background (of foodmax and temperature)
"""

import pygame as pyg
from . import utility as utl
from . import var
import os


class PygameCanvas(object):
    START_RESOLUTION = (100, 100)

    def __init__(self, father):
        """
        initialiser of the pygame canvas
        :param father: the simulation window
        """
        self.father = father
        self.backgrounds = dict()
        self.resized_backgrounds = dict()
        self.surface = pyg.display.set_mode(self.START_RESOLUTION)
        self._background_creation()

    def destroy(self):
        """
        it closes the simulation
        :return:
        """
        pyg.quit()

    def _background_creation(self):
        """
        it creates the background of the world
        :return:
        """
        for attr in var.CHUNK_ATTRS:
            path = os.path.join(self.father.directories['images'], f"{attr}_background.gif")
            self.backgrounds[attr] = utl.img_load(path)

    def resize(self):
        """
        it changes the size of the window
        :return:
        """
        for i in self.backgrounds:
            self.resized_backgrounds[i] = utl.img_resize(self.backgrounds[i], self.father.zoom)
        self.surface = pyg.display.set_mode(
            (int(self.father.sim_width * self.father.zoom / 10), int(self.father.sim_height * self.father.zoom / 10)))

    def update(self, tick, shows):
        """
        function which updates the screen
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """
        self.chunk_display(tick, shows['ch'])
        self.creatures_display(tick, shows)
        pyg.display.update()

    def chunk_display(self, tick, to_show):
        """
        function which rapresents the chunks
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """
        if to_show == 'food':
            for chunk in self.father.chunk_list:
                chunk.draw(self.surface, tick, self.father.chunk_dim, self.father.zoom)
        else:
            self.surface.blit(self.resized_backgrounds[to_show], (0, 0))

    def tick_creature_list(self, tick):
        """
        it creates a list with all the creature alive in a certain tick
        :return: the list of all the creature alive in a certain tick
        """
        L = []
        for i in self.father.creature_list:
            if i.birth_tick <= tick <= i.death_tick:
                L.append(i)
        return L

    def creatures_display(self, tick, shows):
        """
        function which rapresents the creature
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """

        color = shows['cc']
        dim = shows['cd']

        for creature in self.tick_creature_list(tick):
            creature.draw(self.surface, tick, color, dim, self.father.zoom)
