from noise.simplexnoise.noise import normalize


class Chunk:
    '''classe dei chunk ( unita' del territorio )'''

    def __init__(self, world, x, y):
        '''costruttore dei chunk'''
        self.coord = [x, y]

        # cibo
        self.world = world
        self.foodMax = normalize(self.world.ch_foodMaxNoise.noise(x, y)) * self.world.ch_foodMaxMax  # l'erba massima in un territorio e' compresa tra 0 e max ed e' fissa
        self.food = self.foodMax / 2  # all'inizio il cibo e' al massimo
        self.growthRate = self.foodMax * self.world.ch_growthCoeff  # la crescita e' direttamente proporzionale all'erba massima

        # temperatura
        self.temperature = (normalize(self.world.ch_temperatureNoise.noise(x, y)) - 0.5) * self.world.ch_temperatureMax * 2  # la temperatura in un territorio e' compresa tra -max e max ed e' fissa
        self.foodHistory = ""
        self.chunkCreatureList = []

    def update(self):
        '''metodo di update dei chunk'''
        self.food *= (1 + self.growthRate)  # ad ogni ciclo l'erba cresce
        if self.food > self.foodMax:  # finche' non raggiunge il massimo
            self.food = self.foodMax

        self.foodHistory += f"{int(self.food)},"

    def __del__(self):
        try:
            self.world.chunkData.write(f"{self.coord[0]};{self.coord[1]};{self.foodMax};{self.growthRate};{self.temperature};{self.foodHistory[:-1]}\n")
        except ValueError:
            pass
