from classes.analysis import analysis
from classes.world import World

name = "test_simulation"
world = World(name, width=400, height=300, initialCreatures=100, lifetime=1000)
world.run()
analysis(name)
