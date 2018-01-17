from random import random as rnd, gauss
from .alleles import *

class BaseGene(object):
    """
    generic gene object
    """
    REC_TYPE = None

    def __init__(self, gen=None):
        """
        creates a gene

        :param gen: genotype of the gene
        """
        self.genotype = gen
        self.phenotype = None
        if gen:
            self._phenotype_calc()

    def randomize(self):
        """
        it evaluates the phenotype after a randomization

        :return:
        """
        self._phenotype_calc()

    def _phenotype_calc(self):
        """
        it evaluates the genotype of the gene

        :return:
        """
        pass

    def reproduce(self, other, sigma):
        """
        method to reproduce a gene with another

        :param other: the other gene
        :type other: BaseGene object
        :param sigma:

        :return: None
        """
        return None

    def get(self):
        """
        it gets the phenotype of the gene

        :return: the phenotype
        """
        return self.phenotype

    def __str__(self):
        """
        it creates a string of its genotype

        :return: the string created
        """
        return str(self.phenotype)


class MendelGene(BaseGene):
    """
    class of mendelian genes
    """
    ALLELES = [] #list of all possible alleles

    def randomize(self, lims=None):
        """
        it creates a generic random gene with 2 alleles taken from the list ALLELES

        :param lims: None
        :type lims: boolean

        :return:
        """
        genotype = list()
        for i in range(2):
            genotype.append(Allele(*self.ALLELES[int(rnd() * len(self.ALLELES))]))
        self.genotype = genotype
        super(MendelGene, self).randomize()

    def _phenotype_calc(self):
        """
        evaluates the phenotype of the gene

        :return:
        """
        self.phenotype = self.genotype[0] + self.genotype[1]

    def reproduce(self, other, sigma):
        """
        it reproduces itself with another gene created a random gene

        :param other: the other gene
        :param other: MendelGene object
        :param sigma:

        :return: the new gene
        """
        return type(self)(gen=[self.genotype[int(rnd() * 2)], other.genotype[int(rnd() * 2)]])


class NumberGene(BaseGene):
    """
    class of numeric characteristics
    """
    REC_TYPE = 'num'

    def randomize(self, lims):
        """
        it creates a random number respecting the limits

        :param lims: tuple of the 2 extreme limits
        :type lims: tuple

        :return:
        """
        self.genotype = lims[0] + rnd() * (lims[1] - lims[0])
        super(NumberGene, self).randomize()

    def _phenotype_calc(self):
        """
        it evaluates the phenotype

        :return:
        """
        self.phenotype = self.genotype

    def reproduce(self, other, sigma):
        """
        it reproduces itself with another gene. It is chosen one of the
        two genes and than it is applied a mutation on it. The mutation is chosen
        using a gaussian function

        :param other: the other gene
        :param other: NumberGene object
        :param sigma: standard deviation of the mutation
        :param sigma: int

        :return: the new gene
        """
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
        """
        nothing

        :return:
        """
        pass

    def reproduce(self, other, sigma):
        """
        it reproduces itself

        :param other: the other gene
        :type other: BaseGene object or an object derived
        :param sigma: standard deviation (if numeric gene considered) or None
        :type sigma: int or boolean

        :return: the new gene
        """
        new_gen = dict()
        for i in self.genotype:
            new_gen[i] = self.genotype[i].reproduce(other.genotype[i], sigma)
        return type(self)(gen=new_gen)


class TempResist(MendelGene):
    """
    class of the temperature resistant genes
    """
    REC_TYPE = 'spr'
    REC_CLASSES = (('N', 'n'), ('c',), ('l',))
    REC_CHUNK_ATTR = 'temperature'
    ALLELES = (('N', DOMINANT), ('c', RECESSIVE), ('l', RECESSIVE))

    def _phenotype_calc(self):
        """
        it evaluates the phenotype following mendelian rules

        :return:
        """
        if self.genotype[0].is_dominant() or self.genotype[1].is_dominant():
            phen = 'N'
        elif not self.genotype[0] == self.genotype[1]:
            phen = 'n'
        else:
            phen = self.genotype[0].value
        self.phenotype = phen


class MendelControl(MendelGene):
    """
    class of a mendel gene which has not phenotype consequences
    """

    REC_TYPE = 'spr'
    REC_CLASSES = (('A',), ('a',))
    REC_CHUNK_ATTR = 'temperature'
    ALLELES = (('A', DOMINANT), ('a', RECESSIVE))


class Agility(NumberGene):
    """
    class of the agility gene
    """
    pass


class Bigness(NumberGene):
    """
    class of the bigness gene
    """
    pass


class Fertility(NumberGene):
    """
    class of the fertility gene
    """
    pass


class NumControl(NumberGene):
    """
    class of the NumControl gene
    """
    pass


class Speed(SecondaryGene, NumberGene):
    """
    class of the speed gene
    """
    def _phenotype_calc(self):
        """
        it evaluates the phenotype of the speed gene depending of bigness and agility

        :return:
        """
        self.phenotype = self.genotype['agility'].get() / self.genotype['bigness'].get() * 2
