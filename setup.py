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
        description = "A simulator which reproduces what happens in a natural ecosystem",
        license = "GNU General Public License v3.0",
        summary = "(R)Evolution Simulator is a program written in Python 3.6 which objective is reproducing in a virtual simulation what happens in a real ecosystem. The entire world is populated by herbivore creatures which evolve their characteristics to survive in this environment. Some of the aspects examined are natural selection, transmission of genes with Mendel laws, distribution of the creature depending on the distribution of food and temperature, population trends.",
        install_requires=[
            'scipy',
            'numpy',
            'Pillow',
            'pygame',
            'matplotlib'
        ],
)
