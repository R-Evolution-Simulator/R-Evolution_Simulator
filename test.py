from modules.world import World
from modules import var

lol = var.DFEAULT_SIM_VARIABLES
world = World('test3', lol)
world.run()
del (world)
