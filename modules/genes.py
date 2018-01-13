from random import random as rnd, gauss
from .alleles import *


class BaseGene(object):
    REC_TYPE = None

    def __init__(self, gen=None):
        self.genotype = gen
        self.phenotype = None
        if gen:
            self._phenotype_calc()

    def randomize(self):
        self._phenotype_calc()

    def _phenotype_calc(self):
        pass

    def reproduce(self, other, sigma):
        return None

    def get(self):
        return self.phenotype

    def __str__(self):
        return str(self.phenotype)


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
    REC_TYPE = 'num'

    def randomize(self, lims):
        self.genotype = lims[0] + rnd() * (lims[1] - lims[0])
        super(NumberGene, self).randomize()

    def _phenotype_calc(self):
        self.phenotype = self.genotype

    def reproduce(self, other, sigma):
        random = int(rnd() * 2)
        if random:
            chosen = self
        else:
            chosen = other
        return type(self)(gen=(chosen.phenotype * (1 + gauss(0, sigma))))


class SecondaryGene(BaseGene):
    """
    Genes which have other genes as genotype
    """

    def _phenotype_calc(self):
        pass

    def reproduce(self, other, sigma):
        new_gen = dict()
        for i in self.genotype:
            new_gen[i] = self.genotype[i].reproduce(other.genotype[i], sigma)
        return type(self)(gen=new_gen)


class TempResist(MendelGene):
    REC_TYPE = 'spr'
    REC_CLASSES = (('N', 'n'), ('c',), ('l',))
    REC_CHUNK_ATTR = 'temperature'
    ALLELES = (('N', DOMINANT), ('c', RECESSIVE), ('l', RECESSIVE))

    def _phenotype_calc(self):
        if self.genotype[0].is_dominant() or self.genotype[1].is_dominant():
            phen = 'N'
        elif not self.genotype[0] == self.genotype[1]:
            phen = 'n'
        else:
            phen = self.genotype[0].value
        self.phenotype = phen


class MendelControl(MendelGene):
    REC_TYPE = 'spr'
    REC_CLASSES = (('A',), ('a',))
    REC_CHUNK_ATTR = 'temperature'
    ALLELES = (('A', DOMINANT), ('a', RECESSIVE))


class Agility(NumberGene):
    pass


class Bigness(NumberGene):
    pass


class Fertility(NumberGene):
    pass


class NumControl(NumberGene):
    pass


class Speed(SecondaryGene, NumberGene):
    def _phenotype_calc(self):
        self.phenotype = self.genotype['agility'].get() / self.genotype['bigness'].get() * 2

