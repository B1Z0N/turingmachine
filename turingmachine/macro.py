import abc
import functools
from collections.abc import Hashable

from turingmachine import alphabetgenerator
from turingmachine import machine


class Basic:
    """Class with functionality common to all classes of macros"""

    def __init__(self, tm: machine.TuringMachine):
        """Do some setup work"""
        self.tm = tm
        self.cond_alpha = alphabetgenerator.AlphabetGenerator(gen=self.tm.condition)
        self.val_alpha = alphabetgenerator.AlphabetGenerator()
        self.val_alpha.reserved.update(val for val in self.tm.tape)

        self.stick_cond = self.tm.condition
        self.stick_val = self.tm.current

    def set_rule(self, next_val, next_cond, direction, suppose_val=None):
        """
        Set the rule for movement, suppose_val should be omitted if
        next tape value would be equal to next_val
        """

        if suppose_val is None:
            suppose_val = next_val

        self.tm.set_rule(
            self.stick_val, self.stick_cond,
            next_val, next_cond, direction
            )
        self.stick_val = suppose_val
        self.stick_cond = next_cond

    def stop(self):
        """
        Finish macro machine execution, every command after this function
        will be useless
        """
        self.set_rule(self.stick_val, self.stick_cond, 'STOP')


class MacroFuncTemplate(metaclass=abc.ABCMeta):
    """
    Descriptor ABC class for acting like a function of one
    of the subclasses of Basic class
    """

    def __init__(self):
        self.cases = []
        self.reuse_case = None
        self.for_use = None

    @abc.abstractmethod
    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    @abc.abstractmethod
    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    @abc.abstractmethod
    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create(self, obj: Basic, *args, **kwargs):
        pass

    def main(self, obj: Basic, *args, **kwargs) -> None:
        self.take_reusable(obj, *args, **kwargs)
        self.prepare(obj, *args, **kwargs)
        self.use(obj, *args, **kwargs)

    def take_reusable(self, obj: Basic, *args, **kwargs):
        self.reuse_case = None
        for case in self.cases:
            self.is_reusable(obj, case, *args, **kwargs)
            if self.reuse_case is not None:
                break

    def use(self, obj: Basic, *args, **kwargs):
        if self.reuse_case is not None:
            self.reuse(obj, *args, **kwargs)
        else:
            self.create(obj, *args, **kwargs)
            self.cases.append((args, kwargs))

    __call__ = main

    def __get__(self, obj: Basic, cls):
        func = functools.partial(self.__call__, obj)

        return func


class MoveByVal(MacroFuncTemplate):
    """Class for managing move by value functionality"""

    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    def create(self, obj: Basic, *args, **kwargs):
        pass


class SetAllOnWay(MacroFuncTemplate):
    """
    Class for setting changing one values to another
    while going through the tape
    """

    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    def create(self, obj: Basic, *args, **kwargs):
        pass


class CopyRange(MacroFuncTemplate):
    """Class for managing copying of the tape range functionality"""

    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    def create(self, obj: Basic, *args, **kwargs):
        pass


class CleanRange(MacroFuncTemplate):
    """Class for managing clearing of the tape range functionality"""

    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    def create(self, obj: Basic, *args, **kwargs):
        pass


class MacroMain(Basic):
    """Assembly of all main helper macro classes"""

    move_by_val = MoveByVal()
    set_all_on_way = SetAllOnWay()
    copy_range = CopyRange()
    clean_range = CleanRange()

    def copy_one(
            self, to: str,
            on_way_vals: Hashable,
            direction: str
            ):
        pass

    def move_one(
            self, to: str,
            on_way_vals: Hashable,
            direction: str
            ):
        pass

    def put_one(
            self, val: str, to: str,
            on_way_vals: Hashable,
            direction
            ):
        pass

    def clean_one(self):
        pass

    def move_range(
            self,
            start1: str,
            between1: Hashable,
            end1: str,
            between12: Hashable,
            start2: str,
            after2: Hashable,
            direction
            ):
        pass
