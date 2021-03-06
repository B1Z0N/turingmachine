"""
Module to generate tm code by python functions

Usage:

>>> create = lambda string: Macro(TuringMachine.from_str(string))

>>> tmac = create("1,0,1,0,1,b,1,0,o,t,c:::q1:")
>>> tmac.single_move("R", suppose_val="0")
# "1,0,1,0,1,b,1,0,o,t,c:1::-:" expected

>>> tmac = create("a,1,0,1,1,b,2,3,2,2,c:::q1:")
>>> tmac.copy_range(["1", "0"], "b", ["2", "3"], "c", [tmac.tm.default], "R")
>>> tmac.stop()
>>> tmac.tm.run()
# "a,1,0,1,1,b,2,3,2,2,c,1,0,1,1:::-:" expected

>>> tmac = create("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:")
>>> tmac.move_by_val.single_move(['0', '1', 'o', 't', 'b'], 'c', "R"
# "1,0,0,0,1,1,0,b,1,0,o,t,t,c:13::-:" expected

>>> tmac = create("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:")
>>> tmac.move_from_to.single_move(['0', '1', 'o', 't', 'b'], 'c', "R", replace_with="d")
>>> # "d,0,0,0,1,1,0,b,1,0,o,t,t,1:::-:" expected

"""
import abc
import enum
from collections.abc import Iterable

from ordered_set import OrderedSet

from turingmachine import alphabetgenerator
from turingmachine import machine


class MacroError(Exception):
    """Main exception class for this module"""
    pass


class MacroSticks:
    """
    Class that handles stick values for Basic class.

    Invariant: exactly one of this is true in every time point:
    1. is_mul_val_cond
    2. is_sin_val_cond
    3. is_sin_val_mul_cond

    Attributes:
        _sin_val_cond: val_cond contains single value and single condition
        _mul_val_cond: val_cond contains multiple values and multiple conditions
        _sin_val_mul_cond: val_cond contains single value and multiple conditions

        contains: container of different types determined by some of (look upper) parameters,
                  contains value(s) and condition(s)
        updated: are the sticks true for now?
    """

    class StickError(MacroError):
        """
        Error class for signalizing invalid input of stick value(s) and condition(s)
        """

        def __init__(self, val, cond):
            msg = "Enter value-condition, two iterables of value and " \
                  "condition or value-condition dictionary, not val: {} and cond: {}"
            super().__init__(msg.format(val, cond))

    def __init__(self, stick_val, stick_cond):
        """
        Set stick values depending on passed arguments.

        Pass:
            two iterables - multiple values and conditions
            one value and multiple conditions
            one value and one condition
        """
        self.updated = True

        self._sin_val_cond = False
        self._mul_val_cond = False
        self._sin_val_mul_cond = False
        self._mul_val_sin_cond = False

        if isinstance(stick_val, str) and isinstance(stick_cond, str):
            # two parameters and it is ordinary string value, condition
            self._set_ordinary(stick_val, stick_cond)
        elif isinstance(stick_val, Iterable) and isinstance(stick_cond, Iterable):
            if isinstance(stick_val, str):
                # two parameters and it is condition iterable, and ordinary string value
                self._set_single_value_multiple_conditions(stick_val, stick_cond)
            elif isinstance(stick_cond, str):
                # two parameters and it is value iterable, and ordinary string condition
                self._set_multiple_value_single_conditions(stick_val, stick_cond)
            else:
                # two parameters and it is two iterables of values and conditions
                self._set_two_iterables(stick_val, stick_cond)
        else:
            # nothing of the above
            raise self.StickError(stick_val, stick_cond)

    def set(self, stick_val=None, stick_cond=None):
        if stick_val is None and stick_cond is None:
            self.updated = True

        if stick_cond is None:
            stick_cond = self.contains[1]
        if stick_val is None:
            stick_val = self.contains[0]

        self.__init__(stick_val, stick_cond=stick_cond)
        return self.contains

    def get(self):
        return self.contains

    def _set_two_iterables(self, values: Iterable, conditions: Iterable):
        self.contains = list(values), list(conditions)
        self._mul_val_cond = True

    def _set_single_value_multiple_conditions(self, value: Iterable, conditions: Iterable):
        self.contains = value, list(conditions)
        self._sin_val_mul_cond = True

    def _set_multiple_value_single_conditions(self, values: Iterable, condition: Iterable):
        self.contains = list(values), condition
        self._mul_val_sin_cond = True

    def _set_ordinary(self, value: str, condition: str):
        self.contains = value, condition
        self._sin_val_cond = True

    def get_values(self):
        """
        Returns list of values, or single value
        """
        return self.contains[0]

    def get_conds(self):
        """
        Returns list of conditions, or single condition
        """
        return self.contains[1]

    def is_mul_val_cond(self):
        return self._mul_val_cond

    def is_sin_val_cond(self):
        return self._sin_val_cond

    def is_sin_val_mul_cond(self):
        return self._sin_val_mul_cond

    def is_mul_val_sin_cond(self):
        return self._mul_val_sin_cond

