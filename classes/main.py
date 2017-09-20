import tkinter as tk
from . import windows as wndw
import threading as thr


class Main(object):
    def __init__(self):
        self.windows = [wndw.MainMenuWindow(self), ]

    def run(self):
        try:
            while True:
                self.windows[0].update()
        except IndexError:
            pass
