import os
import pygame as pyg

SIMULATIONS_PATH = os.path.join(os.getcwd(), "simulations")

# simulation

DFEAULT_SIM_VARIABLES = {'width': 600,
                         'height': 450,
                         'chunk_dim': 10,
                         'lifetime': 10000,
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
                                                          'num_control_gene': (0, 100)
                                                          },
                                            'mutation_coeff': 0.1,
                                            'eat_coeff_max': 0.003,
                                            },
                         }

CHUNK_NOISE_ATTRS = ['temperature', 'foodmax']

# files

FILE_SEPARATOR = ';'

HISTORY_SEPARATORS = (',', '/')

TO_RECORD = {'simulation': ['name', 'width', 'height', 'lifetime', 'initial_creatures', 'chunk_dim', 'tick_count', 'chunks_vars', 'creatures_vars', 'ID_count'],
             'creature': ['ID', 'birth_tick', 'parents_ID', 'sex', 'genes', 'death_tick', 'death_cause'],
             'chunk': ['coord', 'foodmax', 'growth_rate', 'temperature']}

ROUNDINGS = {'simulation': None, 'creature': 4, 'chunk': 4}

# analysis

TIME_INTERVAL = 100

PERCENTILE_PARTS = 4

PARTS = 8

TEMPERATURE_FOOD_PARTS = {'temperature': 3, 'foodmax': 1}

ADJ_COEFF = 100

#graphics

DEFAULT_CREATURES_COLORS = {'N': pyg.Color(255, 255, 255, 255),
                            'S': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                            'TR': {'c': pyg.Color(255, 0, 0, 255), 'l': pyg.Color(0, 0, 255, 255), 'N': pyg.Color(128, 128, 128, 255), 'n': pyg.Color(255, 255, 255, 255)}}

DEFAULT_CREATURES_DIMS = {'N': 7, 'A': 5, 'B': 7, 'EC': 42, 'NCG': 9, 'S': 5}

DEFAULT_CREATURES_BORDER = {'color': pyg.Color(0, 0, 0, 255), 'width': 1}
