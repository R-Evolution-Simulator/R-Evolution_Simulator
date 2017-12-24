from modules.world import World
from modules import var

name = "test"
lol = var.DFEAULT_SIM_VARIABLES
world = World(name, lol)
world.run()
