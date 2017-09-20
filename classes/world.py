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
        self.chunk_list = [[0 for x in range(0, self.height, self.chunk_dim)] for y in range(0, self.width, self.chunk_dim)]  # viene riempita una matrice di 0
        self.creature_list = set()
        self.alive_creatures = set()
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
            shutil.rmtree(self.path)
            os.makedirs(self.path)
            '''if "y" == input(f"Simulation \"{self.name}\" already exists. Overwrite it? y/n"):
                shutil.rmtree(self.path)
                os.makedirs(self.path)
            else:
                exit()'''
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
        x = rnd() * self.width
        y = rnd() * self.height
        energy = 50 + rnd() * 100
        sex = int(rnd() * 2)
        lims = self.creatures_vars['genes_lim']
        temp_resist = "Nlc"
        genes = {'temp_resist_gen': temp_resist[int(rnd() * 3)] + temp_resist[int(rnd() * 3)]}
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
        for i in self.alive_creatures:
            i.update()  # viene aggiornata ogni creatura
        for i in self.new_born:
            i.update()
        self.creature_list = self.creature_list | self.new_born
        self.alive_creatures = self.alive_creatures | self.new_born
        self.alive_creatures -= self.tick_dead

    def get_ID(self):
        self.ID_count += 1
        return self.ID_count

    def tick_creature_list(self, tick, attr=None):
        L = list()
        for i in self.creature_list:
            if i.birth_tick <= tick and i.death_tick >= tick:
                if attr:
                    L.append(i.genes[attr])
                    return sorted(L)
                else:
                    L.append(i)
                return L

    def analysis(self):
        print(f"{self.name}: analysis setup")

        # analisi caratteristiche
        print(f"{self.name}: genes analysis")
        names = ["agility", "bigness", "fertility", "speed", "eat_coeff", "num_control_gene"]

        for k in names:
            f = open(os.path.join(self.path, f"{k}.csv"), 'w')
            for i in range(0, self.lifetime, vars.TIME_INTERVAL):
                l = self.tick_creature_list(i, k)
                to_write = str(i)
                for j in range(0, vars.PERCENTILE_PARTS + 1):
                    to_write += vars.FILE_SEPARATOR + str(l[round((j / vars.PERCENTILE_PARTS) * (len(l) - 1))])
                to_write += vars.FILE_SEPARATOR + str(sum(l) / float(len(l))) + '\n'
                f.write(to_write)
            f.close()

        f = open(os.path.join(self.path, f"population.csv"), 'w')
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
            f.write(str(i) + vars.FILE_SEPARATOR + str(born) + vars.FILE_SEPARATOR + str(deaths[0]) + vars.FILE_SEPARATOR + str(deaths[1]) + vars.FILE_SEPARATOR + str(deaths[2]) + '\n')
        f.close()

        names = ['foodmax', 'temperature']
        chunks_f_t = dict()
        for k in names:
            f = open(os.path.join(self.path, f"{k}.csv"), 'w')
            parts = [0 for x in range(vars.PARTS)]
            for i in self.chunk_list:
                for j in i:
                    val = min(j.__dict__[k], self.chunks_vars[k + '_max'] - 1)
                parts[int((val * vars.PARTS) / (self.chunks_vars[k + '_max']))] += 1
            string = str()
            for i in range(0, 8):
                string += str(parts[i]) + vars.FILE_SEPARATOR
            chunks_f_t[k] = parts
            f.write(string[:-1] + '\n')
            f.close()

            # analisi disposizione
        print(f"{self.name}: spreading and deaths analysis")
        names = vars.TEMPERATURE_FOOD_PARTS
        f = dict()
        s = dict()
        for j in names:
            f[j] = dict()
            s[j] = list()
            for i in names[j]:
                f[j][i] = open(os.path.join(self.path, f"temperature_{i}.csv"), 'w')
                s[j].append(str())
        for i in range(0, self.lifetime, 100):
            l = self.tick_creature_list(i)
            data = dict()
            for w in ['temperature', 'foodmax']:
                data[w] = dict()
                for k in ['raw', 'correct']:
                    data[w][k] = [[0 for x in range(vars.PARTS)] for y in range(vars.TEMPERATURE_FOOD_PARTS[w])]
                for j in l:
                    birth = max(j.birth_tick, 1)
                    coord = (j.tick_history[i - birth][0], j.tick_history[i - birth][1])
                    chunk_coord = (int(coord[0] / self.chunk_dim), int(coord[1] / self.chunk_dim))
                    val = min(self.chunk_list[chunk_coord[0]][chunk_coord[1]].__dict__[w], self.chunks_vars[w + '_max'] - 1)
                    data[w]['raw'][utl.data_number(w, j)][int((val * vars.PARTS) // (self.chunks_vars[w + '_max']))] += 1

                x = 0
                for k in vars.TEMPERATURE_FOOD_PARTS[w]:
                    s[w][x] = str(i)
                    for j in range(vars.PARTS):
                        data[w]['correct'][x][j] = data[w]['raw'][x][j] / chunks_f_t[w][j] * vars.ADJ_COEFF
                        s[w][x] += vars.FILE_SEPARATOR + data[w]['raw'][x][j] + vars.FILE_SEPARATOR + data[w]['correct'][x][j]
                    f[w][k].write(s[w][x])
                    f[w][k].close()
                    x += 1

        '''os.chdir(self.path)
        for name in ["TempFrames", "FoodMaxFrames"]:
            try:
                os.makedirs(name)
            except FileExistsError:
                shutil.rmtree(name)
                os.makedirs(name)

        for tick in range(0, lifetime, 100):
            imageFood = PIL.Image.new("RGB", (width, height))
            drawFood = PIL.ImageDraw.Draw(imageFood)
            imageTemp = PIL.Image.new("RGB", (width, height))
            drawTemp = PIL.ImageDraw.Draw(imageTemp)

            for i in range(len(datiChunk)):
                for j in range(len(datiChunk[i])):
                    drawFood.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(0, int(datiChunk[i][j][0]), 0), outline="black")

            for i in tick_creature_list(tick):
                birth = max(i[1], 1)
                coord = (i[14][tick - birth][0], i[14][tick - birth][1])
                energy = i[14][tick - birth][2]
                drawFood.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 0, 0), outline="black")

            for i in range(len(datiChunk)):
                for j in range(len(datiChunk[i])):
                    temperature = datiChunk[i][j][2]
                    if temperature > 0:
                        drawTemp.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(255, int(255 - (temperature / 100 * 255)), int(255 - (temperature / 100 * 255))), outline="black")
                    else:
                        drawTemp.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(int(255 + (temperature / 100 * 255)), int(255 + (temperature / 100 * 255)), 255), outline="black")

            for i in tick_creature_list(tick):
                birth = max(i[1], 1)
                coord = (i[14][tick - birth][0], i[14][tick - birth][1])
                energy = i[14][tick - birth][2]
                x = i[8]
                if x == "N" or x == "n":
                    drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 255, 255), outline="black")

                elif x == "l":
                    drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(0, 0, 255), outline="black")

                elif x == "c":
                    drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 0, 0), outline="black")
            imageFood.save(f"FoodMaxFrames/FrameF{tick}.jpg", "JPEG")
            imageTemp.save(f"TempFrames/FrameT{tick}.jpg", "JPEG")
            del imageTemp, imageFood, drawFood, drawTemp
        os.chdir("..")'''
