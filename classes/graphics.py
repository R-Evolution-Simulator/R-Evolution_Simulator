from . import windows as wndw


class Graphics(object):
    def __init__(self):
        self.main_window = wndw.LoadWindow(self)

    def run(self):
        self.main_window.mainloop()