class NextCondition(enum.Enum):
    """
    Class that chooses what next condition to create depending
    on the argument passed using function set_condition

    Attributes:
        prev: select previous condition
        auto: generate new condition by condition alphabetgenerator
    """
    prev = enum.auto()
    auto = enum.auto()

    @staticmethod
    def get_condition(basic_obj, next_cond, amount=1):
        """
        Get condition depending on the arguments passed

        Arguments:
            basic_obj: object that are using this class to set conditions

            next_cond: condition. Could be of type NextCondition, than
            appropriate condition is settled automatically.
            Could be just a desirable next condition for the move, than
            it is simply returned.

            amount: amount of conditions for next move to be
            checked for or generated
        """
        cls = NextCondition

        if not isinstance(next_cond, cls):
            return next_cond

        elif next_cond == cls.prev:
            return basic_obj.val_cond.get_conds()

        elif next_cond == cls.auto:
            if amount != 1:
                return [basic_obj.cond_alpha.pop() for _ in range(amount)]
            return basic_obj.cond_alpha.pop()


class Basic:
    """
    Class with functionality common to all classes of macros. It simplifies
    creating programs on tm, and working with tm as a whole

    Attributes:
        tm: TuringMachine class for using this macro on
        cond_alpha: AlphabetGenerator class for automatically generating conditions
        val_alpha: AlphabetGenerator class for automatically generating values
        val_cond: current value and condition, could be determined(one pair), or
            undetermined(multiple pairs)
    """

    class UndeterminedConditionError(MacroError):
        def __init__(self, sticks):
            msg = "Undetermined condition:\n {}"
            super().__init__(msg.format(sticks.get()))

    def __init__(self, tm: machine.TuringMachine):
        self.tm = tm
        self.cond_alpha = alphabetgenerator.AlphabetGenerator(gen=self.tm.condition)
        self.val_alpha = alphabetgenerator.AlphabetGenerator()
        self.val_alpha.reserved.update(val for val in self.tm.tape)

        self.val_cond = MacroSticks(self.tm.current, self.tm.condition)

    def reserve_name(self, valset=None, condset=None):
        if valset is not None:
            self.val_alpha.reserved = self.val_alpha.reserved.union(valset)

        if condset is not None:
            self.cond_alpha.reserved = self.cond_alpha.reserved.union(condset)

    def set_rule(self, direction, next_val=None, suppose_val=None, join=False, next_cond=None):
        """
            Separates decisions of how to set the rule depending on the value-condition case:

            1. if join is true and if it ended in one value and multiple conditions,
                they are joined to one condition and value
            2. if it ended in multiple value-condition pairs, they are continuing moving each
            3. if it ended in one value and multiple conditions, they are continuing moving each,
            like in previous case
            4. if it ended in determined single value-condition pair, it is moved from one pair ot other

            !!! 5. if it ended in multiple value-condition pairs, then exception raised
            (there are no simple rule for this kind of situation, please modify tape to
            use one of the above cases)

            Next condition will be generated automatically

            Arguments:
                next_val: next value for rule
                direction: direction
                suppose_val: suppose_value for next position
                join: explicit join(equivalent to self.join call)
                next_cond: next desirable condition for this move.

                If settled to None, than
                if join is true it will be passed to join settled to
                NextCondition.auto
                else it will be settled to
                NextCondition.prev

                Also you could specify it, for example:
                    obj.set_rule( ... , next_cond=NextCondition.auto)
                    ...
                    onj.set_rule( ... , next_cond='q5')

            Returns:
                MacroStick object containing current case (value, condition)
        """

        def consists_of_one_value(lst):
            return isinstance(lst, str)

        if self.val_cond.is_mul_val_cond():
            if not consists_of_one_value(self.val_cond.get_values()):
                raise self.UndeterminedConditionError(self.val_cond)

        if join is True:
            next_cond = NextCondition.auto if next_cond is None else next_cond
            return self.join(direction, next_val=next_val, suppose_val=suppose_val, next_cond=next_cond)

        next_cond = NextCondition.prev if next_cond is None else next_cond
        if self.val_cond.is_sin_val_cond():
            return self.single_move(direction, next_val=next_val, suppose_val=suppose_val, next_cond=next_cond)
        else:
            return self.parallel_cond_move(direction, next_vals=next_val, suppose_vals=suppose_val, next_conds=next_cond)

    def is_up_to_date(self):
        assert self.val_cond.updated, "Should be updated after call to self.manual_rule, to use macro functions"

    def single_move(self, direction, suppose_val=None, next_val=None, next_cond=NextCondition.prev):
        """
        Set the rule for movement, suppose_val could be omitted if
        next tape value would be equal to next_val

        For automatically generating next_cond, see NextCondition documentation

        Use only if tm is in determined condition
        Arguments:
            next_val: next value for current sel, previous by default
            direction: direction
            suppose_val: suppose_value for next position
            next_cond: next condition for movement, previous by default
        Returns:
            MacroStick object containing value, condition pair of this move
        """
        self.is_up_to_date()
        assert self.val_cond.is_sin_val_cond(), \
            "There are join for joining multiple conditions, and parallelise for continuing multiple conditions"

        next_cond = NextCondition.get_condition(self, next_cond)
        next_val = self.val_cond.get_values() if next_val is None else next_val

        if suppose_val is None:
            suppose_val = next_val
        try:
            self.manual_rule(
                *self.val_cond.get(),
                next_val, next_cond, direction
            )
        except machine.RuleExistsError:
            pass

        return self.val_cond.set(suppose_val, next_cond)

    def join(self, direction, suppose_val=None, next_val=None, next_cond=NextCondition.auto):
        """
        Joins multiple conditions to one

        If it ended in multiple conditions and one value they are joined to one

        For automatically generating next_cond, see NextCondition documentation

        Arguments:
            next_val: next value for rule, previous if omitted
            direction: direction
            suppose_val: suppose value for next move
            next_cond: next condition for joining, autogenerated by default
        Returns:
            MacroStick object containing value, condition pair of this move
        """
        self.is_up_to_date()
        assert self.val_cond.is_sin_val_mul_cond(), \
            "Single value and multiple conditions should be passed"

        if next_cond == NextCondition.prev:
            raise self.UndeterminedConditionError(self.val_cond)

        next_cond = NextCondition.get_condition(self, next_cond)
        next_val = self.val_cond.get_values() if next_val is None else next_val

        suppose_val = next_val if suppose_val is None else suppose_val

        value = self.val_cond.get_values()
        for condition in self.val_cond.get_conds():
            try:
                self.manual_rule(value, condition, next_val,
                                 next_cond, direction)
            except machine.RuleExistsError:
                pass

        return self.val_cond.set(suppose_val, next_cond)

    def parallel_cond_move(self, direction, suppose_vals=None, next_vals=None, next_conds=NextCondition.prev):
        """
        Sets rule for multiple conditions, smth alike for_each

        For automatically generating next_conds, see NextCondition documentation

        Arguments:
            next_vals: next values for rule, previous if omitted
            direction: direction
            suppose_vals: suppose values for next move
            next_conds: next conditions for move, previous by default
        Returns:
            MacroStick object containing values, conditions iterables of this move
        """
        self.is_up_to_date()
        assert self.val_cond.is_sin_val_mul_cond(), \
            "Single value and multiple conditions should be passed"

        length = len(self.val_cond.get_conds())

        if next_vals is None:
            next_vals = [self.val_cond.get_values()] * length

        try:
            assert not isinstance(suppose_vals, str)
            len(suppose_vals)
            firstly_supposed = suppose_vals
        except:  # catches all
            firstly_supposed = suppose_vals
            suppose_vals = [suppose_vals] * length

        assert len(next_vals) == len(self.val_cond.get_conds()) == len(suppose_vals), \
            "Lengths of next_vals, suppose_vals, and last move val-cond pairs should be equal"

        next_conds = NextCondition.get_condition(self, next_conds, amount=length)

        conditions = self.val_cond.get_conds()
        value = self.val_cond.get_values()
        for i in range(length):
            try:
                self.manual_rule(value, conditions[i], next_vals[i],
                                 next_conds[i], direction)
            except machine.RuleExistsError:
                pass

        return self.val_cond.set(firstly_supposed, next_conds)

    def parallelise_by_vals(self, direction, suppose_vals=None, next_val=None, next_cond=NextCondition.prev):
        """
        val_cond:
            (value1, condition1) -> (values2, condition2)
        """
        _, cond = self.single_move(direction, next_val=next_val, next_cond=next_cond)
        return self.val_cond.set(suppose_vals, cond)

    def stop(self):
        """
        Finish macro machine execution, every command after this function
        will be useless.

        Should be called only in determined condition and value.

        Returns:
            MacroStick object containing value, condition pair of the last move
        """
        self.is_up_to_date()

        if self.val_cond.is_sin_val_cond():
            return self.single_move("STOP")
        elif self.val_cond.is_mul_val_sin_cond():
            vals, cond = self.val_cond.get()
            for value in vals:
                self.val_cond.set(value, cond)
                self.single_move("STOP")

            return self.val_cond.set(vals, cond)
        elif self.val_cond.is_sin_val_mul_cond():
            val, conds = self.val_cond.get()
            for condition in conds:
                self.val_cond.set(val, condition)
                self.single_move("STOP")

            return self.val_cond.set(val, conds)
        else:
            raise self.UndeterminedConditionError(self.val_cond)

    def manual_rule(self, value, condition, next_value, next_condition, direction):
        """
        Setting the rule for turing and preserving some parameters of this macro.

        It is recommended to use this function instead of self.tm.set_rule
        Both of this functions are used when you need "bare" access to turing machine.
        Be careful, you will need to set val_cond to some meaningful value after this call.
        """
        self.reserve_name({next_value}, {next_condition})
        self.tm.set_rule(value, condition, next_value, next_condition, direction)

        self.val_cond.updated = False


