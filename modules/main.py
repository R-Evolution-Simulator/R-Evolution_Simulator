from . import windows as wndw


class Main(object):
    def __init__(self):
        self.windows = [wndw.MainMenuWindow(self), ]

    def run(self):
        while True:
            self.windows[0].update()