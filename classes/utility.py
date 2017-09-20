import pygame as pyg
from . import vars


def img_load(path):
    image = pyg.image.load(path)
    image.convert()
    return image


def img_resize(image, zoom):
    rect = image.get_rect()
    image = pyg.transform.scale(image, (int(rect.width * zoom), int(rect.height * zoom)))
    return image


def add_to_write(object, rounding):
    if type(object) == dict:
        to_return = str()
        for i in object:
            to_return += add_to_write(object[i], rounding)
        return to_return
    else:
        if rounding:
            try:
                return str(round(object, rounding)) + vars.FILE_SEPARATOR
            except TypeError:
                pass
        return str(object) + vars.FILE_SEPARATOR


def history_to_write(history):
    to_write = str()
    for i in history:
        to_write += str(i) + vars.HISTORY_SEPARATORS[0]
    to_write = to_write[:-1] + vars.HISTORY_SEPARATORS[1]
    return to_write


def data_number(w, j):
    if w == 'temperature':
        x = j.genes['temp_resist']
        if x == "N" or x == "n":
            return 0

        elif x == "l":
            return 1

        elif x == "c":
            return 2
    else:
        return 0