class GoToConceptABC(metaclass=abc.ABCMeta):
    """
    Class to implement a common algorithm. Of moving on tape,
    with flexible changing of starting, moving and ending values
    functionality.

    Attributes:
        obj: instance of Basic
    """
    def __init__(self, obj: Basic):
        """Set Basic object to work with"""
        self.obj = obj

    def _set_includes(self, include_start: bool, include_end: bool):
        """
        Common operation of setting arguments.

        Arguments:
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        """
        self._include_start = include_start
        self._include_end = include_end

    def single_move(self,
                    move_vals: Iterable,
                    end_vals: Iterable or str,
                    direction: str,
                    include_start=True, include_end=False
                    ):
        """
        Move on tape.

        (value, condition) -> (value[s]1, condition1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_vals: values to stop with
            direction: direction
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, condition in case of single end_vals
            or value and multiple conditions in case of multiple end_vals
        """
        # preparation
        self._set_includes(include_start, include_end)
        end_vals = [end_vals] if isinstance(end_vals, str) else end_vals
        end_vals = OrderedSet(end_vals)
        move_vals = OrderedSet(move_vals) - end_vals

        # start move
        new_start_value = self._start_modifier(self.obj.val_cond.get_values())
        _, move_cond = self.obj.single_move(direction, next_val=new_start_value, next_cond=NextCondition.auto)

        # main move
        for value in move_vals:
            self.obj.manual_rule(value, move_cond, self._move_modifier(value), move_cond, direction)

        # end move
        new_end_vals = [self._end_modifier(value) for value in end_vals]
        end_cond = self.obj.cond_alpha.pop()

        for i in range(len(end_vals)):
            self.obj.manual_rule(end_vals[i], move_cond, new_end_vals[i], end_cond, "S")

        return self.obj.val_cond.set(new_end_vals[0] if len(new_end_vals) == 1
                                     else new_end_vals, end_cond)

    def parallelise(self,
                    move_vals: Iterable,
                    end_val: str,
                    direction: str,
                    start_vals=None,
                    include_start=True, include_end=False
                    ):
        """
        Parallelise by conds for each value in start_vals and
        move for each to end_val.

        (values, condition) -> (value1, conditions1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_val: value(single) to stop with
            direction: direction
            start_vals: values to parallelise, if omitted,
            self.val_cond.get_values() is used to get them
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, multiple conditions
        """
        if start_vals is None:
            start_vals, _ = self.obj.val_cond.get()
        start_vals = OrderedSet(start_vals)

        move_vals -= OrderedSet(end_val) | start_vals
        start_value, start_cond = self.obj.val_cond.set(start_vals, self.obj.val_cond.get_conds())

        assert self.obj.val_cond.is_mul_val_sin_cond(), \
            "Multiple values and single condition should be passed"

        end_conds = []
        for start_value in start_vals:
            move_cond = self.obj.cond_alpha.pop()
            self.obj.manual_rule(start_value, start_cond, start_value, move_cond, "S")

            self.obj.val_cond.set(start_value, move_cond)
            end_conds.append(
                self.single_move(move_vals.union(start_vals), end_val, direction,
                                 include_start=include_start, include_end=include_end)[1]
            )

        return self.obj.val_cond.set(end_val, end_conds)

    def parallel_move(self, move_vals: Iterable, end_val: str, direction: str,
                      include_start=True, include_end=False
                      ):
        """
        Move for each cond in self.obj.val_cond.get_conds()
        move for each to end_val.

        (value, conditions) -> (value1, conditions)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_val: value(single) to stop with
            direction: direction
            self.val_cond.get_values() is used to get them
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, multiple conditions
        """
        assert self.obj.val_cond.is_sin_val_mul_cond(), \
            "Single value and multiple conditions should be passed"

        start_val, start_conds = self.obj.val_cond.get()

        end_conds = []
        for condition in start_conds:
            self.obj.val_cond.set(start_val, condition)
            end_conds.append(
                self.single_move(move_vals, end_val, direction,
                                 include_end=include_end, include_start=include_start)[1]
            )

        return self.obj.val_cond.set(end_val, end_conds)

    def main(self, move_vals: Iterable, end_vals: Iterable or str,
             direction: str, include_start=True, include_end=False):
        """
        Main function for calling as __call__

        Basically the same as self.single_move

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_vals: values to stop with
            direction: direction
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, condition in case of single end_vals
            or value and multiple conditions in case of multiple end_vals
        """
        self.single_move(move_vals, end_vals, direction, include_end, include_start)

    __call__ = main

    def _move_modifier(self, move_val):
        """Internal function for modifying move values"""
        return self.move_modifier(move_val)

    def _start_modifier(self, start_val):
        """Internal function for modifying start values"""
        return self.start_modifier(start_val) if self._include_start else start_val

    def _end_modifier(self, end_val):
        """Internal function for modifying end values"""
        return self.end_modifier(end_val) if self._include_end else end_val

    @abc.abstractmethod
    def move_modifier(self, move_val):
        """
        External function for modifying move values
        Should be redefined in child classes for different behaviour
        """
        pass

    @abc.abstractmethod
    def start_modifier(self, start_val):
        """
        External function for modifying start values
        Should be redefined in child classes for different behaviour
        """
        pass

    @abc.abstractmethod
    def end_modifier(self, end_val):
        """
        External function for modifying end values
        Should be redefined in child classes for different behaviour
        """
        pass


