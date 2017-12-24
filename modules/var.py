import os
import pygame as pyg
from . import genes as gns

SIMULATIONS_PATH = os.path.join(os.getcwd(), "simulations")

# simulation

DFEAULT_SIM_VARIABLES = {'dimension': (60, 45),  # in chunks
                         'chunk_dim': 10,
                         'max_lifetime': 10000,
                         'initial_creatures': 750,
                         'chunks_vars': {'growth_coeff': 0.0005,
                                         'foodmax_max': 100,
                                         'temperature_max': 100,
                                         },
                         'creatures_vars': {'view_ray': 3,
                                            'en_dec_coeff': 0.02,
                                            'en_inc_coeff': 1.5,
                                            'average_age': 2000,
                                            'dev_age_prob': 750,
                                            'temp_death_prob_coeff': 100,
                                            'genes_lim': {'agility': (10, 60),
                                                          'bigness': (20, 80),
                                                          'fertility': (50, 250),
                                                          'num_control': (0, 100)
                                                          },
                                            'mutation_coeff': 0.05,
                                            },
                         'analysis': {'time_interval': 100,
                                      'percentile_parts': 4,
                                      'parts': 8,
                                      'rounding': 4}
                         }

CHUNK_ATTRS = ('temperature', 'foodmax')

CREATURES_GENES = {'agility': gns.Agility, 'bigness': gns.Bigness, 'fertility': gns.Fertility,
                   'num_control': gns.NumControl, 'temp_resist': gns.TempResist, 'mndl_control': gns.MendelControl}

# files

FILE_SEPARATOR = ';'

HISTORY_SEPARATORS = (',', '/')

TO_RECORD = {
    'simulation': ['name', 'dimension', 'lifetime', 'initial_creatures', 'chunk_dim', 'tick_count', 'chunks_vars',
                   'creatures_vars', 'analysis', 'ID_count'],
    'creature': ['ID', 'birth_tick', 'parents_ID', 'sex', 'genes', 'death_tick', 'death_cause'],
    'chunk': ['coord', 'foodmax', 'growth_rate', 'temperature']}

# graphics

DEFAULT_CREATURES_COLORS = {'N': pyg.Color(255, 255, 255, 255),
                            'S': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                            'TR': {'c': pyg.Color(255, 0, 0, 255), 'l': pyg.Color(0, 0, 255, 255),
                                   'N': pyg.Color(128, 128, 128, 255), 'n': pyg.Color(255, 255, 255, 255)}}

DEFAULT_CREATURES_DIMS = {'N': 7, 'A': 5, 'B': 7, 'EC': 42, 'NCG': 9, 'S': 5}

DEFAULT_CREATURES_BORDER = {'color': pyg.Color(0, 0, 0, 255), 'width': 1}
