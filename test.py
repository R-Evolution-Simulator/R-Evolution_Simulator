from modules.world import World
import os
import shutil
from modules import var
import json

f = open(os.path.join(var.TEMPLATES_PATH, 'default.rsst'))
variables = json.loads(f.readline())
sims = os.listdir(var.SIMULATIONS_PATH)
i = 1
while True:
    name = f's_{i}'
    if name not in sims:
        print(name)
        try:
            new = World(name, variables)
        except KeyboardInterrupt:
            shutil.rmtree(os.path.join(var.SIMULATIONS_PATH, name))
            exit()
        except Exception as e:
            print(f"ERROR {name}:   {e}")
            i -= 1
    i += 1
