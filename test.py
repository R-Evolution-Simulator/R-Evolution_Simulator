from modules.windows import SimReplayControlWindow


class Main(object):
    def __init__(self):
        self.windows = [SimReplayControlWindow(self, 'test'), ]

    def run(self):
        try:
            while True:
                self.windows[0].update()
        except IndexError:
            pass


a = Main()
a.run()
