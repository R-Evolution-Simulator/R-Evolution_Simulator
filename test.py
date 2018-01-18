from modules.world import World
from modules import var
import queue as que

queues = dict()
for key in ['status', 'details', 'percent', 'eta']:
    queues[key] = que.Queue(1)

lol = var.DEFAULT_SIM_VARIABLES
lol['max_lifetime'] = 10000
lol['analysis']['percentile_parts'] = 8
lol['analysis']['parts'] = 8

world = World('test', lol, progress_queues=queues)