class GoToConcept(GoToConceptABC):
    def move_modifier(self, move_val):
        return move_val

    def start_modifier(self, start_val):
        return start_val

    def end_modifier(self, end_val):
        return end_val


class IgnoreThis:
    """
    Class for signaling that this
    keyword parameter should be ignored
    """
    pass


class MoveByVal(GoToConcept):
    """ Main class for moving to value on the tape"""

    def single_move(self, move_vals: Iterable, end_vals: Iterable or str,
                    direction: str, include_start=IgnoreThis, include_end=IgnoreThis):
        return super().single_move(move_vals, end_vals, direction)

    def parallelise(self, move_vals: Iterable, end_val: str, direction: str,
                    start_vals=None, include_start=IgnoreThis, include_end=IgnoreThis):
        return super().parallelise(move_vals, end_val, direction, start_vals=start_vals)

    def parallel_move(self, move_vals: Iterable, end_val: str,
                      direction: str, include_start=IgnoreThis, include_end=IgnoreThis):
        return super().parallel_move(move_vals, end_val, direction)

    def main(self, move_vals: Iterable, end_vals: Iterable or str,
             direction: str, include_start=IgnoreThis, include_end=IgnoreThis):
        return super().main(move_vals, end_vals, direction)

    __call__ = main


class CleanRange(GoToConcept):
    """Main class for clearing the range on the tape"""
    def move_modifier(self, move_val):
        return self.obj.tm.default

    def start_modifier(self, start_val):
        return self.obj.tm.default

    def end_modifier(self, end_val):
        return self.obj.tm.default

    def parallel_move(self, *args, **kwargs):
        """Not needed in this class"""
        pass

    def parallelise(self, *args, **kwargs):
        """Not needed in this class"""
        pass


