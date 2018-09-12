"""
this modulo contains the class Chunk which controls all the functions and variable of
every portion of the world (quantity of food, temperature, growth of the food, etc.)
"""

from random import random

from . import utility as utl
from . import var


class Chunk:
    """
    chunk class
    """

    def __init__(self, world, x, y, foodmax, temperature):
        """
        Creates a new chunk object given the coords

        :param world: world object where the chunk is
        :type world: World
        :param coord: tuple with the coordinates of the chunk
        :type coord: tuple
        """
        self.coord = (x, y)
        # food
        self.world = world
        self.foodmax = foodmax
        self.temperature = temperature
        self.food = self.foodmax * random() * self.world.chunks_vars['start_food']
        self.growth_rate = self.foodmax * self.world.chunks_vars['growth_coeff']
        self.food_history = list()
        self.chunk_creature_set = set()
        self.ticks_record = list()

    def update(self, tick_to_record):
        """
        Updates the parameters of the chunk

        :return:
        """
        self.food *= (1 + self.growth_rate)  # ad ogni ciclo l'erba cresce
        if self.food > self.foodmax:  # finche' non raggiunge il massimo
            self.food = self.foodmax

        self.food_history.append((int(self.food),))

        if tick_to_record:
            self.tick_record()

    def tick_record(self):
        self.ticks_record.append(self.chunk_creature_set.copy())

    def end(self, file):
        """
        Saves the data of the chunk at the end of the simulation

        :param file: the file to write to
        :return:
        """
        to_write = str()
        for i in var.TO_RECORD['chunk']:
            to_write += utl.add_to_write(self.__dict__[i], self.world.analysis['rounding'])
        file.write(to_write[:-1] + '\n')
