import os
import shutil
from random import random as rnd

from .noise.simplexnoise.noise import SimplexNoise
from .chunk import Chunk
from .creature import Creature
from . import vars
from . import utility as utl


class World:
    """class of the world where creatures live"""
    TO_RECORD = vars.TO_RECORD['simulation']

    def __init__(self, name, sim_variables):
        print(f"{name}: simulation setup")
        self.name = name
        self.path = os.path.join(vars.SIMULATIONS_PATH, name)
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
        self.directory_setup()

        print(f"        - creating chunks")
        for i in range(len(self.chunk_list)):  # quindi ogni 0 e' sostituito con un Chunk
            for j in range(len(self.chunk_list[0])):
                self.chunk_list[i][j] = Chunk(self, (i, j))

        print(f"        - creating creatures")
        for i in range(self.initial_creatures):
            Creature(*self.creature_randomization())

        self.creature_list = self.new_born
        self.alive_creatures = self.new_born
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
        self.files['chunk_data'] = open(os.path.join(self.path, "chunkData.csv"), 'w')

    def death(self):
        for i in self.chunk_list:
            for j in i:
                j.death()
        for i in self.creature_list:
            i.death()

    def __del__(self):

        # closing simulation and files

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
        to_write = str()
        for i in self.TO_RECORD:
            to_write += utl.add_to_write(self.__dict__[i], vars.ROUNDINGS['simulation'])
        try:
            self.files['simulation_data'].write(to_write[:-1])
        except ValueError:
            pass
        print(f"        - closing files")
        for i in self.files:
            self.files[i].close()
        print(f"{self.name}: simulation ended")

    def creature_randomization(self):
        """
        function which returns a tuple with creature's characteristics
        """
        # calcolo delle caratteristiche della nuova creatura (random)
        coord = [0, 0]
        for i in range(2):
            coord[i] = rnd() * self.dimension[i] * self.chunk_dim
        energy = 50 + rnd() * 100
        sex = int(rnd() * 2)
        lims = self.creatures_vars['genes_lim']
        temp_resist = "Nlc"
        genes = {'temp_resist_gen': temp_resist[int(rnd() * 3)] + temp_resist[int(rnd() * 3)]}
        for i in lims:
            genes[i] = rnd() * (lims[i][1] - lims[i][0])

        # creazione della creatura con le caratteristiche calcolate
        return (self, coord, (0, 0), energy, sex, genes, int(rnd() * (self.creatures_vars['average_age'] / 2)))

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
        self.death()
        self.analysis()

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

    def get_ID(self):
        self.ID_count += 1
        return self.ID_count

    def tick_creature_list(self, tick, gene=None):
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

    def analysis(self):
        print(f"{self.name}: analysis setup")

        # analisi caratteristiche
        print(f"{self.name}: genes analysis")

        for k in vars.NUM_GENES_LIST:
            self.files[k] = open(os.path.join(self.path, f"{k}.csv"), 'w')
            for i in range(0, self.lifetime, vars.TIME_INTERVAL):
                l = self.tick_creature_list(i, k)
                to_write = str(i)
                for j in range(0, vars.PERCENTILE_PARTS + 1):
                    to_write += vars.FILE_SEPARATOR + str(l[round((j / vars.PERCENTILE_PARTS) * (len(l) - 1))])
                to_write += vars.FILE_SEPARATOR + str(sum(l) / float(len(l))) + '\n'
                self.files[k].write(to_write)

        self.files['population'] = open(os.path.join(self.path, f"population.csv"), 'w')
        for i in range(0, self.lifetime, vars.TIME_INTERVAL):
            deaths = [0, 0, 0]
            born = 0
            for j in self.creature_list:
                if j.birth_tick >= i and j.birth_tick < i + vars.TIME_INTERVAL:
                    born += 1
                if j.death_tick >= i and j.death_tick < i + vars.TIME_INTERVAL:
                    if j.death_cause == "s":
                        deaths[0] += 1
                    elif j.death_cause == "t":
                        deaths[1] += 1
                    elif j.death_cause == "a":
                        deaths[2] += 1
            self.files['population'].write(str(i) + vars.FILE_SEPARATOR + str(born) + vars.FILE_SEPARATOR + str(
                deaths[0]) + vars.FILE_SEPARATOR + str(deaths[1]) + vars.FILE_SEPARATOR + str(deaths[2]) + '\n')

        chunk_attrs_spread = dict()
        for k in vars.CHUNK_ATTRS:
            self.files[k] = open(os.path.join(self.path, f"{k}.csv"), 'w')
            parts = [0 for x in range(vars.PARTS)]
            for i in self.chunk_list:
                for j in i:
                    val = min(j.__dict__[k], self.chunks_vars[k + '_max'] - 1)
                parts[int((val * vars.PARTS) / (self.chunks_vars[k + '_max']))] += 1
            string = str()
            for i in range(0, 8):
                string += str(parts[i]) + vars.FILE_SEPARATOR
            chunk_attrs_spread[k] = parts
            self.files[k].write(string[:-1] + '\n')

            # analisi disposizione
        print(f"{self.name}: spreading and deaths analysis")
        files = dict()
        strings = dict()
        for j in vars.CHUNK_ATTRS_PARTS:
            files[j] = list()
            strings[j] = list()
            for i in range(vars.CHUNK_ATTRS_PARTS[j]):
                files[j].append(open(os.path.join(self.path, f"{j}_{i}.csv"), 'w'))
                strings[j].append(str())
        for i in range(0, self.lifetime, 100):
            l = self.tick_creature_list(i)
            data = dict()
            for w in vars.CHUNK_ATTRS:
                data[w] = dict()
                for k in ['raw', 'correct']:
                    data[w][k] = [[0 for x in range(vars.PARTS)] for y in range(vars.CHUNK_ATTRS_PARTS[w])]
                for j in l:
                    birth = max(j.birth_tick, 0)
                    coord = (j.tick_history[i - birth][0], j.tick_history[i - birth][1])
                    chunk_coord = (int(coord[0] / self.chunk_dim), int(coord[1] / self.chunk_dim))
                    print(chunk_coord)
                    val = min(self.chunk_list[chunk_coord[0]][chunk_coord[1]].__dict__[w], self.chunks_vars[w + '_max'] - 1)
                    data[w]['raw'][utl.data_number(w, j)][
                        int((val * vars.PARTS) // (self.chunks_vars[w + '_max']))] += 1

                x = 0
                for k in range(vars.CHUNK_ATTRS_PARTS[w]):
                    strings[w][x] = str(i)
                    for j in range(vars.PARTS):
                        if chunk_attrs_spread[w][j] == 0:
                            data[w]['correct'][x][j] = 0
                        else:
                            data[w]['correct'][x][j] = data[w]['raw'][x][j] / chunk_attrs_spread[w][j] * vars.ADJ_COEFF
                        strings[w][x] += vars.FILE_SEPARATOR + str(data[w]['raw'][x][j]) + vars.FILE_SEPARATOR + str(
                            data[w]['correct'][x][j])
                    files[w][k] = open(os.path.join(self.path, f"{j}_{i}.csv"), 'w')
                    files[w][k].write(strings[w][x])
                    self.files[w + '_' + str(k)] = files[w][k]
                    x += 1