class SetAllOnWay(GoToConcept):
    """Main class for setting all values on way to end_val with to_val"""
    def move_modifier(self, move_val):
        return self.to_val

    def start_modifier(self, start_val):
        return self.to_val

    def end_modifier(self, end_val):
        return self.to_val

    def __init__(self, obj):
        self._default = obj.tm.default
        super().__init__(obj)

    def single_move(self, move_vals: Iterable, end_vals: Iterable or str,
                    direction: str, to_val=None, include_start=True, include_end=False):
        self.to_val = to_val if to_val is not None else self._default
        return super().single_move(move_vals, end_vals, direction, include_start, include_end)

    def main(self, move_vals: Iterable, end_vals: Iterable or str,
             direction: str, to_val=None, include_start=True, include_end=False):
        self.to_val = to_val if to_val is not None else self._default
        return super().main(move_vals, end_vals, direction, include_start, include_end)

    def parallel_move(self, *args, **kwargs):
        pass

    def parallelise(self, *args, **kwargs):
        pass

    __call__ = main


class PutByVal(MoveByVal):
    """Main class for moving to end_val and putting put_val instead"""

    def single_move(self, move_vals: Iterable, end_vals: Iterable or str,
                    direction: str, put_val=None, include_start=IgnoreThis, include_end=IgnoreThis):
        """
        Move on tape and put_val instead of end_vals.

        (value, condition) -> (put_val, condition1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_vals: values to stop with
            direction: direction
            put_val: value to put instead of end_val, if omitted
            this function would be equal to moving by value,
            not changing anything
            include_start: unused, needed for inheritance compatibility
            include_end: unused, needed for inheritance compatibility
        Returns:
            tuple of value, condition in case of single end_vals
            or value and multiple conditions in case of multiple end_vals
        """
        val_cond = super().single_move(move_vals, end_vals, direction, include_start=True, include_end=True)

        if put_val is not None:
            try:
                if self.obj.val_cond.is_sin_val_cond():
                    val_cond = self.obj.single_move("S", next_val=put_val)
                else:
                    cur_cond = self.obj.val_cond.get_conds()
                    end_cond = self.obj.cond_alpha.pop()
                    for value in self.obj.val_cond.get_values():
                        self.obj.val_cond.set(value, cur_cond)
                        self.obj.single_move("S", next_val=put_val, next_cond=end_cond)
                    val_cond = self.obj.val_cond.set(put_val, end_cond)
            except AssertionError:
                raise Basic.UndeterminedConditionError(self.obj.val_cond)

        return val_cond

    def parallelise(self, move_vals: Iterable, end_val: str,
                    direction: str, put_vals=None, start_vals=None, include_start=IgnoreThis, include_end=IgnoreThis):
        """
        Parallelise by conds for each value in start_vals and
        move for each to end_val.

        (values, condition) -> (value1, conditions1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_val: value(single) to stop with
            direction: direction
            put_vals: values to put instead of end_val, if omitted
            this function would be equal to parallelise in MoveByVal,
            not changing anything
            start_vals: values to parallelise, if omitted,
            self.val_cond.get_values() is used to get them
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, multiple conditions
        """
        val_cond = super().parallelise(move_vals, end_val, direction, start_vals, include_start=True, include_end=True)
        if put_vals is not None:
            val_cond = self.set_appropriate(put_vals, conditions=val_cond[1])

        return val_cond

    def set_appropriate(self, put_vals, conditions=None):
        """
        Set value from self.val_cond.get_values() in appropriate
        condition from conditions. To value from put_vals and
        final condition.

        (values, conditions) -> (put_vals, condition1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.
        """
        cur_val = self.obj.val_cond.get_values()
        if conditions is None:
            conditions = self.obj.val_cond.get_conds()

        finita_condition = self.obj.cond_alpha.pop()
        for i in range(len(put_vals)):
            self.obj.manual_rule(cur_val, conditions[i], put_vals[i], finita_condition, "S")

        return self.obj.val_cond.set(put_vals, finita_condition)

    def main(self, move_vals: Iterable, end_vals: Iterable or str,
             direction: str, put_val=None, include_start=IgnoreThis, include_end=IgnoreThis):
        return super().main(move_vals, end_vals, direction, include_start=True, include_end=True)

    __call__ = main


