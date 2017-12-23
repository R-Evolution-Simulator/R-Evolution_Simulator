from classes.world import World
from classes import var

name = "test"
lol = var.DFEAULT_SIM_VARIABLES
lol['dimension'] = (20, 15)
lol['initial_creatures'] = 100
lol['max_lifetime'] = 500
world = World(name, lol)
world.run()
