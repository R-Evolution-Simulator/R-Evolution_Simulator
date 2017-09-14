from . import windows as wndw
import tkinter as tk
import threading as thr


class Graphics(object):
    def __init__(self):
        # self._tkinter_thread()
        self.main_window = wndw.CanvasWindow(self)
        self.main_window.load_window_creation()

    def _tkinter_thread(self):
        a = tk.Tk()
        self.tkinter = thr.Thread(target=tk.mainloop)
        self.tkinter.setDaemon(True)
        self.tkinter.start()

    def run(self):
        while True:
            print("i'm updating")
            self.main_window.run()
