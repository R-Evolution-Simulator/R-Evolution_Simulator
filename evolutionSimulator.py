from classes.analysis import analysis
from classes.world import World
from classes import var

name = "test"
lol = var.DFEAULT_SIM_VARIABLES
lol['dimension'] = (20, 15)
lol['initial_creatures'] = 100
lol['lifetime'] = 500
world = World(name, lol)
world.run()
del(world)
