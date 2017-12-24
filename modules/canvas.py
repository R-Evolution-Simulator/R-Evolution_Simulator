from math import ceil
import pygame as pyg
from PIL import ImageDraw, Image as Img
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
        self.surface = None
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
        image_food = Img.new("RGB", (int(self.father.sim_width / 10), int(self.father.sim_height / 10)))
        draw_food = ImageDraw.Draw(image_food)
        image_temp = Img.new("RGB", (int(self.father.sim_width / 10), int(self.father.sim_height / 10)))
        draw_temp = ImageDraw.Draw(image_temp)

        for chunk in self.father.chunk_list:
            draw_food.rectangle((chunk.coord[0] * self.father.chunk_dim / 10,
                                 chunk.coord[1] * self.father.chunk_dim / 10,
                                 (chunk.coord[0] + 1) * self.father.chunk_dim / 10,
                                 (chunk.coord[1] + 1) * self.father.chunk_dim / 10),
                                fill=(0, int(chunk.foodMax * 255 / 100), 0))
            if chunk.temperature > 0:
                draw_temp.rectangle((chunk.coord[0] * self.father.chunk_dim / 10,
                                     chunk.coord[1] * self.father.chunk_dim / 10,
                                     (chunk.coord[0] + 1) * self.father.chunk_dim / 10,
                                     (chunk.coord[1] + 1) * self.father.chunk_dim / 10),
                                    fill=(255, int(255 - (chunk.temperature / 100 * 255)),
                                          int(255 - (chunk.temperature / 100 * 255))))
            else:
                draw_temp.rectangle((chunk.coord[0] * self.father.chunk_dim / 10,
                                     chunk.coord[1] * self.father.chunk_dim / 10,
                                     (chunk.coord[0] + 1) * self.father.chunk_dim / 10,
                                     (chunk.coord[1] + 1) * self.father.chunk_dim / 10),
                                    fill=(int(255 + (chunk.temperature / 100 * 255)),
                                          int(255 + (chunk.temperature / 100 * 255)), 255))

        backgrounds_paths = {'FM': os.path.join(var.SIMULATIONS_PATH, self.father.sim_name, "backgroundFM.gif"),
                             'T': os.path.join(var.SIMULATIONS_PATH, self.father.sim_name, "backgroundT.gif")}

        image_food.save(backgrounds_paths['FM'], "GIF")
        image_temp.save(backgrounds_paths['T'], "GIF")
        for i in backgrounds_paths:
            self.backgrounds[i] = utl.img_load(backgrounds_paths[i])
        del image_temp, image_food, draw_food, draw_temp

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
        self.chunk_display(tick, shows)
        self.creatures_display(tick, shows)
        pyg.display.update()

    def chunk_display(self, tick, shows):
        """
        function which rapresents the chunks
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """
        to_show = shows['ch']
        if to_show == "F":  # con il cibo in un certo momento
            for chunk in self.father.chunk_list:
                chunk.draw(self.surface, tick, self.father.chunk_dim, self.father.zoom)
        else:
            self.surface.blit(self.resized_backgrounds[to_show], (0, 0))

    def creatures_display(self, tick, shows):
        """
        function which rapresents the creature
        :param tick: tick represented
        :param shows: which characteristic is showed
        :return:
        """

        def tick_creature_list():
            """
            it creates a list with all the creature alive in a certain tick
            :return: the list of all the creature alive in a certain tick
            """
            L = []
            for i in self.father.creature_list:
                if i.birthTick <= tick <= i.deathTick:
                    L.append(i)
            return L

        color = shows['cc']
        dim = shows['cd']

        for creature in tick_creature_list():
            creature.draw(self.surface, tick, color, dim, self.father.zoom)
