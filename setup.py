from setuptools import setup

if __name__ == "__main__":

    setup(
        name = "R-Evolution Simulator",
        version='1.0.0',
        packages = ['modules','modules.noise','modules.noise.examples','modules.noise.img','modules.noise.simplexnoise',
                    'modules.noise.tests','data','data.templates','data.sounds.cows',
                    ],
        scripts=['R-Evolution_Simulator.py'],
        author = "Federico Malnati, Matteo Palmieri, Alessandro Sosso",
        author_email = "revolution.simulator@gmail.com",
        url = "https://r-evolution-simulator.github.io/",
        install_requires=[
            'scipy',
            'numpy',
            'Pillow',
            'pygame',
            'matplotlib'
        ],
)
