from random import random as rnd, gauss


class BaseGene(object):
    def __init__(self, gen=None, phen=None):
        if not phen:
            self.genotype = gen
            self.phenotype = None
            if gen:
                self.fenotype_calc()
        else:
            self.phenotype = phen

    def randomize(self, lims=None):  # placeholder
        pass

    def _phenotype_calc(self):  # placeholder
        pass

    def reproduce(self, other, sigma):
        return None

    @property
    def get(self):
        return self.phenotype


class Allele():
    def __init__(self, value, dominance):
        self.value = value
        self.dominance = dominance  # Allele dominance: 0 if recessive, 1 if dominant

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False


class MendelGene(BaseGene):
    ALLELES = []

    def randomize(self, lims=None):
        genotype = list()
        for i in range(2):
            genotype.append(self.ALLELES[int(rnd() * len(self.ALLELES))])
        self.genotype = genotype
        self._phenotype_calc()

    def reproduce(self, other, sigma):
        return type(self)(gen=[self.genotype[int(rnd() * 2)], other.genotype[int(rnd() * 2)]])


class NumberGene(BaseGene):
    def randomize(self, lims):
        self.genotype = rnd() * (lims[1] - lims[0])

    def _phenotype_calc(self):
        self.phenotype = self.genotype

    def reproduce(self, other, sigma):
        return type(self)(gen=((self.genotype + other.genotype)*(1/2 + gauss(0, sigma))))


class TempResist(MendelGene):
    ALLELES = [Allele('N', 1), Allele('c', 0), Allele('l', 0)]

    def _phenotype_calc(self):
        if self.genotype[0] == self.ALLELES[0] or self.genotype[1] == self.ALLELES[0]:
            phen = 'N'
        elif not self.genotype[0] == self.genotype[1]:
            phen = 'n'
        else:
            if self.genotype[0] == self.ALLELES[1]:
                phen = 'c'
            else:
                phen = 'l'
        self.phenotype = phen


class Agility(NumberGene):
    pass


class Bigness(NumberGene):
    pass


class Fertility(NumberGene):
    pass


class NumControl(NumberGene):
    pass


class Speed(BaseGene):
    def __init__(self, agility, bigness):
        super(Speed, self).__init__(phen=((agility.get() / bigness.get()) * 2))


class EatCoeff(BaseGene):
    def __init__(self, bigness, max):
        super(Speed, self).__init__(phen=(bigness.get() * max))
