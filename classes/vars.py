import os

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
