"""
    Just some pointless lines that print the code in files "world.py", "creature.py", "chunk.py", "analysis.py", "graphics.py"
"""

from time import *

name = ["world", "creature", "chunk", "analysis", "graphics"]

lines = {}
for a in name:
    f = open(f"classes/{a}.py")
    lines[a] = f.readlines()
while True:
    for a in name:
        print(f"----- file: {a}.py -----")
        for line in lines[a]:
            print(line, end='')
            sleep(0.05)
