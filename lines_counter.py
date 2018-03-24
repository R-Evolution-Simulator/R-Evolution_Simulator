import os

tot = 0
for i in os.listdir(os.path.join(os.getcwd(), 'modules')):
    print(i, end=' - ')
    lines = 0
    try:
        f = open(os.path.join(os.getcwd(), 'modules', i))
    except IsADirectoryError:
        pass
    else:
        lines = len(f.readlines())
        tot += lines
    print(lines)
print(tot)
