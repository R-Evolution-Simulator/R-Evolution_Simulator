import math
import random
from random import random as rnd


# from .world import World


class Creature:
    '''class of creatures'''

    def __init__(self, world, x, y, parentsID, energy, tempResistGen, agility, bigness, sex, fertility, numControlGene, startCount=0):
        '''creatures constructor'''
        self.world = world
        self.ID = self.world.cr_creaturesIDCount
        self.coord = [x, y]  # creatture's starting coord definition
        self.parentsID = parentsID
        self.tickHistory = ""
        self.birthTick = self.world.tickCount - startCount  # creature's creation tick definition (startCount is used only during diversification at start)
        self.energy = energy  # creature's starting energy definition
        self.chunkIn().chunkCreatureList.append(self)  # creature's adding to the list of creatures in its chunk
        self.reprodReady = False  # reproduction capacity set to false
        self.deathDate = int(random.gauss(self.world.cr_averageAge, self.world.cr_deviationAgeProb))  # crearture's age of death definition
        self.age = 0  # age set to 0
        self.destChunk = [self.chunkCoord(0), self.chunkCoord(1)]

        # creature's genes definition
        self.tempResistGen = tempResistGen  # it can be N (normal), c (short fur), l (long fur)
        self.agility = agility
        self.bigness = bigness
        self.sex = sex
        self.fertility = fertility
        self.reprodCountdown = fertility
        self.numControlGene = numControlGene

        # phenotypic characteristics valuation
        self.tempResist = self.tempResistCalc(self.tempResistGen)
        self.speed = (self.agility / self.bigness) * 2
        self.eatCoeff = self.bigness * self.world.cr_eatCoeffMax

        self.world.cr_creaturesIDCount += 1

        self.world.newBorn.add(self)  # creature's adding to the list of creatures

    def __del__(self, cause="e"):
        """creature's destructor"""
        self.deathTick = self.world.tickCount
        self.deathCause = cause
        try:
            self.world.creaturesData.write(
                f"{self.ID};{self.birthTick};{self.parentsID[0]},{self.parentsID[1]};{self.tempResistGen};{self.agility};{self.bigness};{self.sex};{self.fertility};{self.tempResist};{self.speed};{self.eatCoeff};{self.numControlGene};{self.deathTick};{self.deathCause};{self.tickHistory[:-1]}\n")
        except ValueError:
            pass

    def update(self):
        """creature update/AI method"""

        # reproduction control
        if self.energy > 50 and self.reprodCountdown <= 0:
            self.reprodReady = True
            self.datingAgency()

        else:
            self.reprodReady = False
            self.reprodCountdown -= 1

        # food search
        self.destCalc()
        if not [self.chunkCoord(0),
                self.chunkCoord(1)] == self.destChunk:
            self.step()

        else:
            self.eat()

        # creature's variables update
        self.energy -= self.world.cr_enDecCoeff * self.energy  # energy decrease every tick
        self.age += 1

        # death control
        self.tickHistory += f"{round(self.coord[0],2)},{round(self.coord[1],2)},{int(self.energy)},{int(self.reprodReady)}/"
        self.deathControl()

    def chunkIn(self):
        """returns Chunk object in which the creature is"""
        return self.world.chunkList[self.chunkCoord(0)][self.chunkCoord(1)]

    def deathControl(self):
        '''death control method'''
        if self.energy < 10:  # starvation death
            self.world.tickDead.add(self)
            self.__del__("s")

        elif rnd() <= self.deathProbTemp():  # temperature death
            self.world.tickDead.add(self)
            self.__del__("t")

        elif self.age >= self.deathDate:  # death by age
            self.world.tickDead.add(self)
            self.__del__("a")

    def deathProbTemp(self):
        '''temperature death probabilities calc'''
        t = self.world.ch_temperatureMax
        if self.tempResist == "c":
            return ((self.chunkIn().temperature ** 2 / (4 * (self.world.ch_temperatureMax ** 2))) - (self.chunkIn().temperature / (2 * self.world.ch_temperatureMax)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.tempResist == "l":
            return ((self.chunkIn().temperature ** 2 / (4 * (t ** 2))) + (self.chunkIn().temperature / (2 * t)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.tempResist == "N" or self.tempResist == "n":
            return ((self.chunkIn().temperature ** 2) / (self.world.ch_temperatureMax ** 2)) / self.world.cr_tempDeathProbCoeff

    def destCalc(self):
        '''most convenient chunk calc'''

        x = self.chunkCoord(0)
        y = self.chunkCoord(1)
        maxEn = float("-inf")

        for i in range(max(x - self.world.cr_viewRay, 0), min(x + self.world.cr_viewRay + 1, int(
                        (self.world.width) / self.world.chunkDim))):
            for j in range(max(y - self.world.cr_viewRay, 0), min(y + self.world.cr_viewRay + 1, int(
                            (self.world.height) / self.world.chunkDim))):

                if self.world.chunkList[i][j].food * self.eatCoeff * self.world.cr_enIncCoeff - self.energyConsume(i,
                                                                                                                   j) > maxEn:
                    maxEn = self.world.chunkList[i][
                                j].food * self.eatCoeff * self.world.cr_enIncCoeff - self.energyConsume(i, j)
                    self.destChunk = [i, j]

        self.destCoord = [(self.destChunk[0] + 0.5) * self.world.chunkDim, (
            self.destChunk[1] + 0.5) * self.world.chunkDim]

    def step(self):
        '''creature's new position calc'''

        self.chunkIn().chunkCreatureList.remove(
            self)

        self.coord[0] += (self.destCoord[0] - self.coord[0]) / math.sqrt((self.destCoord[0] - self.coord[0]) ** 2 + (
            self.destCoord[1] - self.coord[1]) ** 2) * self.speed
        self.coord[1] += (self.destCoord[1] - self.coord[1]) / math.sqrt(
            (self.destCoord[0] - self.coord[0]) ** 2 + (self.destCoord[1] - self.coord[1]) ** 2) * self.speed

        self.chunkIn().chunkCreatureList.append(
            self)

    def eat(self):
        '''energy and chunk's remaining food update'''
        foodEaten = self.chunkIn().food * self.eatCoeff
        self.energy += foodEaten * self.world.cr_enIncCoeff
        self.chunkIn().food -= foodEaten
        self.energy = min(self.energy, 100)

    def energyConsume(self, x, y):
        '''energy consumption to reach a chunk'''

        return (math.sqrt((x * self.world.chunkDim + 5 - self.coord[0]) ** 2 + (
            y * self.world.chunkDim + 5 - self.coord[1]) ** 2) / self.speed) * self.world.cr_enDecCoeff * self.energy

    def chunkCoord(self, i):
        '''returns chunk cord of the creature chunk'''
        if i == 0:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.width / self.world.chunkDim) - 1)
        else:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.height / self.world.chunkDim) - 1)

    def datingAgency(self):
        '''reproduction mate finder in the chunk. If there is someone "available", the creature reproduces itself'''

        for i in self.chunkIn().chunkCreatureList:

            if i.reprodReady and i.sex != self.sex:

                self.reproduction(i)
                self.reprodReady = False
                i.reprodReady = False

    def reproduction(self, shelf):
        '''reproduction method'''

        x = (self.coord[0] + shelf.coord[0]) / 2
        y = (self.coord[1] + shelf.coord[1]) / 2
        energy = (self.energy + shelf.energy) / 2
        tempResistGen = self.tempResistGen[int(rnd() * 2)] + shelf.tempResistGen[
            int(rnd() * 2)]
        agility = (self.agility + shelf.agility) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        bigness = (self.bigness + shelf.bigness) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        sex = int(rnd() * 2)
        fertility = (self.fertility + shelf.fertility) / 2 + random.gauss(0, self.world.cr_mutationCoeff)
        numControlGene = (self.numControlGene + shelf.numControlGene) / 2 + random.gauss(0, self.world.cr_mutationCoeff)

        Creature(self.world, x, y, (self.ID, shelf.ID), energy, tempResistGen, agility, bigness, sex, fertility, numControlGene)

    def tempResistCalc(self, gen):
        '''creature's phenotipyc expression of the temperature calc'''
        if gen[0] == "N" or gen[1] == "N":
            return "N"

        elif gen == "ll":
            return "l"

        elif gen == "cc":
            return "c"

        else:
            return "n"