class MoveFromTo(PutByVal):
    """
    Main class for moving from to end_val and
    replacing starting value with replace_with
    """
    def single_move(self, move_vals: Iterable, end_vals: Iterable or str,
                    direction: str, replace_with=None, include_start=IgnoreThis, include_end=IgnoreThis):
        """
        Move on tape and put_val instead of end_vals.

        (value, condition) -> (start_val, condition1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_vals: values to stop with
            direction: direction
            replace_with: value to put instead of start_val, if omitted
            this function would be equal to moving by value,
            not changing anything
            include_start: unused, needed for inheritance compatibility
            include_end: unused, needed for inheritance compatibility
        Returns:
            tuple of value, condition in case of single end_vals
            or value and multiple conditions in case of multiple end_vals
        """

        put_val = None
        if replace_with is not None:
            put_val = self.obj.val_cond.get_values()
            self.obj.single_move("S", next_val=replace_with)

        return super().single_move(move_vals, end_vals, direction, put_val=put_val)

    def parallelise(self, move_vals: Iterable, end_val: str,
                    direction: str, replace_with=None, start_vals=None, include_start=IgnoreThis,
                    include_end=IgnoreThis):
        """
        Parallelise by conds for each value in start_vals and repalce tham with
        replace_with move for each to end_val and put start_vals to them.

        (values, condition) -> (value1, conditions1)

        self.obj.val_cond should be settled to determined single
        value-condition pair condition. After work this function
        sets self.obj.val_cond appropriate.

        Arguments:
            move_vals: values to move through
            end_val: value(single) to stop with
            direction: direction
            replace_with: values to put instead of start_vals, if omitted
            this function would be equal to parallelise in MoveByVal,
            not changing anything
            start_vals: values to parallelise, if omitted,
            self.val_cond.get_values() is used to get them
            include_start: should we use start_modifier function?
            include_end: should we use end_modifier function?
        Returns:
            tuple of value, multiple conditions
        """
        put_vals = None
        if replace_with is not None:
            if start_vals is None:
                start_vals = self.obj.val_cond.get_values()
            put_vals = start_vals

            start_cond = self.obj.val_cond.get_conds()
            move_cond = self.obj.cond_alpha.pop()
            for start, replace in zip(start_vals, replace_with):
                self.obj.manual_rule(start, start_cond, replace, move_cond, "S")

            self.obj.val_cond.set(replace_with, move_cond)
            start_vals = replace_with

        return super().parallelise(move_vals, end_val, direction, put_vals=put_vals, start_vals=start_vals)

    def main(self, move_vals: Iterable, end_vals: Iterable or str,
             direction: str, replace_with=None, include_start=IgnoreThis, include_end=IgnoreThis):
        return self.single_move(move_vals, end_vals, direction, replace_with=replace_with)

    __call__ = main


