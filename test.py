from modules.world import World
from modules import var

lol = var.DFEAULT_SIM_VARIABLES
lol['max_lifetime'] = 500
world = World('test4', lol)
world.run()
del (world)
