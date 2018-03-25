from modules.world import World
import os
from modules import var
import json

f=open(os.path.join(var.TEMPLATES_PATH, 'default.rsst'))
variables=json.loads(f.readline())
for i in range(10,21):
    new=World(f's_{i}', variables)