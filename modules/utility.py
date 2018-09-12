"""
this module contains some functions useful somwwhere in the other parts of the program
"""

import pygame as pyg

from . import var


def img_load(path):
    """
    Loads the image and converts it

    :param path: where the image is in the computer
    :type path: str

    :return: image
    """
    image = pyg.image.load(path)
    image.convert()
    return image


def img_resize(image, zoom):
    """
    It resizes the image given and returns it

    :param image: image to be resized
    :type image:
    :param zoom: zoom factor
    :type zoom: float

    :return: image resized
    """
    rect = image.get_rect()
    image = pyg.transform.scale(image, (int(rect.width * zoom), int(rect.height * zoom)))
    return image


def add_to_write(object, rounding, level=0):
    """
    converts the object into a string using separators in modulo var.py
    so that it can be saved in a file .csv

    :param object: object to be converted into string
    :type: dict or list or tuple or float
    :param rounding: how much the numbers must be approximated
    :type rounding: int
    :param level: parameter which indicates what separator has to be used
    :type level: int

    :return: the object converted
    """
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
                try:
                    return str(round(object.get(), rounding)) + var.FILE_SEPARATORS[level]
                except AttributeError:
                    pass
                except TypeError:
                    pass
        return str(object) + var.FILE_SEPARATORS[level]


def get_from_string(string, keys=None, level=0):
    """
    it takes data from a string, recognising the separators

    :param string: string to be converted
    :type: string: str
    :param level: integer which indicates what separator has to be used
    :type: level: int
    :param keys: variable used in case the string has to be converted into a dictionary
    :type keys: None, int or dict

    :return: the object containing the data taken from the string
    """
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
            to_return.append(get_from_string(split, level=level + 1))
    else:
        to_return = dict()
        i = 0
        for key in keys:
            to_return[key] = get_from_string(splits[i], keys[key], level + 1)
            i += 1
    return to_return
