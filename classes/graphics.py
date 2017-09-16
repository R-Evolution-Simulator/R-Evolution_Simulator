import tkinter as tk
from . import windows as wndw
import threading as thr


class Graphics(object):
    def __init__(self):
        # self._tkinter_thread()
        '''a=tk.Tk()
        a.update()'''
        self.windows = [wndw.MainMenuWindow(self), ]
        '''d=tk.Button(a, text='ooo')
        d.pack()
        a.update()'''

    def _tkinter_thread(self):
        a = tk.Tk()
        self.tkinter = thr.Thread(target=tk.mainloop)
        self.tkinter.setDaemon(True)
        self.tkinter.start()

    def run(self):
        try:
            while True:
                self.windows[0].update()
        except IndexError:
            pass