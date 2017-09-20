from .noise.simplexnoise.noise import normalize
from . import vars
from . import utility as utl


class Chunk:
    """class of chunk (unity of territory)"""
    NOISE_ATTRS = vars.CHUNK_NOISE_ATTRS
    TO_RECORD = vars.TO_RECORD['chunk']

    def __init__(self, world, x, y):
        '''constructor of Chunk'''
        self.coord = (x, y)
        # food
        self.world = world
        for i in self.NOISE_ATTRS:
            self.__dict__[i] = normalize(self.world.noises[i].noise(x, y)) * self.world.chunks_vars[i + '_max']
        self.food = self.foodmax / 2  # all'inizio il cibo e' al massimo
        self.growth_rate = self.foodmax * self.world.chunks_vars['growth_coeff']  # la crescita e' direttamente proporzionale all'erba massima
        self.food_history = list()
        self.chunk_creature_list = []

    def update(self):
        '''chunk update method'''
        self.food *= (1 + self.growth_rate)  # ad ogni ciclo l'erba cresce
        if self.food > self.foodmax:  # finche' non raggiunge il massimo
            self.food = self.foodmax

        self.food_history.append((int(self.food),))

    def death(self):
        """chunk destructor"""
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], vars.ROUNDINGS['chunk'])
        for i in self.food_history:
            to_write += utl.history_to_write(i)
        try:
            self.world.files['chunk_data'].write(to_write[:-1] + '\n')
        except ValueError:
            pass