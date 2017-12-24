from classes.world import World
from classes import var

name = "test"
lol = var.DFEAULT_SIM_VARIABLES
lol['dimension'] = (50, 30)
lol['initial_creatures'] = 500
lol['max_lifetime'] = 1000
world = World(name, lol)
world.run()
