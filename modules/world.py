import os
import shutil
import time
from random import random as rnd

import numpy
import scipy

from . import genes as gns
from . import utility as utl
from . import var
from .chunk import Chunk
from .creature import Herbivore, Carnivore


class World(object):
    """class of the world where creatures live"""

    def __init__(self, name, sim_variables, progress_queues=None, termination_event=None):
        """
        Creates new simulation

        :param name: name of the simulation
        :type name: str
        :param sim_variables: paramaters of the simulation
        :type sim_variables: dict
        :return:
        """
        self.name = name
        self.prgr_que = progress_queues
        self._progress_update('status', 'Simulation setup')
        self.thr_termination = termination_event
        self.path = os.path.join(var.SIMULATIONS_PATH, name)
        self.directories = dict()
        self.__dict__.update(sim_variables)
        self.tick_count = 0
        self.ID_count = 0
        # self.noises = {'foodmax': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700),
        #               'temperature': SimplexNoise(num_octaves=6, persistence=0.1, dimensions=2, noise_scale=700)}
        self.creature_list = set()
        self.alive_creatures = set()
        self.tick_dead = set()
        self.new_born = set()
        self._directory_setup()

        with open(os.path.join(var.MAPS_PATH, self.map_name, f"params.{var.FILE_EXTENSIONS['map_data']}"), 'r') as map_file:
            map_params = map_file.readline()
            self.__dict__.update(utl.get_from_string(map_params, var.TO_RECORD['map']))

            self.coords_limits = (self.dimension['width'], self.dimension['height'])
            self.chunk_list = [[None for x in range(self.dimension['height'])] for y in
                               range(self.dimension['width'])]

            self.tot_chunks = self.dimension['width'] * self.dimension['height']
            chunk = 0
            for line in map_file.readlines():
                ch_params = utl.get_from_string(line, var.TO_RECORD['map_chunk'])
                self.chunk_list[ch_params['x']][ch_params['y']] = Chunk(self, **ch_params)
                chunk += 1
                self._progress_update('details', ('creating chunks', (chunk, self.tot_chunks)))
                self._progress_update('percent', chunk / self.tot_chunks)

        tot_carnivores = self.initial_creatures['carnivores']
        for j in range(tot_carnivores):
            Carnivore(*self._creature_randomization())
            self._progress_update('details', ('creating carnivores', (j, tot_carnivores)))
            self._progress_update('percent', j / tot_carnivores)

        tot_herbivores = self.initial_creatures['herbivores']
        for j in range(tot_herbivores):
            Herbivore(*self._creature_randomization())
            self._progress_update('details', ('creating herbivores', (j, tot_herbivores)))
            self._progress_update('percent', j / tot_herbivores)

        for i in self.chunk_list:
            for j in i:
                j.tick_record()

        self.creature_list = self.new_born
        self.alive_creatures = self.new_born
        self.run()

    def run(self):
        """
        Calls update() one time per tick in lifetime

        :return:
        """
        self._progress_update('status', 'Simulation running...')
        self.start_time = time.time()
        for i in range(self.max_lifetime):
            self._update()
            if len(self.alive_creatures) == 0:
                break
        self.lifetime = self.tick_count
        self._progress_update('status', 'Simulation ended')
        self._progress_update('eta', None)
        self._end()
        self._progress_update('status', 'Simulation analysis')
        self._analysis()
        self._progress_update('status', 'Drawing backgrounds')
        self._copy_backgrounds()
        self._progress_update('status', 'Cleaning up and terminating')
        self._finalize()
        self._progress_update('status', 'Finished')
        self._progress_update('details', tuple())
        self._progress_update('percent', None)

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
            self.directories[i] = self._create_directory(self.path, i, var.DIRECTORIES)

    def _create_directory(self, path, name, dir_dict):
        new_directory = os.path.join(path, name)
        os.makedirs(new_directory)
        sub_dir = dir_dict[name]
        for dir in sub_dir:
            self._create_directory(new_directory, dir, sub_dir)
        return new_directory

    def _end(self):
        """
        Kills all creatures and chunks at the end of the simulation

        :return:
        """
        with open(os.path.join(self.directories['data'], f"chunks.{var.FILE_EXTENSIONS['chunks_data']}"), 'w') as file:
            count = 0
            for i in self.chunk_list:
                for j in i:
                    j.end(file)
                    count += 1
                    self._progress_update('details', ('saving chunks data', (count, self.tot_chunks)))
                    self._progress_update('percent', count / self.tot_chunks)
        tot_creatures = len(self.alive_creatures)
        count = 0
        for i in self.alive_creatures:
            i.death()
            count += 1
            self._progress_update('details', ('killing alive creatures', (count, tot_creatures)))
            self._progress_update('percent', count / tot_creatures)
        with open(os.path.join(self.directories['data'], f"creatures.{var.FILE_EXTENSIONS['creatures_data']}"), 'w') as file:
            tot_creatures = len(self.creature_list)
            count = 0
            for i in self.creature_list:
                i.end(file)
                count += 1
                self._progress_update('details', ('saving creatures data', (count, tot_creatures)))
                self._progress_update('percent', count / tot_creatures)

    def _finalize(self):
        """
        Deletes all creatures and chunks objects, saves simulation files and deletes the simulation object

        :return:
        """

        tot_creatures = len(self.creature_list)
        count = 0
        for i in self.creature_list:
            del i
            count += 1
            self._progress_update('details', ('deleting creatures', (count, tot_creatures)))
            self._progress_update('percent', count / tot_creatures)

        count = 0
        for i in self.chunk_list:
            for j in i:
                del j
            count += 1
            self._progress_update('details', ('deleting creatures', (count, self.tot_chunks)))
            self._progress_update('percent', count / self.tot_chunks)

        self._progress_update('details', ('saving simulation data',))
        to_write = str()
        for i in var.TO_RECORD['simulation']:
            to_write += utl.add_to_write(self.__dict__[i], self.analysis['rounding'])
        with open(os.path.join(self.path, f"params.{var.FILE_EXTENSIONS['simulation_data']}"), 'w') as file:
            try:
                file.write(to_write[:-1])
            except ValueError:
                pass

    def _creature_randomization(self):
        """
        Creates a tuple with random characteristics of a creatures

        :return: tuple
        """
        coord = [0, 0]
        for i in range(2):
            coord[i] = rnd() * self.coords_limits[i] * self.chunk_dim
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

        tick_to_record = self.tick_count % self.analysis['tick_interval'] == 0
        for i in self.chunk_list:
            for j in i:
                j.update(tick_to_record)

        self.creature_list = self.creature_list.union(self.new_born)
        self.alive_creatures = self.alive_creatures.union(self.new_born)
        self.alive_creatures = self.alive_creatures.difference(self.tick_dead)
        self._progress_update('details', (f'tick # {self.tick_count}  -  alive: {len(self.alive_creatures)}',))
        self._progress_update('percent', self.tick_count / self.max_lifetime)
        self._progress_update('eta', (time.time() - self.start_time) / self.tick_count * (self.max_lifetime - self.tick_count))

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

        self._progress_update('details', ('analysing chunk attributes',))

        self._analysis_chunk_attrs()

        genes = dict()
        genes.update(var.CREATURES_GENES)
        genes.update(var.CREATURES_SECONDARY_GENES)

        for tick in range(0, self.lifetime, self.analysis['tick_interval']):
            self._progress_update('details', ('analysing tick #', (tick, self.lifetime)))
            self._progress_update('percent', tick / self.lifetime)
            alive = self._tick_creature_get(tick)

            for gene in genes:
                rec_type = genes[gene].REC_TYPE
                if rec_type == 'num':
                    self._analysis_num_gene(gene, alive, tick)

                elif rec_type == 'spr':
                    self._analysis_spr_gene(gene, tick)

            self._analysis_demographic_change(tick)
            self._analysis_demographic_spreading(tick)

    def _analysis_file_write(self, file_name, file_type, to_write, tick=None, attr=None):
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
        file_name = file_name + '.' + var.FILE_EXTENSIONS[file_type]
        try:
            file = open(os.path.join(self.directories['analysis'], file_name), 'r+')
            file.seek(0, 2)
        except FileNotFoundError:
            file = open(os.path.join(self.directories['analysis'], file_name), 'w')
            if attr is not None:
                file.write(attr + '\n')
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
            parts = numpy.histogram(values, self.analysis['parts'], (0, self.map_maxes[attr]))[0]
            self.chunk_attrs_freq[attr] = parts
            self._analysis_file_write(attr, 'chunks_attribute', parts)

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
        self._analysis_file_write(gene, 'numeric_analysis', parts, tick)

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
        attr_max = self.map_maxes[attr]
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
            self._analysis_file_write(gene + '_' + classes[phen][0], 'spreading_analysis', values[phen] + correct[phen], tick, attr)

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
        self._analysis_file_write('demographic_change', 'demographic_analysis', [born, deaths['s'], deaths['t'], deaths['a']], tick)

    def _analysis_demographic_spreading(self, tick):
        index = tick // self.analysis['tick_interval']
        attr = 'foodmax'
        attr_max = self.map_maxes['foodmax']
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
        self._analysis_file_write("demographic_spreading", 'spreading_analysis', values + correct, tick, attr)
        total = 0
        for i in values:
            total += i
        self._analysis_file_write("population", 'population_analysis', (total,), tick)

    def _copy_backgrounds(self):
        for attr in var.CHUNK_ATTRS:
            map_path = os.path.join(var.MAPS_PATH, self.map_name, f"{attr}.gif")
            path = os.path.join(self.directories['images'], f"{attr}_background.gif")
            shutil.copyfile(map_path, path)

    def _progress_update(self, type, msg):
        self._termination_control()
        if self.prgr_que:
            self.prgr_que[type].put(msg)
        else:
            if type == 'status':
                print(f"{self.name} - {type}: {msg} ")

    def _termination_control(self):
        try:
            if self.thr_termination[0].is_set():
                shutil.rmtree(self.path)
                self.thr_termination[1].set()
                exit()
        except AttributeError:
            pass
        except TypeError:
            pass
