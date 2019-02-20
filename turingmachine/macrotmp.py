import abc

from turingmachine import alphabetgenerator
from turingmachine import machine


class Basic:

    def __init__(self, tm: machine.TuringMachine):
        self.tm = tm
        self.cond_alpha = alphabetgenerator.AlphabetGenerator(gen=self.tm.condition)
        self.val_alpha = alphabetgenerator.AlphabetGenerator()
        self.val_alpha.reserved.update(val for val in self.tm.tape)

        self.stick_cond = self.tm.condition
        self.stick_val = self.tm.current

    def set_rule(self, next_val, next_cond, direction, suppose_val=None):
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
    """Class for managing move by value functionality"""

    def __init__(self):
        self.cases = []
        self.reuse_case = None
        self.for_use = None

    @abc.abstractmethod
    def prepare(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def is_reusable(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def reuse(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    def move_by_val(self, *args, **kwargs) -> None:
        self.take_reusable(*args, **kwargs)
        self.prepare()
        self.use()

    def take_reusable(self, *args, **kwargs):
        self.reuse_case = None
        for case in self.cases:
            self.is_reusable(case, *args, **kwargs)
            if self.reuse_case is not None:
                break

    def use(self, *args, **kwargs):
        if self.reuse_case is not None:
            self.reuse(self, *args, **kwargs)
        else:
            self.create(self, *args, **kwargs)
            self.cases.append((args, kwargs))


class MoveByVal:
    """Class for managing move by value functionality"""

    def __init__(self):
        self.cases = []
        self.reuse_case = None

    def move_by_val(
            self, val: str,
            on_way_vals: abc.Iterable,
            direction: str,
            cycle=False
            ) -> None:
        self._take_reusable_set_all_on_way(val, on_way_vals, direction, cycle)
        self._prepare_set_all_on_way(val, on_way_vals, direction)
        self._use_set_all_on_way(val, on_way_vals, direction)

    def _take_reusable_set_all_on_way(self, val, on_way_vals, direction, cycle):
        self.reuse_case = None
        for case in self.cases:
            self._is_reusable_set_all_on_way(
                case, val, on_way_vals, direction, cycle
                )
            if self.reuse_case is not None: break

    def _use_set_all_on_way(self, val, on_way_vals, direction):
        if self.reuse_case is not None:
            self._reuse_set_all_on_way(self, val, on_way_vals, direction)
        else:
            self._new_set_all_on_way(self, val, on_way_vals, direction)
            self.cases.append((val, on_way_vals, direction))
