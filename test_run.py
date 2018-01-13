from modules.world import World
from modules import var

i = 0
while True:
    try:
        name = "test" + str(i)
        lol = var.DFEAULT_SIM_VARIABLES
        world = World(name, lol)
        world.run()
    except Exception as e:
        raise
        print(e)
        i -= 1
    print('\n------------------\n')
    i += 1
