"""
this modulo is used for the class Alleles which controls creation,
reproduction and transmission of alleles
"""

DOMINANT = 1
RECESSIVE = 0

class Allele(object):
    """
    class of alleles
    """
    def __init__(self, value, dominance):
        """
        creates a new allele

        :param value: the value of the allele
        :type value: str
        :param dominance: allele dominance: 0 if recessive, 1 if dominant
        :type dominance: int
        """
        self.value = value
        self.dominance = dominance

    def is_dominant(self):
        """
        it indicates if the allele is dominant

        :return: True if the allele is dominant, False otherwise
        """
        return self.dominance == DOMINANT

    def __eq__(self, other):
        """
        it compares two alleles to recognise if they are equal

        :param other: the other allele
        :type other: Allele object

        :return: True if they have got the same value, False otherwise
        """
        if self.value == other.value:
            return True
        return False

    def __add__(self, other):
        """
        it adds two alleles taking the value of the dominant one or
        returning the value of the recessive one (if both recessives)

        :param other: the other allele
        :type other: Allele object

        :return: the dominant one or the recessive one (if both recessives)
        """
        if other.is_dominant():
            return other.value
        else:
            return self.value
