import abc
import functools
from collections import namedtuple
from collections.abc import Iterable

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
        self.args = None
        self.cur_case = None

    @abc.abstractmethod
    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    @abc.abstractmethod
    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create(self, obj: Basic, *args, **kwargs):
        pass

    def main(self, obj: Basic, *args, **kwargs) -> None:
        self.prepare(obj, *args, **kwargs)
        self.use(obj)

    # def take_reusable(self, obj: Basic, *args, **kwargs):
    #     self.is_reuse = False
    #     for case in self.cases:
    #         self.prepare(obj, case, *args, **kwargs)
    #         if self.is_reuse is True:
    #             break

    def use(self, obj: Basic):
        if self.cur_case is not None:
            self.reuse(obj, *self.args)
        else:
            self.create(obj, *self.args)

    __call__ = main

    def __get__(self, obj: Basic, cls):
        func = functools.partial(self.__call__, obj)

        return func


MacroCase = namedtuple("MacroCase", "conds args")


class Params:
    def __init__(self, args, kwargs=None):
        self.kwargs = None if kwargs is None else kwargs
        self.args = args


# noinspection PyMethodOverriding,PyMethodOverriding,PyMethodOverriding,PyMethodOverriding
class MoveByVal(MacroFuncTemplate):
    """Class for managing move by value functionality"""

    MoveByValConds = namedtuple("MoveByValConds", "move_cond, end_cond")

    def prepare(
            self, obj: Basic,
            val: str,
            on_way_vals: Iterable,
            direction: str,
            cycle=False,
            new=False
            ):
        on_way_vals = {on_way_vals}
        on_way_vals = on_way_vals.difference({val})
        on_way_vals = on_way_vals.union({obj.stick_val})

        self.cur_case = None
        if new is True:
            self.args = (val, on_way_vals, direction)
            return

        for case in self.cases:
            val1, on_way_vals1, direction1 = case.params.args

            if direction == direction1:
                reuse = True
            else:
                continue

            if cycle:
                reuse = reuse and val in val1
                reuse = reuse and all((
                    on_way_vals.issubset(on_way_vals1),
                    val in val1
                    ))
            else:
                reuse = reuse and all((
                    on_way_vals.isdisjoint(on_way_vals1),
                    val not in on_way_vals1,
                    val1 not in on_way_vals,
                    val != val1
                    ))
            if reuse is True:
                self.cur_case = case
                break

        if self.cur_case is not None:
            self.args = (val, on_way_vals, direction, cycle)
        else:
            self.args = (val, on_way_vals, direction)

    @staticmethod
    def _main_move(
            obj: Basic, val: str,
            on_way_vals: set,
            direction: str,
            cycle=True
            ):
        obj.set_rule(obj.stick_val, obj.stick_cond, direction)

        for oval in on_way_vals:
            obj.tm.set_rule(
                oval, obj.stick_cond,
                oval, obj.stick_cond,
                direction
                )

        obj.stick_val = val
        if cycle is False:
            obj.set_rule(val, obj.cond_alpha.pop(), 'S')

    def reuse(
            self, obj: Basic, val: str,
            on_way_vals: set,
            direction: str,
            cycle: bool
            ):
        _, on_way_vals1, _ = self.cur_case.params.args

        move_set = on_way_vals1.difference(on_way_vals)
        self._main_move(obj, val, move_set, direction, cycle)

        if cycle:
            params = Params((val, on_way_vals.union(on_way_vals1), direction))
            conds = self.MoveByValConds(
                move_cond=self.cur_case.conds.move_cond,
                end_cond=self.cur_case.conds.end_cond
                )

            self.cases.append(MacroCase(conds, params))
        else:

    def create(
            self, obj: Basic, val: str,
            on_way_vals: set,
            direction: str,
            ):
        """Stops once val was encountered on the tape"""
        start_cond = obj.stick_cond

        self._main_move(obj, val, on_way_vals, direction)

        params = Params((val, on_way_vals, direction))
        conds = self.MoveByValConds(move_cond=start_cond, end_cond=obj.stick_cond)

        self.cases.append(MacroCase(conds, params))


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
            on_way_vals: Iterable,
            direction: str
            ):
        pass

    def move_one(
            self, to: str,
            on_way_vals: Iterable,
            direction: str
            ):
        pass

    def put_one(
            self, val: str, to: str,
            on_way_vals: Iterable,
            direction
            ):
        pass

    def clean_one(self):
        pass

    def move_range(
            self,
            start1: str,
            between1: Iterable,
            end1: str,
            between12: Iterable,
            start2: str,
            after2: Iterable,
            direction
            ):
        pass
