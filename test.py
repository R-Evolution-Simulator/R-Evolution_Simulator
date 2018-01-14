from modules.world import World
from modules import var

lol = var.DFEAULT_SIM_VARIABLES
lol['max_lifetime'] = 5000
lol['analysis']['percentile_parts'] = 8
lol['analysis']['parts'] = 8
world = World('test', lol)
world.run()
del (world)
