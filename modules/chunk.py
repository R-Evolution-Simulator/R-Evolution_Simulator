from .noise.simplexnoise.noise import normalize
from . import var
from . import utility as utl


class Chunk:
    """
    chunk class
    """
    NOISE_ATTRS = var.CHUNK_ATTRS
    TO_RECORD = var.TO_RECORD['chunk']

    def __init__(self, world, coord):
        """
        Creates a new chunk object given the coords

        :param world: world object where the chunk is
        :type world: World
        :param coord: tuple with the coordinates of the chunk
        :type coord: tuple
        """
        self.coord = coord
        # food
        self.world = world
        for i in self.NOISE_ATTRS:
            self.__dict__[i] = normalize(self.world.noises[i].noise(*coord)) * self.world.chunks_vars[i + '_max']
        self.food = self.foodmax / 2  # all'inizio il cibo e' al massimo
        self.growth_rate = self.foodmax * self.world.chunks_vars[
            'growth_coeff']  # la crescita e' direttamente proporzionale all'erba massima
        self.food_history = list()
        self.chunk_creature_list = list()
        self.ticks_record = list()
        self._tick_record()

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
            self._tick_record()

    def _tick_record(self):
        self.ticks_record.append(self.chunk_creature_list)

    def end(self, file):
        """
        Saves the data of the chunk at the end of the simulation

        :param file: the file to write to
        :return:
        """
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], self.world.analysis['rounding'])
        file.write(to_write[:-1] + '\n')
