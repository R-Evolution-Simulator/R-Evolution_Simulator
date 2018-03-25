"""
Just some pointless lines that print the code in files
"""

from time import *
import os


def print_and_wait(str):
    print(str)
    sleep(0.1)


modules = os.listdir(os.path.join(os.getcwd(), 'modules'))
lines = dict()
for a in modules:
    try:
        f = open(os.path.join(os.getcwd(), 'modules', a))
    except IsADirectoryError:
        pass
    else:
        lines[a] = f.readlines()
while True:
    for a in lines:
        for i in ('', '', '', '', f"----- file: {a} -----", '', ''):
            print_and_wait(i)
        for line in lines[a]:
            print_and_wait(line[:-1])
