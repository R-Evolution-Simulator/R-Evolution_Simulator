import os
import shutil
from random import random as rnd

from .noise.simplexnoise.noise import SimplexNoise
from .chunk import Chunk
from .creature import Creature
from . import vars


class World:
    """class of the world where creatures live"""

    def __init__(self, name, width=vars.DEFAULT_WIDTH, height=vars.DEFAULT_HEIGHT, lifetime=vars.DEFAULT_LIFETIME,
                 initialCreatures=vars.DEFAULT_INITIALCREATURES, chunkDim=vars.DEFAULT_CHUNKDIM,
                 ch_growthCoeff=vars.DEFAULT_CH_GROWTHCOEFF, ch_foodMaxMax=vars.DEFAULT_CH_FOODMAXMAX,
                 ch_temperatureMax=vars.DEFAULT_CH_TEMPERATUREMAX,
                 cr_viewRay=vars.DEFAULT_CR_VIEWRAY,
                 cr_enDecCoeff=vars.DEFAULT_CR_ENDECCOEFF,
                 cr_enIncCoeff=vars.DEFAULT_CR_ENINCCOEFF,
                 cr_averageAge=vars.DEFAULT_CR_AVERAGEAGE,
                 cr_deviationAgeProb=vars.DEFAULT_CR_DEVIATIONAGEPROB,

                 cr_tempDeathProbCoeff=vars.DEFAULT_CR_TEMPDEATHPROBCOEFF,

                 cr_genesLim=vars.DEFAULT_CR_GENESLIM, cr_mutationCoeff=vars.DEFAULT_CR_MUTATIONCOEFF,

                 cr_eatCoeffMax=vars.DEFAULT_CR_EATCOEFFMAX):
        print(f"{name}: simulation setup")
        self.name = name
        self.path = os.path.join(vars.SIMULATIONS_PATH, name)

        self.width = width
        self.height = height
        self.lifetime = lifetime
        self.initialCreatures = initialCreatures
        self.chunkDim = chunkDim
        self.tickCount = 0

        self.ch_growthCoeff = ch_growthCoeff
        self.ch_foodMaxNoise = SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700)
        self.ch_temperatureNoise = SimplexNoise(num_octaves=7, persistence=0.1, dimensions=2, noise_scale=700)
        self.ch_foodMaxMax = ch_foodMaxMax
        self.ch_temperatureMax = ch_temperatureMax

        self.cr_viewRay = cr_viewRay
        self.cr_enDecCoeff = cr_enDecCoeff
        self.cr_enIncCoeff = cr_enIncCoeff
        self.cr_averageAge = cr_averageAge
        self.cr_deviationAgeProb = cr_deviationAgeProb
        self.cr_tempDeathProbCoeff = cr_tempDeathProbCoeff
        self.cr_genesLim = cr_genesLim
        self.cr_eatCoeffMax = cr_eatCoeffMax
        self.cr_creaturesIDCount = 1
        self.cr_mutationCoeff = cr_mutationCoeff

        self.directorySetup()

        self.chunkList = [[0 for x in range(0, height, chunkDim)] for y in
                          range(0, width, chunkDim)]  # viene riempita una matrice di 0
        self.creatureList = set()
        self.tickDead = set()
        self.newBorn = set()

        print(f"        - creating chunks")
        for i in range(len(self.chunkList)):  # quindi ogni 0 e' sostituito con un Chunk
            for j in range(len(self.chunkList[0])):
                self.chunkList[i][j] = Chunk(self, i, j)

        print(f"        - creating creatures")
        for i in range(initialCreatures):
            Creature(*self.creatureRandomization())

        self.creatureList = self.newBorn
        print(f"{self.name}: simulation setup done")

    def directorySetup(self):
        """
        method which creates a new directory for the simulation
        and deletes it if it already exists
        """
        try:
            os.makedirs(self.path)
        except FileExistsError:
            if "y" == input(f"Simulation \"{self.name}\" already exists. Overwrite it? y/n"):
                shutil.rmtree(self.path)
                os.makedirs(self.path)
            else:
                exit()
        self.simulationData = open(os.path.join(self.path, "simulationData.csv"), 'w')
        self.creaturesData = open(os.path.join(self.path, "creaturesData.csv"), 'w')
        self.chunkData = open(os.path.join(self.path, "chunkData.csv"), 'w')

    def __del__(self):
        """
        closing simulation and files
        """
        print(f"{self.name}: simulation ending...")
        print(f"        - deleting creatures")
        for i in self.creatureList:
            try:
                i.__del__()
            except AttributeError:
                print("--error closing creature")
        print(f"        - deleting chunks")
        for i in self.chunkList:
            for j in i:
                try:
                    j.__del__()
                except AttributeError:
                    print("error")
        try:
            self.simulationData.write(
                f"{self.name};{self.width};{self.height};{self.lifetime};{self.initialCreatures};{self.chunkDim};{self.tickCount};{self.ch_growthCoeff};{self.ch_foodMaxNoise};{self.ch_temperatureNoise};{self.ch_foodMaxMax};{self.ch_temperatureMax};{self.cr_viewRay};{self.cr_enDecCoeff};{self.cr_enIncCoeff};{self.cr_averageAge};{self.cr_deviationAgeProb};{self.cr_tempDeathProbCoeff};{self.cr_genesLim};{self.cr_eatCoeffMax};{self.cr_creaturesIDCount};{self.cr_mutationCoeff}")
        except ValueError:
            pass
        print(f"        - closing files")
        self.simulationData.close()
        self.creaturesData.close()
        self.chunkData.close()
        print(f"{self.name}: simulation ended")

    def creatureRandomization(self):
        """
        function which returns a tuple with creature's characteristics
        """
        # calcolo delle caratteristiche della nuova creatura (random)
        x = rnd() * self.width
        y = rnd() * self.height
        energy = 50 + rnd() * 100
        tempResist = "Nlc"
        tempResistGen = tempResist[int(rnd() * 3)] + tempResist[int(rnd() * 3)]
        agility = self.cr_genesLim["agility"][0] + rnd() * (
            self.cr_genesLim["agility"][1] - self.cr_genesLim["agility"][0])
        bigness = self.cr_genesLim["bigness"][0] + rnd() * (
            self.cr_genesLim["bigness"][1] - self.cr_genesLim["bigness"][0])
        sex = int(rnd() * 2)
        fertility = self.cr_genesLim["fertility"][0] + rnd() * (
            self.cr_genesLim["fertility"][1] - self.cr_genesLim["fertility"][0])
        numControlGene = self.cr_genesLim["numControlGene"][0] + rnd() * (
            self.cr_genesLim["numControlGene"][1] - self.cr_genesLim["numControlGene"][0])

        # creazione della creatura con le caratteristiche calcolate
        return (
            self, x, y, (0, 0), energy, tempResistGen, agility, bigness, sex, fertility, numControlGene,
            int(rnd() * (self.cr_averageAge / 2)))

    def run(self):
        """
        method which execute the simulation
        """
        print(f"{self.name}: simulation running...")
        for i in range(self.lifetime):
            if i % 100 == 0:
                print(f"        - tick #{i}")
            self.update()
        print(f"{self.name}: run finished")
        self.__del__()

    def update(self):
        """
        method which update all the characteristics of creatures and chunks
        """
        self.tickCount += 1
        self.tickDead = set()
        self.newBorn = set()

        for i in self.chunkList:
            for j in i:
                j.update()  # viene aggiornata ogni unita' di territorio

        # update delle creature
        for i in self.creatureList:
            i.update()  # viene aggiornata ogni creatura
        for i in self.newBorn:
            i.update()
        self.creatureList = self.creatureList | self.newBorn
        self.creatureList -= self.tickDead
