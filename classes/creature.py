import math
import random
from random import random as rnd
from . import utility as utl
from . import var
from . import genes as gns


class Creature:
    """class of creatures"""
    TO_RECORD = var.TO_RECORD['creature']

    def __init__(self, world, start_coord, parents_ID, energy, sex, genes, start_count=0):
        """
        Creates a new creature

        :param world: world object where the creature lives
        :type world: World
        :param start_coord: initial coordinates where the creature is
        :type start_coord: tuple
        :param parents_ID: number of the two creature parents' ID
        :type parents_ID: tuple
        :param energy: level of initial energy
        :type energy: float
        :param sex: 0 or 1 indicates the sex of the creature
        :type sex: int
        :param genes: dictionary with all the characteristics
        :type genes: dict
        :param start_count: age of the initial creatures (it is equal to 0 for creatures born after tick 1)
        :type start_count: int
        """
        self.world = world
        self.ID = self.world.get_ID()
        self.coord = start_coord  # creature's starting coord definition
        self.parents_ID = parents_ID
        self.tick_history = list()
        self.birth_tick = self.world.tick_count - start_count  # creature's creation tick definition (startCount is used only during diversification at start)
        self.energy = energy  # creature's starting energy definition
        self._actual_chunk().chunk_creature_list.append(self)  # creature's adding to the list of creatures in its chunk
        self.reprod_ready = False  # reproduction capacity set to false
        self.death_date = int(random.gauss(self.world.creatures_vars['average_age'], self.world.creatures_vars[
            'dev_age_prob']))  # crearture's age of death definition
        self.age = 0  # age set to 0
        self.dest_chunk = [self._chunk_coord(0), self._chunk_coord(1)]
        self.sex = sex
        self.death_tick = None
        self.death_cause = None

        # creature's genes definition
        self.genes = genes
        self.reprod_countdown = self.genes['fertility'].get()

        # phenotypical characteristics valuation

        self.world.new_born.add(self)  # creature's adding to the list of creatures

    def death(self, cause="e"):
        """
        Kills the creature

        :param cause: way in which the creature die
        :type cause: str
        
        :return:
        """
        self.death_tick = self.world.tick_count
        self.death_cause = cause
        self.world.tick_dead.add(self)

    def update(self):
        """
        Updates the creature providing the given tick

        :return:
        """
        
        # reproduction control
        if self.energy > 50 and self.reprod_countdown <= 0:
            self.reprod_ready = True
            self._dating_agency()

        else:
            self.reprod_ready = False
            self.reprod_countdown -= 1

        # food search
        self._dest_calc()
        if not [self._chunk_coord(0),
                self._chunk_coord(1)] == self.dest_chunk:
            self._step()

        else:
            self._eat()

        # creature's variables update
        self.energy -= self.world.creatures_vars['en_dec_coeff'] * self.energy  # energy decrease every tick
        self.age += 1

        # death control
        self.tick_history.append(
            (round(self.coord[0], 2), round(self.coord[1], 2), int(self.energy), int(self.reprod_ready)))
        self._death_control()

    def _actual_chunk(self):
        """
        Gets the Chunk object in which the creature is

        :return: the Chunk object in which the creature is
        """
        return self.world.chunk_list[self._chunk_coord(0)][self._chunk_coord(1)]

    def _death_control(self):
        """
        Controls if the creatures has to die for some reasons.
        Controls the parameters of starvation, temperature and age
        
        :return:
        """
        if self.energy < 10:  # starvation death
            self.world.tick_dead.add(self)
            self.death("s")

        elif rnd() <= self._death_prob_temp():  # temperature death
            self.world.tick_dead.add(self)
            self.death("t")

        elif self.age >= self.death_date:  # death by age
            self.world.tick_dead.add(self)
            self.death("a")

    def _death_prob_temp(self):
        """
        Temperature death probabilities calculation
        
        :return: the probablity to die for temperature reasons
        """
        t = self.world.chunks_vars['temperature_max']
        temp_resist = self.genes['temp_resist'].get()
        if temp_resist == 'c':
            return ((self._actual_chunk().temperature ** 2 / (4 * (self.world.chunks_vars['temperature_max'] ** 2))) - (
                self._actual_chunk().temperature / (2 * self.world.chunks_vars['temperature_max'])) + (1 / 4)) / \
                   self.world.creatures_vars['temp_death_prob_coeff']

        elif temp_resist == 'l':
            return ((self._actual_chunk().temperature ** 2 / (4 * (t ** 2))) + (
                self._actual_chunk().temperature / (2 * t)) + (1 / 4)) / self.world.creatures_vars[
                       'temp_death_prob_coeff']

        elif temp_resist == 'N' or temp_resist == 'n':
            return ((self._actual_chunk().temperature ** 2) / (self.world.chunks_vars['temperature_max'] ** 2)) / \
                   self.world.creatures_vars['temp_death_prob_coeff']

    def _dest_calc(self):
        """
        Evaluates the most convenient chunk to go to
        
        :return:
        """

        x = self._chunk_coord(0)
        y = self._chunk_coord(1)
        maxEn = float("-inf")

        for i in range(max(x - self.world.creatures_vars['view_ray'], 0),
                       min(x + self.world.creatures_vars['view_ray'] + 1, self.world.dimension[0])):
            for j in range(max(y - self.world.creatures_vars['view_ray'], 0),
                           min(y + self.world.creatures_vars['view_ray'] + 1, self.world.dimension[1])):

                if self.world.chunk_list[i][j].food * self.genes['eat_coeff'].get() * self.world.creatures_vars[
                    'en_inc_coeff'] - self._energy_consume(i, j) > maxEn:
                    maxEn = self.world.chunk_list[i][j].food * self.genes['eat_coeff'].get() * \
                            self.world.creatures_vars[
                                'en_inc_coeff'] - self._energy_consume(i, j)
                    self.dest_chunk = [i, j]

        self.dest_coord = [(self.dest_chunk[0] + 0.5) * self.world.chunk_dim, (
            self.dest_chunk[1] + 0.5) * self.world.chunk_dim]

    def _step(self):
        """
        Changes the coordinates of the creature
        
        :return:
        """

        self._actual_chunk().chunk_creature_list.remove(
            self)
        speed = self.genes['speed'].get()
        self.coord[0] += (self.dest_coord[0] - self.coord[0]) / math.sqrt((self.dest_coord[0] - self.coord[0]) ** 2 + (
            self.dest_coord[1] - self.coord[1]) ** 2) * speed
        self.coord[1] += (self.dest_coord[1] - self.coord[1]) / math.sqrt(
            (self.dest_coord[0] - self.coord[0]) ** 2 + (self.dest_coord[1] - self.coord[1]) ** 2) * speed

        self._actual_chunk().chunk_creature_list.append(
            self)

    def _eat(self):
        """
        Increases the energy of the creature by eating and consequently decreases the food in the chunk

        :return:
        """
        food_eaten = self._actual_chunk().food * self.genes['eat_coeff'].get()
        self.energy += food_eaten * self.world.creatures_vars['en_inc_coeff']
        self._actual_chunk().food -= food_eaten
        self.energy = min(self.energy, 100)

    def _energy_consume(self, x, y):
        """
        Evaluates the quantity of the energy that would be used to reach
        another chunk
        
        :param x: first coordinate of the destination chunk to reach
        :type x: int
        :param y: second coordinate of the destination chunk to reach
        :type y: int
        :return: energy consumption value
        """

        return (math.sqrt(
            (x * self.world.chunk_dim + 5 - self.coord[0]) ** 2 + (y * self.world.chunk_dim + 5 - self.coord[1]) ** 2) /
                self.genes['speed'].get()) * self.world.creatures_vars['en_dec_coeff'] * self.energy

    def _chunk_coord(self, i):
        """
        Evaluates the chunk coordinates where the creature is
        
        :param i: indicates which coordinate is considered (0 for the x coordinate1 for the y coordinate)
        :type i: int
        :return: the chunk coordinates
        """
        return min(int(self.coord[i] / self.world.chunk_dim), self.world.dimension[i]) - 1

    def _dating_agency(self):
        """
        Searches a mate to reproduct with. Finds the mate and activates the reproduction function
        
        :return:
        """
        for i in self._actual_chunk().chunk_creature_list:

            if i.reprod_ready and i.sex != self.sex:
                self._reproduction(i)
                self.reprod_ready = False
                i.reprod_ready = False

    def _reproduction(self, other):
        """
        Creates a new creature from the two parents
        
        :param other: mate creature
        :type other: Creature object
        :return:
        """
        genes = dict()
        start_coord = [0, 0]
        sex = int(rnd() * 2)
        for i in range(2):
            start_coord[i] = (self.coord[i] + other.coord[i]) / 2
        energy = (self.energy + other.energy) / 2
        for i in self.genes:
            genes[i] = self.genes[i].reproduce(other.genes[i], self.world.creatures_vars['mutation_coeff'])
        Creature(self.world, start_coord, (self.ID, other.ID), energy, sex, genes)

    def end(self):
        """
        Saves the data of the creature at the end of the simulation

        :return:
        """
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], self.world.analysis['rounding'])
        for i in self.tick_history:
            to_write += utl.history_to_write(i)
        try:
            self.world.files['creatures_data'].write(to_write[:-1] + '\n')
        except ValueError:
            print('dio')
