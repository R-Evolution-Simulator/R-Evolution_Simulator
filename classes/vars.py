import os
import pygame as pyg

SIMULATIONS_PATH = os.path.join(os.getcwd(), "simulations")

DFEAULT_SIM_VARIABLES = {'width': 600,
                         'height': 450,
                         'chunk_dim': 10,
                         'lifetime': 600,
                         'initial_creatures': 600,
                         'chunks_vars': {'growth_coeff': 0.0005,
                                         'foodmax_max': 100,
                                         'temperature_max': 100,
                                         },
                         'creatures_vars': {'view_ray': 0.0005,
                                            'en_dec_coeff': 0.02,
                                            'en_inc_coeff': 1.5,
                                            'average_age': 2000,
                                            'dev_age_prob': 750,
                                            'temp_death_prob_coeff': 100,
                                            'genes_lim': {'agility': (10, 60),
                                                          'bigness': (20, 80),
                                                          'fertility': (50, 250),
                                                          'numControlGene': (0, 100)
                                                          },
                                            'mutation_coeff': 0.1,
                                            'eat_coeff_max': 0.1,
                                            },
                         }

DEFAULT_CREATURES_COLORS = {'N': pyg.Color(255, 255, 255, 255),
                            'S': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                            'TR': {'c': pyg.Color(255, 0, 0, 255), 'l': pyg.Color(0, 0, 255, 255), 'N': pyg.Color(128, 128, 128, 255), 'n': pyg.Color(255, 255, 255, 255)}}

DEFAULT_CREATURES_DIMS = {'N': 7, 'A': 5, 'B': 7, 'EC': 42, 'NCG': 9, 'S': 5}

DEFAULT_CREATURES_BORDER = {'color': pyg.Color(0, 0, 0, 255), 'width': 1}
