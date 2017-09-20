import math
import random
from random import random as rnd


# from .world import World


class Creature:
    '''class of creatures'''

    def __init__(self, world, x, y, parents_ID, energy, sex, genes, start_count=0):
        '''creatures constructor'''
        self.world = world
        self.ID = self.world.get_ID()
        self.coord = [x, y]  # creature's starting coord definition
        self.parents_ID = parents_ID
        self.tick_history = str()
        self.birth_tick = self.world.tick_count - start_count  # creature's creation tick definition (startCount is used only during diversification at start)
        self.energy = energy  # creature's starting energy definition
        self.actual_chunk().chunkCreatureList.append(self)  # creature's adding to the list of creatures in its chunk
        self.reprod_ready = False  # reproduction capacity set to false
        self.death_date = int(random.gauss(self.world.cr_averageAge, self.world.cr_deviationAgeProb))  # crearture's age of death definition
        self.age = 0  # age set to 0
        self.dest_chunk = [self.chunk_coord(0), self.chunk_coord(1)]
        self.sex = sex

        # creature's genes definition
        self.genes = genes
        self.reprod_countdown = self.genes['fertility']

        # phenotypical characteristics valuation

        self.world.newBorn.add(self)  # creature's adding to the list of creatures

    def phenotype_calc(self):
        self.genes['temp_resist'] = self.temp_resist_calc(self.genes['temp_resist_gen'])
        self.genes['speed'] = (self.genes['agility'] / self.genes['bigness']) * 2
        self.genes['eat_coeff'] = self.genes['bigness'] * self.world.cr_eatCoeffMax

    def __del__(self, cause="e"):
        """creature's destructor"""
        self.death_tick = self.world.tickCount
        self.death_cause = cause
        try:
            self.world.creaturesData.write(
                f"{self.ID};{self.birth_tick};{self.parents_ID[0]},{self.parents_ID[1]};{self.genes['temp_resist']Gen};{round(self.genes['agility'],4)};"
                f"{round(self.genes['bigness'],4)};{self.sex};{round(self.genes['fertility'],4)};{self.genes['temp_resist']};{round(self.genes['speed'],4)};{round(self.genes['eat_coeff'],6)};"
                f"{round(self.genes['num_control_gene'],4)};{self.death_tick};{self.death_cause};{self.tick_history[:-1]}\n")
        except ValueError:
            pass

    def update(self):
        """creature update/AI method"""

        # reproduction control
        if self.energy > 50 and self.reprod_countdown <= 0:
            self.reprod_ready = True
            self.dating_agency()

        else:
            self.reprod_ready = False
            self.reprod_countdown -= 1

        # food search
        self.dest_calc()
        if not [self.chunk_coord(0),
                self.chunk_coord(1)] == self.dest_chunk:
            self.step()

        else:
            self.eat()

        # creature's variables update
        self.energy -= self.world.cr_enDecCoeff * self.energy  # energy decrease every tick
        self.age += 1

        # death control
        self.tick_history += f"{round(self.coord[0],2)},{round(self.coord[1],2)},{int(self.energy)},{int(self.reprod_ready)}/"
        self.death_control()

    def actual_chunk(self):
        """returns Chunk object in which the creature is"""
        return self.world.chunkList[self.chunk_coord(0)][self.chunk_coord(1)]

    def death_control(self):
        '''death control method'''
        if self.energy < 10:  # starvation death
            self.world.tickDead.add(self)
            self.__del__("s")

        elif rnd() <= self.death_prob_temp():  # temperature death
            self.world.tickDead.add(self)
            self.__del__("t")

        elif self.age >= self.death_date:  # death by age
            self.world.tickDead.add(self)
            self.__del__("a")

    def death_prob_temp(self):
        '''temperature death probabilities calc'''
        t = self.world.ch_temperatureMax
        if self.genes['temp_resist'] == "c":
            return ((self.actual_chunk().temperature ** 2 / (4 * (self.world.ch_temperatureMax ** 2))) - (self.actual_chunk().temperature / (2 * self.world.ch_temperatureMax)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.genes['temp_resist'] == "l":
            return ((self.actual_chunk().temperature ** 2 / (4 * (t ** 2))) + (self.actual_chunk().temperature / (2 * t)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.genes['temp_resist'] == "N" or self.genes['temp_resist'] == "n":
            return ((self.actual_chunk().temperature ** 2) / (self.world.ch_temperatureMax ** 2)) / self.world.cr_tempDeathProbCoeff

    def dest_calc(self):
        '''most convenient chunk calc'''

        x = self.chunk_coord(0)
        y = self.chunk_coord(1)
        maxEn = float("-inf")

        for i in range(max(x - self.world.cr_viewRay, 0), min(x + self.world.cr_viewRay + 1, int(
                        (self.world.width) / self.world.chunkDim))):
            for j in range(max(y - self.world.cr_viewRay, 0), min(y + self.world.cr_viewRay + 1, int(
                            (self.world.height) / self.world.chunkDim))):

                if self.world.chunkList[i][j].food * self.genes['eat_coeff'] * self.world.cr_enIncCoeff - self.energy_consume(i,
                                                                                                                              j) > maxEn:
                    maxEn = self.world.chunkList[i][
                                j].food * self.genes['eat_coeff'] * self.world.cr_enIncCoeff - self.energy_consume(i, j)
                    self.dest_chunk = [i, j]

        self.dest_coord = [(self.dest_chunk[0] + 0.5) * self.world.chunkDim, (
            self.dest_chunk[1] + 0.5) * self.world.chunkDim]

    def step(self):
        '''creature's new position calc'''

        self.actual_chunk().chunkCreatureList.remove(
            self)

        self.coord[0] += (self.dest_coord[0] - self.coord[0]) / math.sqrt((self.dest_coord[0] - self.coord[0]) ** 2 + (
            self.dest_coord[1] - self.coord[1]) ** 2) * self.genes['speed']
        self.coord[1] += (self.dest_coord[1] - self.coord[1]) / math.sqrt(
            (self.dest_coord[0] - self.coord[0]) ** 2 + (self.dest_coord[1] - self.coord[1]) ** 2) * self.genes['speed']

        self.actual_chunk().chunkCreatureList.append(
            self)

    def eat(self):
        '''energy and chunk's remaining food update'''
        food_eaten = self.actual_chunk().food * self.genes['eat_coeff']
        self.energy += food_eaten * self.world.cr_enIncCoeff
        self.actual_chunk().food -= food_eaten
        self.energy = min(self.energy, 100)

    def energy_consume(self, x, y):
        '''energy consumption to reach a chunk'''

        return (math.sqrt((x * self.world.chunkDim + 5 - self.coord[0]) ** 2 + (
            y * self.world.chunkDim + 5 - self.coord[1]) ** 2) / self.genes['speed']) * self.world.cr_enDecCoeff * self.energy

    def chunk_coord(self, i):
        '''returns chunk cord of the creature chunk'''
        if i == 0:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.width / self.world.chunkDim) - 1)
        else:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.height / self.world.chunkDim) - 1)

    def dating_agency(self):
        '''reproduction mate finder in the chunk. If there is someone "available", the creature reproduces itself'''

        for i in self.actual_chunk().chunkCreatureList:

            if i.reprodReady and i.sex != self.sex:
                self.reproduction(i)
                self.reprod_ready = False
                i.reprodReady = False

    def reproduction(self, shelf):
        '''reproduction method'''

        x = (self.coord[0] + shelf.coord[0]) / 2
        y = (self.coord[1] + shelf.coord[1]) / 2
        energy = (self.energy + shelf.energy) / 2
        sex = int(rnd() * 2)

        genes = dict()

        genes['temp_resist_gen'] = self.genes['temp_resist_gen'][int(rnd() * 2)] + shelf.genes['temp_resist_gen'][int(rnd() * 2)]
        # TO Do: for to reproduce genes VVVV
        genes['agility'] = (self.genes['agility'] + shelf.genes['agility']) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        genes['bigness'] = (self.genes['bigness'] + shelf.genes['bigness']) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        genes['fertility'] = (self.genes['fertility'] + shelf.genes['fertility']) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        genes['num_control_gene'] = (self.genes['num_control_gene'] + shelf.genes['num_control_gene']) / 2 + random.gauss(0, self.world.cr_mutationCoeff)

        Creature(self.world, x, y, (self.ID, shelf.ID), energy, sex, genes)

    def temp_resist_calc(self, gen):
        '''creature's phenotipyc expression of the temperature calc'''
        if gen[0] == "N" or gen[1] == "N":
            return "N"

        elif gen == "ll":
            return "l"

        elif gen == "cc":
            return "c"

        else:
            return "n"
