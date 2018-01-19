from modules.main import Main

a = Main()
try:
    a.run()
except Exception:
    print('error')
    exit(123456)
