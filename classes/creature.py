import math
import random
from random import random as rnd


# from .world import World


class Creature:
    '''classe degli organismi'''

    def __init__(self, world, x, y, parentsID, energy, tempResistGen, agility, bigness, sex, fertility, numControlGene, startCount=0):
        '''costruttore degli organismi'''
        self.world = world
        self.ID = self.world.cr_creaturesIDCount
        self.coord = [x, y]  # definite le coord iniziali dell'orgsnismo
        self.parentsID = parentsID
        self.tickHistory = ""
        self.birthTick = self.world.tickCount - startCount  # registrato il tick di creazione dell'orgsnismo (startCount serve solo per la diversificazione nel setup iniziale)
        self.energy = energy  # definite l'energia iniziale dell'orgsnismo
        self.chunkIn().chunkCreatureList.append(self)  # aggiunto l'organismo alla lista degli organismi presenti nel chunk in cui si trova
        self.reprodReady = False  # settata la capacita' riproduttiva su falso
        self.deathDate = int(random.gauss(self.world.cr_averageAge, self.world.cr_deviationAgeProb))  # stabilita' l'eventuale eta' di morte per vcchiaiadell'organismo
        self.age = 0  # settata l'eta' a 0
        self.destChunk = [self.chunkCoord(0), self.chunkCoord(1)]

        # attribuiti i geni alla creatura
        self.tempResistGen = tempResistGen  # puo' essere N (normale), l (pelo lungo), c (pelo corto)
        self.agility = agility
        self.bigness = bigness
        self.sex = sex
        self.fertility = fertility
        self.reprodCountdown = fertility
        self.numControlGene = numControlGene

        # calcolo caratteristiche fenotipiche creatura
        self.tempResist = self.tempResistCalc(self.tempResistGen)
        self.speed = (self.agility / self.bigness) * 2
        self.eatCoeff = self.bigness * self.world.cr_eatCoeffMax

        self.world.cr_creaturesIDCount += 1

        self.world.newBorn.add(self)  # organismo aggiunto alla lista degli organismi
        # print(world, x, y, energy, tempResistGen, agility, bigness, sex, fertility, birthFrame, startCount)

    def __del__(self, cause="e"):
        self.deathTick = self.world.tickCount
        self.deathCause = cause
        try:
            self.world.creaturesData.write(
                f"{self.ID};{self.birthTick};{self.parentsID[0]},{self.parentsID[1]};{self.tempResistGen};{self.agility};{self.bigness};{self.sex};{self.fertility};{self.tempResist};{self.speed};{self.eatCoeff};{self.numControlGene};{self.deathTick};{self.deathCause};{self.tickHistory[:-1]}\n")
        except ValueError:
            pass

    def update(self):
        '''metodo di update, AI degli organismi'''

        # controllo per la riproduzione
        if self.energy > 50 and self.reprodCountdown <= 0:
            self.reprodReady = True
            self.datingAgency()

        else:
            self.reprodReady = False
            self.reprodCountdown -= 1

        # calcolo e controllo movimento verso cibo
        self.destCalc()
        if not [self.chunkCoord(0),
                self.chunkCoord(1)] == self.destChunk:  # se non si trova gia' nella destinazione, si muove...
            self.step()

        else:  # ...altrimenti mangia
            self.eat()

        # update variabili della creatura
        self.energy -= self.world.cr_enDecCoeff * self.energy  # tolta energia al passare di ogni ciclo
        self.age += 1

        # controllo morte
        self.tickHistory += f"{round(self.coord[0],2)},{round(self.coord[1],2)},{int(self.energy)},{int(self.reprodReady)}/"
        self.deathControl()

    def chunkIn(self):
        """metodo che restituisce l'oggetto Chunk nel quale si trova la creatura"""
        return self.world.chunkList[self.chunkCoord(0)][self.chunkCoord(1)]

    def deathControl(self):
        '''metodo di controllo delle condizioni di morte dell'organismo'''
        if self.energy < 10:  # morte di fame
            self.world.tickDead.add(self)
            self.__del__("s")

        elif rnd() <= self.deathProbTemp():  # morte per temperatura
            self.world.tickDead.add(self)
            self.__del__("t")

        elif self.age >= self.deathDate:  # morte di vecchiaia
            self.world.tickDead.add(self)
            self.__del__("a")

    def deathProbTemp(self):
        '''calcolo della probabilita' di morire per la temperatura'''
        t = self.world.ch_temperatureMax
        if self.tempResist == "c":
            return ((self.chunkIn().temperature ** 2 / (4 * (self.world.ch_temperatureMax ** 2))) - (self.chunkIn().temperature / (2 * self.world.ch_temperatureMax)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.tempResist == "l":
            return ((self.chunkIn().temperature ** 2 / (4 * (t ** 2))) + (self.chunkIn().temperature / (2 * t)) + (1 / 4)) / self.world.cr_tempDeathProbCoeff

        elif self.tempResist == "N" or self.tempResist == "n":
            return ((self.chunkIn().temperature ** 2) / (self.world.ch_temperatureMax ** 2)) / self.world.cr_tempDeathProbCoeff

    def destCalc(self):
        '''calcolo del chunk piu' conveniente agli animali'''

        x = self.chunkCoord(0)
        y = self.chunkCoord(1)
        maxEn = float("-inf")

        for i in range(max(x - self.world.cr_viewRay, 0), min(x + self.world.cr_viewRay + 1, int(
                        (self.world.width) / self.world.chunkDim))):  # si cicla all'interno del quadrato...
            for j in range(max(y - self.world.cr_viewRay, 0), min(y + self.world.cr_viewRay + 1, int(
                            (self.world.height) / self.world.chunkDim))):  # ...dei Chunk delimitati dal raggio di vista

                if self.world.chunkList[i][j].food * self.eatCoeff * self.world.cr_enIncCoeff - self.energyConsume(i,
                                                                                                                   j) > maxEn:  # se l'energia guadagnata in una certa zona meno quella spesa per andarci e' migliore:
                    maxEn = self.world.chunkList[i][
                                j].food * self.eatCoeff * self.world.cr_enIncCoeff - self.energyConsume(i, j)
                    self.destChunk = [i, j]  # si aggiorna la variabile destinazione in chunk

        self.destCoord = [(self.destChunk[0] + 0.5) * self.world.chunkDim, (
            self.destChunk[1] + 0.5) * self.world.chunkDim]  # e in pixel (che corrisponde al centro di un Chunk)

    def step(self):
        '''metodo che calcola la nuova posizione dopo uno spostamento ogni tick'''

        self.chunkIn().chunkCreatureList.remove(
            self)  # l?organismo si leva dalla lista degli organismi del chunk in cui e', ...

        self.coord[0] += (self.destCoord[0] - self.coord[0]) / math.sqrt((self.destCoord[0] - self.coord[0]) ** 2 + (
            self.destCoord[1] - self.coord[1]) ** 2) * self.speed  # ...calcola la nuova destinazione,...
        self.coord[1] += (self.destCoord[1] - self.coord[1]) / math.sqrt(
            (self.destCoord[0] - self.coord[0]) ** 2 + (self.destCoord[1] - self.coord[1]) ** 2) * self.speed

        self.chunkIn().chunkCreatureList.append(
            self)  # ... e si aggiunge alla nuova lista

    def eat(self):
        '''metodo che aggiorna la quantita' di cibo nel chunk e l'energia dell'organismo in un "boccone" dell'organismo'''
        foodEaten = self.chunkIn().food * self.eatCoeff
        self.energy += foodEaten * self.world.cr_enIncCoeff  # qui l'energia aumenta del cibo mangiato per il coefficiente di aumento dell'energia
        self.chunkIn().food -= foodEaten  # si diminuisce il cibo sul prato
        self.energy = min(self.energy, 100)  # l'energia viene limitata a 100

    def energyConsume(self, x, y):
        '''metodo che restituisce l'enrgia persa per raggiungere un chunk'''

        return (math.sqrt((x * self.world.chunkDim + 5 - self.coord[0]) ** 2 + (
            y * self.world.chunkDim + 5 - self.coord[1]) ** 2) / self.speed) * self.world.cr_enDecCoeff * self.energy

    def chunkCoord(self, i):
        '''converte le coordinate nel chunk che le contiene'''
        if i == 0:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.width / self.world.chunkDim) - 1)
        else:
            return min(int(self.coord[i] / self.world.chunkDim), int(self.world.height / self.world.chunkDim) - 1)

    def datingAgency(self):
        '''metodo con cui le creature controllano se nella lista del chunk ne sono presenti altre pronte alla riproduzione; se si', si riproducono'''

        for i in self.chunkIn().chunkCreatureList:  # cicla tra tutte le crature del chunk

            if i.reprodReady and i.sex != self.sex:  # controlla se sono pronte alla riproduzione

                self.reproduction(i)
                self.reprodReady = False
                i.reprodReady = False

    def reproduction(self, shelf):
        '''metodo della riproduzione delle creature: ne viene creata una nuova con le caratteristiche genetiche ereditate dai genitori'''

        # calcolo delle caratteristiche della nuova creatura
        x = (self.coord[0] + shelf.coord[0]) / 2  # calcolo della posizione x
        y = (self.coord[1] + shelf.coord[1]) / 2  # calcolo della posizione y
        energy = (self.energy + shelf.energy) / 2  # calcolo dell'energia
        tempResistGen = self.tempResistGen[int(rnd() * 2)] + shelf.tempResistGen[
            int(rnd() * 2)]  # calcolo della resistenza alla temperatura
        agility = (self.agility + shelf.agility) / 2 + random.gauss(0, self.world.cr_mutationCoeff)  # calcolo dell'agilita'
        bigness = (self.bigness + shelf.bigness) / 2 + random.gauss(0, self.world.cr_mutationCoeff)  # calcolo della grandezza
        sex = int(rnd() * 2)  # calcolo del sesso
        fertility = (self.fertility + shelf.fertility) / 2 + random.gauss(0, self.world.cr_mutationCoeff)  # calcolo della fertilita'
        numControlGene = (self.numControlGene + shelf.numControlGene) / 2 + random.gauss(0, self.world.cr_mutationCoeff)

        Creature(self.world, x, y, (self.ID, shelf.ID), energy, tempResistGen, agility, bigness, sex, fertility, numControlGene)  # generazione della nuova creature con le caratteristiche calcolate
        # Creature.tickBorn += 1  # aggiunto 1 ai nati nel tick

    '''def geneControl(self, v, vmin, vmax):
        metodo di controllo dei geni: devono rientrare entro i valori limite
        return max(vmin, min(vmax, v))'''

    def tempResistCalc(self, gen):
        '''calcolo dell'espressione fenotipica del gene della resistenza alla temperatura'''
        if gen[0] == "N" or gen[1] == "N":
            return "N"

        elif gen == "ll":
            return "l"

        elif gen == "cc":
            return "c"

        else:
            return "n"
