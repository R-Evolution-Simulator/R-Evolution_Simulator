import pygame as pyg
from . import var


def img_load(path):
    image = pyg.image.load(path)
    image.convert()
    return image


def img_resize(image, zoom):
    rect = image.get_rect()
    image = pyg.transform.scale(image, (int(rect.width * zoom), int(rect.height * zoom)))
    return image


def add_to_write(object, rounding, level=0):
    if type(object) == dict:
        to_return = str()
        for i in object:
            to_return += add_to_write(object[i], rounding, level + 1)
        return to_return[:-1] + var.FILE_SEPARATORS[level]
    elif type(object) == list or type(object) == tuple:
        to_return = str()
        for i in object:
            to_return += add_to_write(i, rounding, level + 1)
        return to_return[:-1] + var.FILE_SEPARATORS[level]
    else:
        if rounding:
            try:
                return str(round(object, rounding)) + var.FILE_SEPARATORS[level]
            except TypeError:
                pass
        return str(object) + var.FILE_SEPARATORS[level]


def get_from_string(string, level, keys=None):
    splits = string.split(var.FILE_SEPARATORS[level])
    if len(splits) == 1 and not keys == 1:
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string
    if not keys or keys == 1:
        to_return = list()
        for split in splits:
            to_return.append(get_from_string(split, level + 1))
    else:
        to_return = dict()
        i = 0
        for key in keys:
            to_return[key] = get_from_string(splits[i], level + 1, keys[key])
            i += 1
    return to_return
