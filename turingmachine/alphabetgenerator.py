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
            yield self.letter + str(self.counter)
            self.counter += 1

    def get_resrved(self):
        for i in range(self.counter):
            yield self.letter + str(i)
        yield self.letter


class AlphabetGenerator:
    """Class for generating short, unique condition strings
    to work with in a TuringMachineMacro"""

    def __init__(self, alphabet=None, gen=None):
        if alphabet is None:
            self.alphabet = string.ascii_lowercase + string.digits
        else:
            self.alphabet = alphabet

        self.it = self._get_letter()

        self.templates = {}
        self.reserved = set()
        if gen is not None:
            self.set_template(gen)
        else:
            self.it = self._get_letter()

    def set_template(self, name):
        """Set a new template, or continue if
        it already exists"""

        temp = NameTemplate(name)
        name = temp.letter

        if name not in self.templates:
            self.templates[name] = temp

        self.it = self.templates[name].iterate()
        self.reserved.update(set(temp.get_resrved()))

    def del_template(self):
        """Set template to default generator"""

        self.it = self._get_letter()

    cur_template = property(None, set_template, del_template)

    def _get_letter(self):
        """Generate all possible products of all possible symbols,
        that doesn't start with a number
        """

        for i in range(1, len(self.alphabet)):  # error with the same names
            for elem in map(
                    lambda x: ''.join(x),
                    filter(
                        lambda x: x[0] not in string.digits,
                        itertools.product(self.alphabet, repeat=i)
                        )
                    ):
                    yield elem

    def pop(self):
        while True:
            res = next(self.it)
            if res not in self.reserved:
                self.reserved.add(res)
                return res
