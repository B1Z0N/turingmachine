"""
Talk about undetermined condition(moving))0)0))00)
Think about exception guaranties(what could you give 'em
"""
import abc

from collections import namedtuple
from collections.abc import Iterable

from functools import wraps

import enum

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
        self._sin_val_cond = False
        self._mul_val_cond = False
        self._sin_val_mul_cond = False

        if isinstance(stick_val, str) and isinstance(stick_cond, str):
            # two parameters and it is ordinary string value, condition
            self._set_ordinary(stick_val, stick_cond)
            self._sin_val_cond = True
        elif isinstance(stick_val, Iterable) and isinstance(stick_cond, Iterable):
            if isinstance(stick_val, str):
                # two parameters and it is value iterable, and ordinary string condition
                self._set_single_value_multiple_conditions(stick_val, stick_cond)
                self._sin_val_mul_cond = True
            else:
                # two parameters and it is two iterables of values and conditions
                self._set_two_iterables(stick_val, stick_cond)
                self._mul_val_cond = True
        else:
            # nothing of the above
            raise self.StickError(stick_val, stick_cond)

    def set(self, stick_val, stick_cond=None):
        self.__init__(stick_val, stick_cond=stick_cond)

    def get(self):
        return self.contains

    def _set_two_iterables(self, values: Iterable, conditions: Iterable):
        self.contains = list(values), list(conditions)

    def _set_single_value_multiple_conditions(self, values: Iterable, conditions: Iterable):
        self.contains = values, list(conditions)

    def _set_ordinary(self, value: str, condition: str):
        self.contains = value, condition

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
        """Do some setup work"""
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
            return self.parallel_move(direction, next_vals=next_val, suppose_vals=suppose_val, next_conds=next_cond)

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
        assert self.val_cond.is_sin_val_cond(), \
            "There are join for joining multiple conditions, and parallelise for continuing multiple conditions"

        next_cond = NextCondition.get_condition(self, next_cond)
        next_val = self.val_cond.get_values() if next_val is None else next_val
        self.reserve_name({next_val}, {next_cond})

        if suppose_val is None:
            suppose_val = next_val
        try:
            self.tm.set_rule(
                *self.val_cond.get(),
                next_val, next_cond, direction
            )
        except machine.RuleExistsError:
            pass

        self.val_cond.set(suppose_val, next_cond)
        return self.val_cond

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
        assert self.val_cond.is_sin_val_mul_cond(), \
            "Single value and multiple conditions should be passed"

        if next_cond == NextCondition.prev:
            raise self.UndeterminedConditionError(self.val_cond)

        next_cond = NextCondition.get_condition(self, next_cond)
        next_val = self.val_cond.get_values() if next_val is None else next_val

        suppose_val = next_val if suppose_val is None else suppose_val

        self.reserve_name({next_val}, {next_cond})

        value = self.val_cond.get_values()
        for condition in self.val_cond.get_conds():
            try:
                self.tm.set_rule(value, condition, next_val,
                                 next_cond, direction)
            except machine.RuleExistsError:
                pass

        self.val_cond.set(suppose_val, next_cond)
        return self.val_cond

    def parallel_move(self, direction, suppose_vals=None, next_vals=None, next_conds=NextCondition.prev):
        """
        Sets rule for multiple conditions, smth alike for_each

        For automatically generating next_conds, see NextCondition documentation

        Arguments:
            next_vals: next values for rule, previous if omitted
            direction: direction
            suppose_vals: suppose values for next move
            next_conds: next conditions for move, previous by default
        Returns:
            MacroStick object containing values, conditions dict of this move
        """
        assert self.val_cond.is_sin_val_mul_cond(), \
            "Single value and multiple conditions should be passed"

        length = len(self.val_cond.get_conds())

        if next_vals is None:
            next_vals = [self.val_cond.get_values()] * length

        try:
            assert not isinstance(suppose_vals, str)
            len(suppose_vals)
            firstly_supposed = suppose_vals
        except:
            firstly_supposed = suppose_vals
            suppose_vals = [suppose_vals] * length

        assert len(next_vals) == len(self.val_cond.get_conds()) == len(suppose_vals), \
            "Lengths of next_vals, suppose_vals, and last move val-cond pairs should be equal"

        next_conds = NextCondition.get_condition(self, next_conds, amount=length)
        self.reserve_name(set(next_vals), set(next_conds))

        conditions = self.val_cond.get_conds()
        value = self.val_cond.get_values()
        for i in range(length):
            try:
                self.tm.set_rule(value, conditions[i], next_vals[i],
                                 next_conds[i], direction)
            except machine.RuleExistsError:
                pass

        self.val_cond.set(firstly_supposed, next_conds)
        return self.val_cond

    def stop(self):
        """
        Finish macro machine execution, every command after this function
        will be useless.

        Should be called only in determined condition and value.

        Returns:
            MacroStick object containing value, condition pair of the last move
        """
        if not self.val_cond.is_sin_val_cond():
            raise self.UndeterminedConditionError(self.val_cond)

        return self.single_move('STOP')


