"""
this module contains all the variables used and their values
"""

import os
import pygame as pyg
from . import genes as gns

SIMULATIONS_PATH = os.path.join(os.getcwd(), "simulations")
DATA_PATH = os.path.join(os.getcwd(), "data")
TEMPLATES_PATH = os.path.join(DATA_PATH, "templates")
ERRORS_PATH = os.path.join(DATA_PATH, "errors")

# simulation

DEFAULT_SIM_VARIABLES = {'dimension': {  # dimension in chunks of the simulation
    'width': 60,
    'height': 45
},
    'chunk_dim': 10,  # dimension of the chunk
    'max_lifetime': 10000,  # max lifetime in ticks
    'initial_creatures': {  # number of creatures at the start
        'herbivores': 400,  # herbivores
        'carnivores': 100  # carnivores
    },
    'chunks_vars': {
        'growth_coeff': 0.0003,  # coefficient of growth of the food in the chunks
        'foodmax_max': 100,  # max value of foodmax in a chunk
        'temperature_max': 100,  # max value of temperature in a chunk
    },
    'creatures_vars': {
        'view_ray': 3,  # creatures' distance of view in chunks
        'en_dec_coeff': 0.02,  # coefficient of energy decrease in creatures
        'eat_coeff': 0.005,  # creatures' coefficient of eating
        'en_inc_coeff': 1.5,  # coefficient of energy increase in creatures per bite
        'average_age': 1000,  # average age of natural death
        'dev_age_prob': 200,  # standard deviation of age of natural death
        'temp_death_prob_coeff': 100,  # coefficient for probability of death by temperature
        'genes_lim': {  # limits of genes in initial randomization
            'agility': (10, 60),
            'bigness': (20, 80),
            'fertility': (150, 250),
            'num_control': (0, 100)
        },
        'mutation_coeff': 0.05,  # coefficient of mutation in genes reproduction
        'initial_reprod_countdown': 50,  # time to add to countdown before first reproduction
        'reprod_energy_dec_coeff': 0.8,  # coefficient of energy lost for reproduction
        'reprod_energy_need_coeff': 15000,  # energy needed for reproduction is this coefficient divided by fertility
        'predator_eat_coeff': 0.5,  # ?
        'help_for_predator': 1.5,  # ?
    },
    'analysis': {
        'tick_interval': 100,  # tick interval between analysis
        'percentile_parts': 4,  # number of percentile parts numeric genes analysis should be divided into
        'parts': 8,  # number of parts spreading genes analysis should be divided into
        'rounding': 4  # decimal places of rounding
    }
}

CHUNK_ATTRS = ('temperature', 'foodmax')

CREATURES_GENES = {'agility': gns.Agility, 'bigness': gns.Bigness, 'fertility': gns.Fertility,
                   'num_control': gns.NumControl, 'temp_resist': gns.TempResist, 'mndl_control': gns.MendelControl}
CREATURES_SECONDARY_GENES = {'speed': gns.Speed}

# files

DIRECTORIES = {'data': dict(), 'images': {'screenshots': dict(), 'diagrams': dict()}, 'analysis': dict()}

FILE_SEPARATORS = (';', '/', ',', '|', '§')

FILE_EXTENSIONS = {'numeric_analysis': 'rsan',
                   'spreading_analysis': 'rsas',
                   'demographic_analysis': 'rsad',
                   'chunks_attribute': 'rsca',
                   'creatures_data': 'rscr',
                   'chunks_data': 'rsch',
                   'simulation_data': 'rssd',
                   'simulation_template': 'rsst'}

TO_RECORD = {
    'simulation': {'name': None, 'dimension': {'width': None, 'height': None}, 'lifetime': None,
                   'initial_creatures': {
                       'herbivores': None,
                       'carnivores': None
                   }, 'chunk_dim': None, 'tick_count': None,
                   'chunks_vars': {'growth_coeff': None,
                                   'foodmax_max': None,
                                   'temperature_max': None,
                                   },
                   'creatures_vars': {'view_ray': None,
                                      'en_dec_coeff': None,
                                      'eat_coeff': None,
                                      'en_inc_coeff': None,
                                      'average_age': None,
                                      'dev_age_prob': None,
                                      'temp_death_prob_coeff': None,
                                      'genes_lim': {'agility': None,
                                                    'bigness': None,
                                                    'fertility': None,
                                                    'num_control': None
                                                    },
                                      'mutation_coeff': None,
                                      'initial_reprod_countdown': None,
                                      'reprod_energy_dec_coeff': None,
                                      'reprod_energy_need_coeff': None,
                                      'predator_eat_coeff': None,
                                      'help_for_predator': None,
                                      },
                   'analysis': {'tick_interval': None,
                                'percentile_parts': None,
                                'parts': None,
                                'rounding': None},
                   'ID_count': None},
    'creature': {'ID': None, 'birth_tick': None, 'parents_ID': None, 'sex': None, 'diet': None,
                 'genes': {'agility': None,
                           'bigness': None,
                           'fertility': None,
                           'num_control': None,
                           'temp_resist': None,
                           'mndl_control': None,
                           'speed': None
                           },
                 'death_tick': None, 'death_cause': None, 'tick_history': 1},
    'chunk': {'coord': None, 'foodmax': None, 'growth_rate': None, 'temperature': None, 'food_history': 1}}

# graphics

DEFAULT_CREATURES_COLORS = {'none': pyg.Color(255, 255, 255, 255),
                            'sex': (pyg.Color(255, 255, 0, 255), pyg.Color(0, 255, 255, 255)),
                            'temp_resist': {'c': pyg.Color(255, 0, 0, 255),
                                            'l': pyg.Color(0, 0, 255, 255),
                                            'N': pyg.Color(127, 127, 127, 255),
                                            'n': pyg.Color(255, 255, 255, 255)},
                            'mndl_control': {'A': pyg.Color(255, 0, 255, 255),
                                             'a': pyg.Color(255, 191, 255, 255), }
                            }

DEFAULT_CREATURES_DIMS = {'none': 49,
                          'agility': 5,
                          'bigness': 5,
                          'num_control': 5,
                          'speed': 25,
                          'energy': 5}

DEFAULT_CREATURES_BORDER = {'color': pyg.Color(0, 0, 0, 255), 'width': 1}
