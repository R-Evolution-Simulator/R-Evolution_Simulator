import os
import shutil
from random import random as rnd

from .noise.simplexnoise.noise import SimplexNoise
from .chunk import Chunk
from .creature import Creature
from . import var
from . import utility as utl


class World:
    """class of the world where creatures live"""
    TO_RECORD = var.TO_RECORD['simulation']

    def __init__(self, name, sim_variables):
        """
        Creates new simulation

        :param name: name of the simulation
        :type name: str
        :param sim_variables: paramaters of the simulation
        :type sim_variables: dict
        :return:
        """
        print(f"{name}: simulation setup")
        self.name = name
        self.path = os.path.join(var.SIMULATIONS_PATH, name)
        self.__dict__.update(sim_variables)
        self.tick_count = 0
        self.noises = {'foodmax': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700),
                       'temperature': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700)}
        self.ID_count = 0
        self.files = dict()
        self.chunk_list = [[None for x in range(self.dimension[1])] for y in
                           range(self.dimension[0])]  # viene riempita una matrice di 0
        self.creature_list = set()
        self.alive_creatures = set()
        self.tick_dead = set()
        self.new_born = set()
        self._directory_setup()

        print(f"        - creating chunks")
        for i in range(len(self.chunk_list)):  # quindi ogni 0 e' sostituito con un Chunk
            for j in range(len(self.chunk_list[0])):
                self.chunk_list[i][j] = Chunk(self, (i, j))

        print(f"        - creating creatures")
        for i in range(self.initial_creatures):
            Creature(*self._creature_randomization())

        self.creature_list = self.new_born
        self.alive_creatures = self.new_born
        print(f"{self.name}: simulation setup done")

    def run(self):
        """
        Calls update() one time per tick in lifetime

        :return:
        """
        print(f"{self.name}: simulation running...")
        for i in range(self.lifetime):
            if i % 100 == 0:
                print(f"        - tick #{i}")
            self._update()
        print(f"{self.name}: run finished")
        self._death()
        self._analysis()

    def get_ID(self):
        """
        Returns the ID of a new creature

        :return:
        """
        self.ID_count += 1
        return self.ID_count

    def _directory_setup(self):
        """
        Creates new directory for simulation and asks to remove it if it already exists

        :return:
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
        self.files['chunk_data'] = open(os.path.join(self.path, "chunkData.csv"), 'w')

    def _death(self):
        """
        Kills all creatures and chunks at the end of the simulation

        :return:
        """
        for i in self.chunk_list:
            for j in i:
                j.death()
        for i in self.creature_list:
            i.death()

    def __del__(self):
        """
        Deletes all creatures and chunks objects, saves simulation files and deletes the simulation object

        :return:
        """

        print(f"{self.name}: simulation ending...")
        print(f"        - deleting creatures")
        for i in self.creature_list:
            try:
                del (i)
            except AttributeError:
                print("--error closing creature")

        print(f"        - deleting chunks")
        for i in self.chunk_list:
            for j in i:
                try:
                    del (j)
                except AttributeError:
                    print("error")
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], var.ROUNDINGS['simulation'])
        try:
            self.files['simulation_data'].write(to_write[:-1])
        except ValueError:
            pass
        print(f"        - closing files")
        for i in self.files:
            self.files[i].close()
        print(f"{self.name}: simulation ended")

    def _creature_randomization(self):
        """
        Creates a tuple with random characteristics of a creatures

        :return: tuple
        """
        coord = [0, 0]
        for i in range(2):
            coord[i] = rnd() * self.dimension[i] * self.chunk_dim
        energy = 50 + rnd() * 100
        sex = int(rnd() * 2)
        lims = self.creatures_vars['genes_lim']
        genes_cls = var.CREATURES_GENES_CLASSES
        genes = dict()
        for i in genes_cls:
            new_gene = genes_cls[i]()
            try:
                new_gene.randomize(lims[i])
            except KeyError:
                new_gene.randomize()
            genes[i] = new_gene

        # creazione della creatura con le caratteristiche calcolate
        return (self, coord, (0, 0), energy, sex, genes, int(rnd() * (self.creatures_vars['average_age'] / 2)))

    def _update(self):
        """
        Updates all chunks and all creatures and adds newborn creatures and removes dead creatures from cratures list

        :return:
        """
        self.tick_count += 1
        self.tick_dead = set()
        self.new_born = set()

        for i in self.chunk_list:
            for j in i:
                j.update()

        j = 0
        for i in self.alive_creatures:
            j += 1
            i.update(self.tick_count)  # viene aggiornata ogni creatura
        if not j == len(self.alive_creatures):
            print('-----    ERROR')
        '''
        for i in self.new_born:
            i.update()
        '''
        self.creature_list = self.creature_list.union(self.new_born)
        self.alive_creatures = self.alive_creatures.union(self.new_born)
        self.alive_creatures.difference(self.tick_dead)

    def _tick_creature_list(self, tick, gene=None):
        """
        Gets the genes of the creatures alive in a specific tick or, if gene is None, a list of the creatures

        :param tick: the tick to search
        :type tick: int
        :param gene: the gene to return. if None, returns a list
        :return:
        """
        l = list()
        for i in self.creature_list:
            if i.birth_tick <= tick <= i.death_tick:
                l.append(i)
        if gene:
            s = list()
            for i in l:
                s.append(i.genes[gene])
            return sorted(s)
        return l

    def _analysis(self):
        """
        Analyses the different creatures genes and variables and prints it to the different files

        :return:
        """
        # TODO: Revise analysis and find why it doesn't work
        print(f"{self.name}: analysis setup")

        # analisi caratteristiche
        print(f"{self.name}: genes analysis")

        for k in var.NUM_GENES_LIST:
            self.files[k] = open(os.path.join(self.path, f"{k}.csv"), 'w')
            for i in range(0, self.lifetime, var.TIME_INTERVAL):
                l = self._tick_creature_list(i, k)
                to_write = str(i)
                for j in range(0, var.PERCENTILE_PARTS + 1):
                    to_write += var.FILE_SEPARATOR + str(l[round((j / var.PERCENTILE_PARTS) * (len(l) - 1))])
                to_write += var.FILE_SEPARATOR + str(sum(l) / float(len(l))) + '\n'
                self.files[k].write(to_write)

        self.files['population'] = open(os.path.join(self.path, f"population.csv"), 'w')
        for i in range(0, self.lifetime, var.TIME_INTERVAL):
            deaths = [0, 0, 0]
            born = 0
            for j in self.creature_list:
                if j.birth_tick >= i and j.birth_tick < i + var.TIME_INTERVAL:
                    born += 1
                if j.death_tick >= i and j.death_tick < i + var.TIME_INTERVAL:
                    if j.death_cause == "s":
                        deaths[0] += 1
                    elif j.death_cause == "t":
                        deaths[1] += 1
                    elif j.death_cause == "a":
                        deaths[2] += 1
            self.files['population'].write(str(i) + var.FILE_SEPARATOR + str(born) + var.FILE_SEPARATOR + str(
                deaths[0]) + var.FILE_SEPARATOR + str(deaths[1]) + var.FILE_SEPARATOR + str(deaths[2]) + '\n')

        chunk_attrs_spread = dict()
        for k in var.CHUNK_ATTRS:
            self.files[k] = open(os.path.join(self.path, f"{k}.csv"), 'w')
            parts = [0 for x in range(var.PARTS)]
            for i in self.chunk_list:
                for j in i:
                    val = min(j.__dict__[k], self.chunks_vars[k + '_max'] - 1)
                parts[int((val * var.PARTS) / (self.chunks_vars[k + '_max']))] += 1
            string = str()
            for i in range(0, 8):
                string += str(parts[i]) + var.FILE_SEPARATOR
            chunk_attrs_spread[k] = parts
            self.files[k].write(string[:-1] + '\n')

            # analisi disposizione
        print(f"{self.name}: spreading and deaths analysis")
        files = dict()
        strings = dict()
        for j in var.CHUNK_ATTRS_PARTS:
            files[j] = list()
            strings[j] = list()
            for i in range(var.CHUNK_ATTRS_PARTS[j]):
                files[j].append(open(os.path.join(self.path, f"{j}_{i}.csv"), 'w'))
                strings[j].append(str())
        for i in range(0, self.lifetime, 100):
            l = self._tick_creature_list(i)
            data = dict()
            for w in var.CHUNK_ATTRS:
                data[w] = dict()
                for k in ['raw', 'correct']:
                    data[w][k] = [[0 for x in range(var.PARTS)] for y in range(var.CHUNK_ATTRS_PARTS[w])]
                for j in l:
                    birth = max(j.birth_tick, 0)
                    coord = (j.tick_history[i - birth][0], j.tick_history[i - birth][1])
                    chunk_coord = (int(coord[0] / self.chunk_dim), int(coord[1] / self.chunk_dim))
                    print(chunk_coord)
                    val = min(self.chunk_list[chunk_coord[0]][chunk_coord[1]].__dict__[w],
                              self.chunks_vars[w + '_max'] - 1)
                    data[w]['raw'][utl.data_number(w, j)][
                        int((val * var.PARTS) // (self.chunks_vars[w + '_max']))] += 1

                x = 0
                for k in range(var.CHUNK_ATTRS_PARTS[w]):
                    strings[w][x] = str(i)
                    for j in range(var.PARTS):
                        if chunk_attrs_spread[w][j] == 0:
                            data[w]['correct'][x][j] = 0
                        else:
                            data[w]['correct'][x][j] = data[w]['raw'][x][j] / chunk_attrs_spread[w][j] * var.ADJ_COEFF
                        strings[w][x] += var.FILE_SEPARATOR + str(data[w]['raw'][x][j]) + var.FILE_SEPARATOR + str(
                            data[w]['correct'][x][j])
                    files[w][k] = open(os.path.join(self.path, f"{j}_{i}.csv"), 'w')
                    files[w][k].write(strings[w][x])
                    self.files[w + '_' + str(k)] = files[w][k]
                    x += 1
