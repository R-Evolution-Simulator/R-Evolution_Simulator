from modules.world import World
from modules import var

name = "test"
lol = var.DFEAULT_SIM_VARIABLES
lol['dimension'] = (60,45)
lol['initial_creatures'] = 400
lol['max_lifetime'] = 1000
world = World(name, lol)
world.run()
del(world)
