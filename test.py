from modules.world import World
from modules import var

lol = var.DFEAULT_SIM_VARIABLES
lol['max_lifetime'] = 10000
lol['analysis']['percentile_parts'] = 8
lol['analysis']['parts'] = 8
lol['dimension'] = (60,45)
lol['initial_creatures'] = 300
world = World('test_rnd', lol)
world.run()
del (world)

