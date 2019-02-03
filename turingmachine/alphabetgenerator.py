"""Module for generating names for Turing machine conditions"""

import itertools
import re
import string


class AlphabetError(Exception):
    """Base exception class for this module"""

    pass


class NotAllowedName(AlphabetError):
    """Raise this exception when the name is
    starting with numbers or special symbols,
    not with a latin letter"""

    def __init__(self, name):
        self.name = name
        super().__init__(self.__str__())

    def __str__(self):
        msg = "Disallowed name: {!r}"
        return msg.format(self.name)


class NameTemplate:
    """Class for generating new condition name based on
    a given symbol.

    Example:
        given 'q32' generated item will be q33
        given 'q' generated item will be q1
    """

    reg = re.compile(r'([a-zA-z]+)([0-9]*)')

    def __init__(self, name):
        match = re.match(self.reg, name)
        if match:
            count = match.group(2)
            self.counter = int(count) if count else 0
            self.letter = match.group(1)
        else:
            raise NotAllowedName(name)
        self.it = self.iterate()

    def iterate(self):
        while True:
            self.counter += 1
            yield self.letter + str(self.counter)


class AlphabetGenerator:
    """Class for generating short, unique condition strings
    to work with in a TuringMachineMacro"""

    def __init__(self, alphabet=None):
        if alphabet is None:
            self.alphabet = string.ascii_lowercase + string.digits
        else:
            self.alphabet = alphabet

        self.it = self.get_letter()
        self.templates = {}
        self.reserved = set()

    def set_template(self, name):
        """Set a new template, or continue if
        it already exists"""

        temp = NameTemplate(name)
        name = temp.letter

        if name not in self.templates:
            self.templates[name] = temp

        self.it = self.templates[name].iterate()

    def del_template(self):
        """Set template to default generator"""

        self.it = self.get_letter()

    cur_template = property(None, set_template, del_template)

    def get_letter(self):
        """Generate all possible products of all possible symbols,
        that doesn't start with a number
        """

        for i in range(1, len(self.alphabet)):
            for elem in map(
                    lambda x: ''.join(x),
                    filter(
                        lambda x: x[0] not in string.digits,
                        itertools.product(self.alphabet, repeat=i)
                        )
                    ):
                if elem in self.reserved:
                    continue
                else:
                    self.reserved.add(elem)
                    yield elem

    def pop(self):
        return next(self.it)
