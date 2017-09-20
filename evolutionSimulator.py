from classes.analysis import analysis
from classes.world import World
from classes import vars

name = "test"
lol = vars.DFEAULT_SIM_VARIABLES
lol['width'] = 400
lol['height'] = 300
lol['initial_creatures'] = 100
lol['lifetime'] = 100
world = World(name, lol)
world.run()
analysis(name)
