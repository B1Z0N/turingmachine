""""Class for adding basic functionality for
writing programs with TuringMachine class"""

import itertools
import string
from turing.machine.turing import TuringMachine


class TuringAlphabet:

    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.it = self.get_letter()

    def get_letter(self):
        for i in range(1, len(self.alphabet)):
            for elem in filter(lambda x: x[0] not in string.digits,
                               itertools.product(self.alphabet, repeat=i)
                               ):
                yield elem

    def pop(self):
        return next(self.it)


class TuringMacros:

    def __init__(self, tm: TuringMachine):
        self.tm = tm
