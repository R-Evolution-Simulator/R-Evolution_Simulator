"""
this modulo is used to created the canvas where pygame will represent the
world, especially the background (of foodmax and temperature)
"""

import os

import pygame as pyg

from . import utility as utl
from . import var


class PygameCanvas(object):
    START_RESOLUTION = (100, 100)

    def __init__(self):
        """
        initialiser of the pygame canvas
        :param father: the simulation window
        """
        self.focus = None
        self.backgrounds = dict()
        self.resized_backgrounds = dict()
        self.resolution = self.START_RESOLUTION
        pyg.display.init()
        self.last_zoom = None
        self.fullscreen_zoom = None
        self.fullscreen = False
        self.full_mode = False
        self.surface = self.set_display()

    def set_focus(self, focus):
        try:
            self.focus.has_focus = False
            self.focus.set_underline()
        except AttributeError:
            pass
        if self.fullscreen:
            self.fullscreen_toggle()
        self.focus = focus
        self.focus.has_focus = True
        self.focus.set_underline()
        info = pyg.display.Info()
        self.fullscreen_zoom = min(info.current_w * 10 / self.focus.sim_width, info.current_h * 10 / self.focus.sim_height)
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
            path = os.path.join(self.focus.directories['images'], f"{attr}_background.gif")
            self.backgrounds[attr] = utl.img_load(path)

    def resize(self):
        """
        it changes the size of the window
        :return:
        """
        for i in self.backgrounds:
            self.resized_backgrounds[i] = utl.img_resize(self.backgrounds[i], self.focus.zoom)
        self.resolution = (int(self.focus.sim_width * self.focus.zoom / 10), int(self.focus.sim_height * self.focus.zoom / 10))
        self.surface = self.set_display()

    def update(self, tick, shows):
        """
        function which updates the screen
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """
        self.get_key_event()
        self.chunk_display(tick, shows['ch'])
        self.creatures_display(tick, shows)
        pyg.display.update()

    def get_key_event(self):
        events = pyg.event.get()
        for event in events:
            if event.type == pyg.KEYDOWN:
                char = event.unicode
                self.focus.get_key_event(char)

    def fullscreen_toggle(self):
        if self.fullscreen:
            self.focus.zoom = self.last_zoom
        else:
            self.last_zoom = self.focus.zoom
            self.focus.zoom = self.fullscreen_zoom
        self.fullscreen = not self.fullscreen
        self.resize()
        self.set_display()

    def full_mode_toggle(self):
        self.full_mode = not self.full_mode

    def set_display(self):
        if self.fullscreen and self.full_mode:
            try:
                return pyg.display.set_mode(self.resolution, pyg.FULLSCREEN)
            except pyg.error:
                pass
        return pyg.display.set_mode(self.resolution)

    def chunk_display(self, tick, to_show):
        """
        function which rapresents the chunks
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """
        if to_show == 'food':
            for chunk in self.focus.chunk_list:
                chunk.draw(self.surface, tick, self.focus.chunk_dim, self.focus.zoom)
        else:
            self.surface.blit(self.resized_backgrounds[to_show], (0, 0))

    def tick_creature_list(self, tick):
        """
        it creates a list with all the creature alive in a certain tick
        :return: the list of all the creature alive in a certain tick
        """
        L = []
        for i in self.focus.creature_list:
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
            creature.draw(self.surface, tick, color, dim, self.focus.zoom)

    def take_screenshot(self, path):
        pyg.image.save(self.surface, path)
