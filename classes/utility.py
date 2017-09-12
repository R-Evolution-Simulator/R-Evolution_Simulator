import pygame as pyg


def img_load(path):
    image = pyg.image.load(path)
    image.convert()
    return image, image.get_rect()


def img_resize(image, zoom):
    rect = image.get_rect()
    image = pyg.transform.scale(image, (int(rect.width * zoom), int(rect.height * zoom)))
    return image, image.get_rect()
