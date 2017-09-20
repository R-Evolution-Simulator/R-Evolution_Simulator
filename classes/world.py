import os
import shutil
from random import random as rnd

from .noise.simplexnoise.noise import SimplexNoise
from .chunk import Chunk
from .creature import Creature
from . import vars


class World:
    """class of the world where creatures live"""

    def __init__(self, name, sim_variables):
        print(f"{name}: simulation setup")
        self.name = name
        self.path = os.path.join(vars.SIMULATIONS_PATH, name)
        self.__dict__.update(sim_variables)
        self.tick_count = 0
        self.noises = {'food_max': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700),
                       'temperature': SimplexNoise(num_octaves=7, persistence=0.1, dimensions=2, noise_scale=700)}
        self.ID_count = 0
        self.files = dict()
        self.chunk_list = [[0 for x in range(0, self.height, self.chunk_dim)] for y in range(0, self.width, self.chunk_dim)]  # viene riempita una matrice di 0
        self.creature_list = set()
        self.tick_dead = set()
        self.new_born = set()
        self.directory_setup()

        print(f"        - creating chunks")
        for i in range(len(self.chunk_list)):  # quindi ogni 0 e' sostituito con un Chunk
            for j in range(len(self.chunk_list[0])):
                self.chunk_list[i][j] = Chunk(self, i, j)

        print(f"        - creating creatures")
        for i in range(self.initial_creatures):
            Creature(*self.creature_randomization())

        self.creature_list = self.new_born
        print(f"{self.name}: simulation setup done")

    def directory_setup(self):
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
        self.files['simulation_data'] = open(os.path.join(self.path, "simulationData.csv"), 'w')
        self.files['creatures_data'] = open(os.path.join(self.path, "creaturesData.csv"), 'w')
        self.files['chunk data'] = open(os.path.join(self.path, "chunkData.csv"), 'w')

    def __del__(self):
        """
        closing simulation and files
        """
        print(f"{self.name}: simulation ending...")
        print(f"        - deleting creatures")
        for i in self.creature_list:
            try:
                i.__del__()
            except AttributeError:
                print("--error closing creature")
        print(f"        - deleting chunks")
        for i in self.chunk_list:
            for j in i:
                try:
                    j.__del__()
                except AttributeError:
                    print("error")
        try:
            self.simulationData.write(
                f"{self.name};{self.width};{self.height};{self.lifetime};{self.initial_creatures};{self.chunk_dim};{self.tick_count};{self.ch_growthCoeff};{self.ch_foodMaxNoise};{self.ch_temperatureNoise};{self.ch_foodMaxMax};{self.ch_temperatureMax};{self.cr_viewRay};{self.cr_enDecCoeff};{self.cr_enIncCoeff};{self.cr_averageAge};{self.cr_deviationAgeProb};{self.cr_tempDeathProbCoeff};{self.cr_genesLim};{self.cr_eatCoeffMax};{self.ID_count};{self.cr_mutationCoeff}")
        except ValueError:
            pass
        print(f"        - closing files")
        self.simulationData.close()
        self.creaturesData.close()
        self.chunkData.close()
        print(f"{self.name}: simulation ended")

    def creature_randomization(self):
        """
        function which returns a tuple with creature's characteristics
        """
        # calcolo delle caratteristiche della nuova creatura (random)
        x = rnd() * self.width
        y = rnd() * self.height
        energy = 50 + rnd() * 100
        sex = int(rnd() * 2)
        lims = self.creatures_vars['genes_lim']
        temp_resist = "Nlc"
        genes = {'temp_resist': temp_resist[int(rnd() * 3)] + temp_resist[int(rnd() * 3)]}
        for i in lims:
            genes[i] = rnd() * (lims[i][1] - lims[i][0])

        # creazione della creatura con le caratteristiche calcolate
        return (self, x, y, (0, 0), energy, sex, genes, int(rnd() * (self.creatures_vars['average_age'] / 2)))

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
        self.tick_count += 1
        self.tick_dead = set()
        self.new_born = set()

        for i in self.chunk_list:
            for j in i:
                j.update()  # viene aggiornata ogni unita' di territorio

        # update delle creature
        for i in self.creature_list:
            i.update()  # viene aggiornata ogni creatura
        for i in self.new_born:
            i.update()
        self.creature_list = self.creature_list | self.new_born
        self.creature_list -= self.tick_dead

    def get_ID(self):
        self.ID_count += 1
        return self.ID_count
