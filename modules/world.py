import os
import shutil
from random import random as rnd
import scipy
import numpy

from .noise.simplexnoise.noise import SimplexNoise
from .chunk import Chunk
from .creature import Creature
from . import var
from . import utility as utl
from . import genes as gns


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
        self.directories = dict()
        self.__dict__.update(sim_variables)
        self.tick_count = 0
        self.noises = {'foodmax': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700),
                       'temperature': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700)}
        self.ID_count = 0
        self.chunk_list = [[None for x in range(self.dimension[1])] for y in
                           range(self.dimension[0])]
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
        for i in range(self.max_lifetime):
            if i % 10 == 0:
                print(f"        - tick #{i} --- {len(self.alive_creatures)} alive")
            self._update()
            if len(self.alive_creatures) == 0:
                break
        self.lifetime = self.tick_count
        print(f"{self.name}: run finished")
        self._end()
        self._analysis()
        self._finalize()

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
            shutil.rmtree(self.path)
            os.makedirs(self.path)
        for i in var.DIRECTORIES:
            new_directory = os.path.join(self.path, i)
            os.makedirs(new_directory)
            self.directories[i] = new_directory

    def _end(self):
        """
        Kills all creatures and chunks at the end of the simulation

        :return:
        """
        with open(os.path.join(self.directories['data'], "chunks.csv"), 'w') as file:
            for i in self.chunk_list:
                for j in i:
                    j.end(file)
        for i in self.alive_creatures:
            i.death()
        with open(os.path.join(self.directories['data'], "creatures.csv"), 'w') as file:
            for i in self.creature_list:
                i.end(file)

    def _finalize(self):
        """
        Deletes all creatures and chunks objects, saves simulation files and deletes the simulation object

        :return:
        """

        print(f"{self.name}: simulation ending...")
        print(f"        - deleting creatures")
        for i in self.creature_list:
            try:
                del i
            except AttributeError:
                print("--error closing creature")

        print(f"        - deleting chunks")
        for i in self.chunk_list:
            for j in i:
                try:
                    del j
                except AttributeError:
                    print("error")
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], self.analysis['rounding'])
        with open(os.path.join(self.path, "params.csv"), 'w') as file:
            try:
                file.write(to_write[:-1])
            except ValueError:
                pass
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
        genes_cls = var.CREATURES_GENES
        genes = dict()
        for i in genes_cls:
            new_gene = genes_cls[i]()
            try:
                new_gene.randomize(lims[i])
            except KeyError:
                new_gene.randomize()
            genes[i] = new_gene
        genes['speed'] = gns.Speed({'agility': genes['agility'], 'bigness': genes['bigness']})

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

        for i in self.alive_creatures:
            i.update()

        for i in self.chunk_list:
            for j in i:
                j.update(self.tick_count % self.analysis['tick_interval'] == 0)

        self.creature_list = self.creature_list.union(self.new_born)
        self.alive_creatures = self.alive_creatures.union(self.new_born)
        self.alive_creatures = self.alive_creatures.difference(self.tick_dead)

    def _tick_creature_get(self, tick):
        """
        Gets the list of the creatures alive in a certain tick

        :param tick: the tick to search
        :type tick: int
        :return:
        """
        l = set()
        for i in self.creature_list:
            if i.birth_tick <= tick <= i.death_tick:
                l.add(i)
        return l

    def _analysis(self):
        """
        Analyses the different creatures genes and variables and prints it to the different files

        :return:
        """
        print(f"{self.name}: analysis setup")

        self._analysis_chunk_attrs()

        genes = dict()
        genes.update(var.CREATURES_GENES)
        genes.update(var.CREATURES_SECONDARY_GENES)

        for tick in range(0, self.lifetime, self.analysis['tick_interval']):
            alive = self._tick_creature_get(tick)

            for gene in genes:
                rec_type = genes[gene].REC_TYPE
                if rec_type == 'num':
                    self._analysis_num_gene(gene, alive, tick)

                elif rec_type == 'spr':
                    self._analysis_spr_gene(gene, tick)

            self._analysis_demographic_change(tick)
            self._analysis_demographic_spreading(tick)

    def _analysis_file_write(self, file_name, to_write, tick=None):
        """
        Writes to file_name the tick if present and then the items in to_write

        :param file_name: the name of the file to write to
        :type file_name: str
        :param to_write: the list of items to write to the file
        :type to_write: list
        :param tick: the tick to write
        :type tick: int
        :return:
        """
        try:
            file = open(os.path.join(self.directories['analysis'], file_name), 'r+')
            file.seek(0, 2)
        except FileNotFoundError:
            file = open(os.path.join(self.directories['analysis'], file_name), 'w')
        if tick is not None:
            out = str(tick) + var.FILE_SEPARATORS[0]
        else:
            out = str()
        for i in to_write:
            out += str(round(i, self.analysis['rounding'])) + var.FILE_SEPARATORS[0]
        file.write(out[:-1] + '\n')
        file.close()

    def _analysis_chunk_attrs(self):
        """
        Prints to the file the number of chunks per attribute class

        :return:
        """
        self.chunk_attrs_freq = dict()
        for attr in var.CHUNK_ATTRS:
            values = list()
            for chunk_row in self.chunk_list:
                for chunk in chunk_row:
                    values.append(chunk.__dict__[attr])
            parts = numpy.histogram(values, self.analysis['parts'], (0, self.chunks_vars[attr + '_max']))[0]
            self.chunk_attrs_freq[attr] = parts
            self._analysis_file_write(f"{attr}.csv", parts)

    def _analysis_num_gene(self, gene, alive, tick):
        """
        Prints to the file the different percentile values and the average

        :param gene: the gene to analyse
        :type gene: str
        :param alive: the list of alive creatures in tick
        :type alive: set
        :param tick: the tick considered
        :type tick: int
        :return:
        """
        values = list()
        for creature in alive:
            values.append(creature.genes[gene].phenotype)
        parts = list()
        for part in range(0, self.analysis['percentile_parts'] + 1):
            parts.append(scipy.percentile(values, part * 100 / self.analysis['percentile_parts']))
        parts.append(scipy.average(values))
        self._analysis_file_write(f"{gene}.csv", parts, tick)

    def _analysis_spr_gene(self, gene, tick):
        """
        Prints to the file the different spreading of creatures by their gene's phenotype

        :param gene: the gene to consider
        :type gene: str
        :param tick: the tick considered
        :type tick: int
        :return:
        """
        index = tick // self.analysis['tick_interval']
        gene_class = var.CREATURES_GENES[gene]
        attr = gene_class.REC_CHUNK_ATTR
        attr_max = self.chunks_vars[attr + '_max']
        classes = gene_class.REC_CLASSES
        values = [[0 for i in range(self.analysis['parts'])] for j in classes]
        for chunk_row in self.chunk_list:
            for chunk in chunk_row:
                chunk_index = int(chunk.__dict__[attr] * self.analysis['parts'] / attr_max)
                for creature in chunk.ticks_record[index]:
                    i = 0
                    for phens in classes:
                        if creature.genes[gene].phenotype in phens:
                            phen_index = i
                            break
                        i += 1
                    try:
                        values[phen_index][chunk_index] += 1
                    except IndexError:
                        if chunk_index == self.analysis['parts']:
                            values[phen_index][chunk_index - 1] += 1
                        else:
                            raise
        correct = [[0 for i in range(self.analysis['parts'])] for j in classes]
        for phen in range(len(classes)):
            for part in range(self.analysis['parts']):
                if not self.chunk_attrs_freq[attr][part] == 0:
                    correct[phen][part] = values[phen][part] / self.chunk_attrs_freq[attr][part]
                else:
                    correct[phen][part] = 0
            self._analysis_file_write(f"{gene}_{classes[phen][0]}.csv", values[phen] + correct[phen], tick)

    def _analysis_demographic_change(self, tick):
        """
        Prints to the file the number of births and deaths divided by cause

        :param tick: the tick considered
        :type tick: int
        :return:
        """
        deaths = {'s': 0, 't': 0, 'a': 0, 'e': 0}
        born = 0
        for creature in self.creature_list:
            if tick <= creature.birth_tick < tick + self.analysis['tick_interval']:
                born += 1
            if tick <= creature.death_tick < tick + self.analysis['tick_interval']:
                deaths[creature.death_cause] += 1
        self._analysis_file_write("population.csv", [born, deaths['s'], deaths['t'], deaths['a']], tick)

    def _analysis_demographic_spreading(self, tick):
        index = tick // self.analysis['tick_interval']
        attr = 'foodmax'
        attr_max = self.chunks_vars['foodmax_max']
        values = [0 for i in range(self.analysis['parts'])]
        for chunk_row in self.chunk_list:
            for chunk in chunk_row:
                chunk_index = int(chunk.__dict__[attr] * self.analysis['parts'] / attr_max)
                try:
                    values[chunk_index] += len(chunk.ticks_record[index])
                except IndexError:
                    if chunk_index == self.analysis['parts']:
                        values[chunk_index - 1] += len(chunk.ticks_record[index])
                    else:
                        raise
        correct = [0 for i in range(self.analysis['parts'])]
        for part in range(self.analysis['parts']):
            if not self.chunk_attrs_freq[attr][part] == 0:
                correct[part] = values[part] / self.chunk_attrs_freq[attr][part]
            else:
                correct[part] = 0
        self._analysis_file_write("demographic_spreading.csv", values + correct, tick)
