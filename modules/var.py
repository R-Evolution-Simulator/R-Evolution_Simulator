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
SOUNDS_PATH = os.path.join(DATA_PATH, "sounds")

# simulation

DEFAULT_SIM_VARIABLES = {'dimension': {  # dimension in chunks of the simulation
    'width': None,
    'height': None
},
    'chunk_dim': None,  # dimension of the chunk
    'max_lifetime': None,  # max lifetime in ticks
    'initial_creatures': {  # number of creatures at the start
        'herbivores': None,  # herbivores
        'carnivores': None  # carnivores
    },
    'chunks_vars': {
        'growth_coeff': None,  # coefficient of growth of the food in the chunks
        'foodmax_max': None,  # max value of foodmax in a chunk
        'temperature_max': None,  # max value of temperature in a chunk
        'start_food': None,
    },
    'creatures_vars': {
        'view_ray': None,  # creatures' distance of view in chunks
        'en_dec_coeff': None,  # coefficient of energy decrease in creatures
        'eat_coeff': None,  # creatures' coefficient of eating
        'en_inc_coeff': None,  # coefficient of energy increase in creatures per bite
        'average_age': None,  # average age of natural death
        'dev_age_prob': None,  # standard deviation of age of natural death
        'temp_death_prob_coeff': None,  # coefficient for probability of death by temperature
        'genes_lim': {  # limits of genes in initial randomization
            'agility': (None, None),
            'bigness': (None, None),
            'fertility': (None, None),
            'num_control': (None, None)
        },
        'mutation_coeff': None,  # coefficient of mutation in genes reproduction
        'initial_reprod_countdown': None,  # time to add to countdown before first reproduction
        'reprod_energy_dec_coeff': None,  # coefficient of energy lost for reproduction
        'reprod_energy_need_coeff': None,  # energy needed for reproduction is this coefficient divided by fertility
        #'predator_eat_coeff': None,  # ?
        #'help_for_predator': None,  # ?
    },
    'analysis': {
        'tick_interval': None,  # tick interval between analysis
        'percentile_parts': None,  # number of percentile parts numeric genes analysis should be divided into
        'parts': None,  # number of parts spreading genes analysis should be divided into
        'rounding': None  # decimal places of rounding
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
                   'population_analysis': 'rsap',
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
                                   'start_food': None,
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
                                      #'predator_eat_coeff': None,
                                      #'help_for_predator': None,
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