class Macro(Basic):
    """
    Full basic macro class
    """

    def __init__(self, tm: machine.TuringMachine):
        super().__init__(tm)

        self.move_by_val = MoveByVal(self)
        self.clean_range = CleanRange(self)
        self.set_all_on_way = SetAllOnWay(self)
        self.put_by_val = PutByVal(self)
        self.move_from_to = MoveFromTo(self)

    def copy_range(self, values, end1, between12,
                   start2, after2, direction, clear_values=False):
        """
        Copy 'values' from range [start_val ... end1] to range [start2 ...]
        Layout for this function
        [self.val_cond.get_values(), *values, end1, *between12, start2, *after2]
        clear_values: clears initial values
        """
        # preparation
        values = OrderedSet(values)
        between12 = OrderedSet(between12)
        after2 = OrderedSet(after2)

        start_val = self.val_cond.get_values()

        values -= OrderedSet([end1, start_val])
        between12 -= OrderedSet([end1, start2])
        after2 -= OrderedSet(start2)

        end2 = self.val_alpha.pop()
        move_set = values | between12 | after2 | OrderedSet([start_val, end1, start2])
        opdirection = "R" if direction == "L" else "L"

        # put end2 at the end and return
        self.move_by_val.single_move(values, end1, direction)
        self.move_by_val.single_move(between12, start2, direction)
        self.put_by_val.single_move([start2], after2, direction, end2)

        self.single_move(opdirection, suppose_val=start2)
        self.move_by_val.single_move(between12, end1, opdirection)
        self.move_by_val.single_move(values, start_val, opdirection)
        self.single_move(direction)

        # start copying
        replace_with = OrderedSet(self.val_alpha.pop() for _ in range(len(values)))
        copy_cond = self.val_cond.get_conds()  # !!!
        self.move_from_to.parallelise(move_set, end2, direction, start_vals=values, replace_with=replace_with)

        # restore end2 delimiter
        restore_conds = []
        capture_cond = self.val_cond.get_conds()
        for value in self.val_cond.get_values():
            self.val_cond.set(stick_val=value, stick_cond=capture_cond)
            restore_conds.append(self.put_by_val.single_move([value], after2, direction, put_val=end2)[1])
        self.val_cond.set(stick_val=end2, stick_cond=restore_conds)
        self.join("S")

        # return back and start again
        self.move_by_val.single_move(move_set, replace_with, opdirection)
        capture_cond = self.val_cond.get_conds()
        for value in self.val_cond.get_values():
            self.val_cond.set(value, capture_cond)
            self.single_move(direction, next_cond=copy_cond)

        # ending the loop and cleaning
        clean_cond = self.cond_alpha.pop()
        self.manual_rule(end1, copy_cond, end1, clean_cond, opdirection)
        self.val_cond.set(end1, clean_cond)

        if clear_values is False:
            for replace, restore in zip(replace_with, values):
                self.manual_rule(replace, clean_cond, restore, clean_cond, opdirection)
        else:
            for replace in replace_with:
                self.manual_rule(replace, clean_cond, self.tm.default, clean_cond, opdirection)

        end_cond = self.cond_alpha.pop()
        self.manual_rule(start_val, clean_cond, start_val, end_cond, "S")
        return self.val_cond.set(start_val, end_cond)

    def move_range(self, values, end1, between12,
                   start2, after2, direction):
        """
        Move 'values' from range [start_val ... end1] to range [start2 ...]
        Layout for this function
        [self.val_cond.get_values(), *values, end1, *between12, start2, *after2]
        """
        return self.copy_range(values, end1, between12, start2,
                               after2, direction, clear_values=True)
