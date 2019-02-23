import abc
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


class MacroFuncABC(metaclass=abc.ABCMeta):
    """
    Descriptor ABC class for acting like a function of one
    of the subclasses of Basic class
    """

    def __init__(self):
        self.cases = []
        self.args = None
        self.cur_case = None
        self.cur_index = None
        self.obj = None

    @abc.abstractmethod
    def prepare(self, *args, **kwargs):
        """
        Filter parameters and chose whether create new set
        of conditions or reuse previous ones.

        Prepare args and put them in self.args to be set for
        self.reuse() or self.create()

        Loop through self.cases and choose one appropriate
        case for reuse, assign it to self.cur_case
        and it's index to self.cur_index. If there are
        no such case it should be assigned to None.
        """
        pass

    @abc.abstractmethod
    def reuse(self, *args, **kwargs):
        """
        Reuse function takes self.args prepared in
        self.prepare

        self.cur_case is helpful info for reuse
        handling.

        Reuse and edit self.cases[self.cur_index]
        so that it contains up to date info about
        this case.
        """
        pass

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        """
        Create function takes self.args prepared
        by self.prepare.

        Handle creating fully new case.

        Finally perform self.cases.append(macro_case),
        for future lookups
        """
        pass

    def main(self, *args, **kwargs) -> None:
        """Function that performs all actions"""
        self.prepare(self.obj, *args, **kwargs)
        self.use()

    # def take_reusable(self, obj: Basic, *args, **kwargs):
    #     self.is_reuse = False
    #     for case in self.cases:
    #         self.prepare(obj, case, *args, **kwargs)
    #         if self.is_reuse is True:
    #             break

    def use(self):
        """Checks whether to reuse older or create new case"""
        if self.cur_case is not None:
            self.reuse(self.obj, *self.args)
        else:
            self.create(self.obj, *self.args)

    __call__ = main

    def __get__(self, obj: Basic, cls):
        """Get main function"""
        self.obj = obj

        return self


"""
Class for shadowing MacroFuncABC docstrings.

MacroFuncABC's docstrings are for developers
extending macros functionality

MacroFuncTemplate's docstrings are for
developers using this module
"""


class MacroFuncTemplate(MacroFuncABC):
    """
    Template descriptor class
    for writing macros to Turing Machine
    """

    @abc.abstractmethod
    def prepare(self, *args, **kwargs):
        """
        Prepare and choose whether to reuse or
        create new case
        """
        pass

    @abc.abstractmethod
    def reuse(self, *args, **kwargs):
        """
        Reuse previous case
        """
        pass

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        """
        Create new case
        """
        pass


MacroCase = namedtuple("MacroCase", "conds params")
"""Recommended class for case in MacroFuncTemplate"""

Params = namedtuple("Params", "args kwargs")

"""Recommended class for args in MacroCase class"""


# noinspection PyMethodOverriding,PyMethodOverriding,PyMethodOverriding,PyMethodOverriding
class MoveByVal(MacroFuncTemplate):
    """Class for managing move by value functionality"""

    MoveByValConds = namedtuple("MoveByValConds", "move_cond, end_cond")
    """Internal class for communicating between functions"""

    def __call__(
            self, val: str,
            on_way_vals: Iterable,
            direction: str,
            cycle=False,
            new=False
            ):
        super().main(val, on_way_vals, direction, cycle=cycle, new=new)

    def prepare(
            self, val: str,
            on_way_vals: Iterable,
            direction: str,
            cycle=False,
            new=False
            ):
        obj = self.obj
        on_way_vals = set(on_way_vals)
        on_way_vals = on_way_vals.difference({val})
        on_way_vals = on_way_vals.union({obj.stick_val})

        self.cur_case = None
        if new is True:
            self.args = (val, on_way_vals, direction)
            return

        for index, case in enumerate(self.cases):
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
                    val not in on_way_vals1,
                    not val1.issubset(on_way_vals),
                    val not in val1
                    ))
            if reuse is True:
                self.cur_case = case
                self.cur_index = index
                break

        if self.cur_case is not None:
            self.args = (val, on_way_vals, direction, cycle)
        else:
            self.args = (val, on_way_vals, direction)

    def _main_move(
            self, val: str,
            on_way_vals: set,
            direction: str,
            cycle=False
            ):
        """Some code common to reuse and create functions"""
        obj = self.obj

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
            self, val: str,
            on_way_vals: set,
            direction: str,
            cycle: bool
            ):
        obj = self.obj
        cur_vals, on_way_vals1, _ = self.cur_case.params.args

        move_set = on_way_vals.difference(on_way_vals1)
        self._main_move(obj, val, move_set, direction, cycle)

        if cycle is False:
            cur_vals = cur_vals.union(val)

        params = Params((cur_vals, on_way_vals.union(on_way_vals1), direction), {})
        conds = self.MoveByValConds(
            move_cond=self.cur_case.conds.move_cond,
            end_cond=self.cur_case.conds.end_cond
            )
        self.cases[self.cur_index] = MacroCase(conds, params)

    def create(
            self, val: str,
            on_way_vals: set,
            direction: str,
            ):
        obj = self.obj
        start_cond = obj.stick_cond

        self._main_move(val, on_way_vals, direction)

        params = Params(({val}, on_way_vals, direction), {})
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