class MacroFunc(metaclass=abc.ABCMeta):
    """
    Descriptor base class for acting like a function of one
    of the subclasses of Basic class.

    Should only be used with classes that give the same interface as Basic

    Attributes:
        obj: link to Basic object, to act as a descriptor
    """

    def __init__(self):
        self.obj = None

    def __call__(self, *args, **kwargs):
        """
        Decides what to do with passed arguments depending on current
        `sticked` machine value, if it is in determined condition than
        set_simple will be called, else continue_parallel will be called.

        To parallelise conditions use parallelise explicitly.

        To join them use join from Basic class.
        """
        if isinstance(self.obj.val_cond, dict):
            return self.parallel_move(*args, **kwargs)
        else:
            return self.single_move(*args, **kwargs)

    @abc.abstractmethod
    def single_move(*args, **kwargs):
        """
        If we are simply moving from determined condition to determined condition
        """
        pass

    @abc.abstractmethod
    def parallelise(self, *args, **kwargs):
        """
        If we are creating branches from determined condition
        """
        pass

    @abc.abstractmethod
    def parallel_move(self, *args, **kwargs):
        """
        If we are continuing our parallel branches, analogous to for_each
        """
        pass

    def __get__(self, obj: Basic, cls):
        """Get object, needed for descriptor call"""
        self.obj = obj

        return self


def macrofunc_preconditions(needed_type, error_msg):
    """
    Decorator for asserting and signaling about non-conformant stick-value type
    """

    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            self = args[0]
            assert get(self.obj, needed_assertion), error_msg

            return func(*args[1:], **kwargs)

        return inner

    return outer


