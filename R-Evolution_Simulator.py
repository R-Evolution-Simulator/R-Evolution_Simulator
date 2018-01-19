from modules.main import Main

a = Main()
try:
    a.run()
except Exception as e:
    print(e)
    exit(34)
