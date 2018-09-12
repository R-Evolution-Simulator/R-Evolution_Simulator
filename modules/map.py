import os
import shutil

from PIL import ImageDraw, Image as Img

from . import utility as utl
from . import var
from .noise.simplexnoise.noise import SimplexNoise, normalize


class Map(object):
    """class of the world where creatures live"""

    def __init__(self, name, variables):
        """
        Creates new map

        :param map: name of the map
        :type map: str
        :param variables: parameters of the map
        :type variables: dict
        :return:
        """
        self.name = name
        self.path = os.path.join(var.MAPS_PATH, name)
        self.__dict__.update(variables)
        self.noises = dict()
        # self.tot_chunks = self.dimension['width'] * self.dimension['height']
        self.chunk_list = [[None for x in range(self.dimension['height'])] for y in
                           range(self.dimension['width'])]
        self._directory_setup()

    def _directory_setup(self):
        """
        Creates new directory for maps and overwrites it if it already exists

        :return:
        """
        try:
            os.makedirs(self.path)
        except FileExistsError:
            shutil.rmtree(self.path)
            os.makedirs(self.path)

    def generate(self):
        for i in self.noises_params:
            self.noises[i] = SimplexNoise(**self.noises_params[i])
        for i in range(len(self.chunk_list)):  # quindi ogni 0 e' sostituito con un Chunk
            for j in range(len(self.chunk_list[0])):
                self.chunk_list[i][j] = self._new_chunk(i, j)
        self._save()

    def _new_chunk(self, x, y):
        chunk = {'x': x,
                 'y': y,
                 'foodmax': normalize(self.noises['foodmax'].noise(x, y)) * self.map_maxes['foodmax'],
                 'temperature': (normalize(self.noises['temperature'].noise(x, y)) - 0.5) * self.map_maxes['temperature'] * 2
                 }
        return chunk

    def _save(self):
        to_write = str()
        for i in var.TO_RECORD['map']:
            to_write += utl.add_to_write(self.__dict__[i], self.map_rounding)
        with open(os.path.join(self.path, f"params.{var.FILE_EXTENSIONS['map_data']}"), 'w') as file:
            try:
                file.write(to_write[:-1])
            except ValueError:
                pass
            for i in range(len(self.chunk_list)):
                for j in range(len(self.chunk_list[0])):
                    to_write = str()
                    chunk = self.chunk_list[i][j]
                    for k in var.TO_RECORD['map_chunk']:
                        to_write += utl.add_to_write(chunk[k], self.map_rounding)
                    file.write('\n' + to_write[:-1])
        self._draw_backgrounds()

    def _draw_backgrounds(self):
        for attr in self.noises:
            image = Img.new("RGB", (int(self.dimension['width']), int(self.dimension['height'])))
            draw = ImageDraw.Draw(image)
            if attr == 'foodmax':
                for chunk_row in self.chunk_list:
                    for chunk in chunk_row:
                        draw.rectangle((chunk['x'] * self.chunk_dim / 10,
                                        chunk['y'] * self.chunk_dim / 10,
                                        (chunk['x'] + 1) * self.chunk_dim / 10,
                                        (chunk['y'] + 1) * self.chunk_dim / 10),
                                       fill=(0, int(chunk['foodmax'] * 255 / 100), 0))
            elif attr == 'temperature':
                for chunk_row in self.chunk_list:
                    for chunk in chunk_row:
                        if chunk['temperature'] > 0:
                            draw.rectangle((chunk['x'] * self.chunk_dim / 10,
                                            chunk['y'] * self.chunk_dim / 10,
                                            (chunk['x'] + 1) * self.chunk_dim / 10,
                                            (chunk['y'] + 1) * self.chunk_dim / 10),
                                           fill=(255, int(255 - (chunk['temperature'] / 100 * 255)),
                                                 int(255 - (chunk['temperature'] / 100 * 255))))
                        else:
                            draw.rectangle((chunk['x'] * self.chunk_dim / 10,
                                            chunk['y'] * self.chunk_dim / 10,
                                            (chunk['x'] + 1) * self.chunk_dim / 10,
                                            (chunk['y'] + 1) * self.chunk_dim / 10),
                                           fill=(int(255 + (chunk['temperature'] / 100 * 255)),
                                                 int(255 + (chunk['temperature'] / 100 * 255)), 255))
            path = os.path.join(self.path, f"{attr}.gif")
            image.save(path, "GIF")