class GoToConcept(MacroFunc, metaclass=abc.ABCMeta):
    # TODO: you could find patterns and shortify code of three main functions
    # TODO: make set_sticks for incapsulation
    """
    Class for managing move to val functionality with
    parameterized actions to perform between start and stop
    point values

    Generalises behaviour of some common operations like
    MoveToVal, SetAllOnWay, CleanRange

    The only difference among this examples is it's function of going
    through the tape to val:
    in MoveToVal it is      a q1 -> a q1 R (do nothing and move)
    in SetAllOnWay it is    a q1 -> b q1 R (change all values to some value 'b')
    in CleanRange it is     a q1 -> default q1 R (clean all values to 'default')

    To customize behaviour inherit from this class and define:
    1. start_modifier: for custom start value changing
    2. move_modifier: for custom move value changing
    3. end_modifier: for custom end value changing

    """

    __ERROR_MSG = "single_move, parallelise - for determined condition, continue_parallel" \
                  " for undetermined(multiple conditions)"

    @macrofunc_preconditions(tuple, __ERROR_MSG)
    def parallelise(
            self,
            move_vals: Iterable,
            end_val: Iterable,
            direction: str,
            start_vals=None
    ):
        """
        Branch one condition and multiple values to multiple conditions for each value.
        Should be called only in determined condition and value

        Arguments:
            move_vals: values of moving
            end_val: stop value
            direction: direction
        Returns:
            MacroStick object with values and conditions of this move
        """
        start_vals = set(start_vals).union({self.obj.val_cond[0]})
        start_cond = self.obj.val_cond[1]
        move_vals = set(move_vals).difference({end_val}).union(start_vals)
        # preparation

        result = []
        for start_value in start_vals:
            self.obj.val_cond = start_value, start_cond
            result.append(self.single_move(move_vals, end_val, direction))

        self.obj.val_cond = dict(result)
        return self.obj.val_cond

    @macrofunc_preconditions(dict, __ERROR_MSG)
    def parallel_move(
            self,
            move_vals: Iterable,
            end_val: Iterable,
            direction: str
    ):
        """
        Continue moving every branch separately.
        Should be called only in undetermined condition and value

        Arguments:
            move_vals: values of moving
            end_val: stop value
            direction: direction
        Returns:
            MacroStick object with values and conditions of this move
        """
        start_vals, start_conds = self.obj.val_cond.keys(), self.obj.val_cond.values()
        move_vals = set(move_vals).difference(end_vals).union(start_vals)
        # preparation

        returns = []
        for value, condition in self.obj.items():
            self.obj.val_cond = value, condition
            returns.append(self.single_move(move_vals, end_val, direction))
        # main move

        self.obj.val_cond = dict(returns)
        return self.obj.val_cond
        # finishing

    @macrofunc_preconditions(tuple, __ERROR_MSG)
    def single_move(
            self,
            move_vals: Iterable,
            end_vals: Iterable,
            direction: str
    ):
        """
        Perform simple move, from one pair of (value, condition) to [other pair]
        or [multiple values and one condition]

        Arguments:
            move_vals: values of moving
            end_vals: stop values
            direction: direction
        Returns:
            MacroStick object with values and conditions of this move
        """
        start_val, start_cond = self.obj.val_cond.get()
        end_vals = set(end_vals)
        move_vals = set(move_vals).difference(end_vals)
        # preparation

        move_cond, start_val = self.start_prepare(start_cond, set(start_val))
        move_vals = move_vals.union(start_val)
        # start

        self.main_move(move_cond, move_vals, direction)
        # main move

        end_cond = self.obj.cond_alpha.pop()
        result = []
        for value in end_vals:
            result.append(self._end_modifier(value))
            self.obj.tm.set_rule(value, move_cond, changed, end_cond, "S")

        self.obj.val_cond = changed, end_cond  #####!!!
        return self.obj.val_cond
        # finishing

    def _start_modifier(self, start_value):
        return self.start_modifier(start_value) \
            if self.include_start is True else start_value

    def _end_modifier(self, end_value):
        return self.end_modifier(end_value) \
            if self.include_end is True else end_value

    def __call__(
            self,
            move_vals: Iterable,
            end_vals: Iterable,
            direction: str,
            include_start=True,
            include_end=False,
    ):
        """
            Descriptor call function

            start_condition and start_value would be deduced from sticks

            Arguments:
                move_vals: values that we are moving through
                end_vals: stopping values
                direction: direction of moving
            Returns:
                one end condition or dict of values-conditions of stopping
        """
        self.include_start = include_start
        self.include_end = include_end
        super().__call__(self, move_vals, end_vals, direction)

    def start_prepare(self, start_cond, start_vals):
        """
        Settles all start_vals from start_cond to move_cond

        Arguments:
            start_cond: condition from which we are starting
            start_vals: set of starting values for moving
        Returns:
            move_cond: condition to which we are switching for further moving
            new_start_vals: changed start values
        """
        move_cond = self.obj.cond_alpha.pop()

        new_start_vals = []
        for value in start_vals:
            changed = self.start_modifier(value)
            self.obj.tm.set_rule(value, start_cond, changed, move_cond, "S")

            new_start_vals.append(changed)

        return move_cond, new_start_vals

    def main_move(self, move_cond, move_vals, direction):
        """
        Moves move_vals in direction with move_cond condition

        Arguments:
            move_cond: condition for moving further
            move_vals: value set to move through
            direction: direction of moving
        """
        for value in move_vals:
            changed = self.move_modifier(value)
            self.obj.tm.set_rule(value, move_cond, changed, move_cond, direction)

    @abc.abstractmethod
    def start_modifier(self, start_value):
        """
        Specializes what to do with start value
        """
        pass

    @abc.abstractmethod
    def move_modifier(self, move_value):
        """
        Specializes what to do with all of the
        middle `move` tape values
        """
        pass

    @abc.abstractmethod
    def end_modifier(self, end_value):
        """
        Specializes what to do with end value
        """


class MoveByVal(GoToConcept):
    """
    Class for going to value on tape
    """

    def move_modifier(self, move_value):
        return move_value

    start_modifier = end_modifier = move_modifier


# class SetAllOnWay(GoToConcept):
#     """
#     Class for changing one values to another one
#     while going through the tape
#     """
#     def __call__(
#             self,
#             to_val: str,
#             move_vals: Iterable,
#             end_vals: Iterable,
#             direction: str,
#             start_vals=None,
#             start_cond=None,
#             end_one_cond=True,
#             include_start=True,
#             include_end=False
#     ):
#         self.to_val = to_val
#         self.include_end = include_end
#         self.include_start = include_start
#
#         super().__call__(start_vals, move_vals, end_vals, direction,
#                          start_cond=start_cond, end_one_cond=end_one_cond)
#
#     def start_modifier(self, start_value):
#         return self.to_val if self.include_start else start_value
#
#     def move_modifier(self, move_value):
#         return self.to_val
#
#     def end_modifier(self, end_value):
#         return self.to_val if self.include_end else end_value
#
#
# class CleanRange(SetAllOnWay):
#     """Class for managing clearing of the tape range functionality"""
#     def __call__(
#             self,
#             move_vals: Iterable,
#             end_vals: Iterable,
#             direction: str,
#             start_vals=None,
#             start_cond=None,
#             end_one_cond=True,
#             include_start=True,
#             include_end=False
#     ):
#         super().__call__(self.obj.tm.default, start_vals, move_vals, end_vals,
#                          direction, start_cond=start_cond, end_one_cond=end_one_cond,
#                          include_start=include_start, include_end=include_end)

class Macro(Basic):
    move_by_val = MoveByVal()
