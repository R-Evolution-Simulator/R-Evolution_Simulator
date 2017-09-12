from .classes.analysis import analysis
from .classes.world import World

try:
    name = "big_long_simulation_noise"
    world = World(name, width=1200, height=900, initialCreatures=3000)
    world.run()
    analysis(name)
except Exception as ex:
    print(f"ERROR {name}: {ex}")
