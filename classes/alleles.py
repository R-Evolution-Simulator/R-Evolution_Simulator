DOMINANT = 1
RECESSIVE = 0


class Allele(object):
    def __init__(self, value, dominance):
        self.value = value
        self.dominance = dominance  # Allele dominance: 0 if recessive, 1 if dominant

    def is_dominant(self):
        return self.dominance == DOMINANT

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False

    def __add__(self, other):
        if other.is_dominant():
            return other.value
        else:
            return self.value
