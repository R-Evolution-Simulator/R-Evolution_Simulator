from random import random as rnd, gauss
from .alleles import *


class BaseGene(object):
    def __init__(self, gen=None, phen=None):
        if not phen:
            self.genotype = gen
            self.phenotype = None
            if gen:
                self._phenotype_calc()
        else:
            self.phenotype = phen

    def randomize(self):
        self._phenotype_calc()

    def _phenotype_calc(self):
        pass

    def reproduce(self, other, sigma):
        return None

    def get(self):
        return self.phenotype


class MendelGene(BaseGene):
    ALLELES = []

    def randomize(self, lims=None):
        genotype = list()
        for i in range(2):
            genotype.append(Allele(*self.ALLELES[int(rnd() * len(self.ALLELES))]))
        self.genotype = genotype
        super(MendelGene, self).randomize()

    def _phenotype_calc(self):
        self.phenotype = self.genotype[0] + self.genotype[1]

    def reproduce(self, other, sigma):
        return type(self)(gen=[self.genotype[int(rnd() * 2)], other.genotype[int(rnd() * 2)]])


class NumberGene(BaseGene):
    def randomize(self, lims):
        self.genotype = rnd() * (lims[1] - lims[0])
        super(NumberGene, self).randomize()

    def _phenotype_calc(self):
        self.phenotype = self.genotype

    def reproduce(self, other, sigma):
        return type(self)(gen=((self.genotype + other.genotype) * (1 / 2 + gauss(0, sigma))))


class TempResist(MendelGene):
    ALLELES = [('N', DOMINANT), ('c', RECESSIVE), ('l', RECESSIVE)]

    def _phenotype_calc(self):
        if self.genotype[0].is_dominant() or self.genotype[1].is_dominant():
            phen = 'N'
        elif not self.genotype[0] == self.genotype[1]:
            phen = 'n'
        else:
            phen = self.genotype[0].value
        self.phenotype = phen


class Agility(NumberGene):
    pass


class Bigness(NumberGene):
    pass


class Fertility(NumberGene):
    pass


class NumControl(NumberGene):
    pass


class Speed(NumberGene):
    def __init__(self, agility, bigness):
        super(Speed, self).__init__(gen=((agility.get() / bigness.get()) * 2))


class EatCoeff(NumberGene):
    def __init__(self, bigness, max):
        super(EatCoeff, self).__init__(gen=(bigness.get() * max))
