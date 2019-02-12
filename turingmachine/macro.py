""""Class for adding basic functionality for
writing programs with TuringMachine class,
main class in this module is TuringMachineMacro"""

import tempfile
from collections import namedtuple
from collections.abc import Iterable

import anytree

from turingmachine import alphabetgenerator
from turingmachine import machine


class TuringMachineMacroError(Exception):
    """Main exception class for this module"""
    pass


class NotAppropriateSymbol(TuringMachineMacroError):
    """
    Class for warning about inappropriate in current context symbols
    for example a letter 'a' in a binary number (must be whether 0 or 1)
    """

    def __init__(self, symbol, appropriate_symbols):
        msg = "Inappropriate symbol: {!r}, should be one of this: {!r}"
        super().__init__(
            msg.format(
                symbol, appropriate_symbols
                )
            )


class InvalidRegionError(TuringMachineMacroError):
    """
    Class for warning about inappropriate in current context region
    to use, for example for converting from binary to unary use the same
    tape region
    """

    def __init__(self, *args):
        msg = "Use another region, issue with this dots: {}"
        super().__init__(
            msg.format(args)
            )


BinaryFunctionVector = namedtuple("BinaryFunctionVector", "name start end")


class TuringMachineMacro:
    """Class for writing rules to Turing Machine to perform
    some well known functions
    """

    def set_rule(self, next_val, next_cond, direction, suppose_val=None):
        if suppose_val is None:
            suppose_val = next_val

        self.tm.set_rule(
            self.stick_val, self.stick_cond,
            next_val, next_cond, direction
            )
        self.stick_val = suppose_val
        self.stick_cond = next_cond

    def gen_func_vec(
            self,
            func_tree: anytree.Node
            ):
        def get_func_and_args(tree):
            args = set()
            funcs = set()
            for elem in anytree.PostOrderIter(tree):
                if elem.is_leaf:
                    args.add(elem)
                else:
                    funcs.add(elem)

            return funcs, args

        funcs, args = get_func_and_args(func_tree)

        for function in funcs:
            self.val_alpha.reserved.add({function.start, function.end})

        symbols_for_args = {arg: self.val_alpha.pop() for arg in args}
        symbols_for_funcs = {func: self.val_alpha.pop() for func in funcs}

        between_bin = {'0', '1'}
        empty = [self.tm.default]
        between_all = {val for pair in funcs for val in (pair.start, pair.end)}
        between_all = between_all.union(between_bin, empty)

        def set_funcs(node, remember=False):
            nonlocal self, between_all, empty
            nonlocal symbols_for_args, symbols_for_funcs

            if node.is_leaf:
                next_cond = self.cond_alpha.pop()
                self.tm.set_rule(self.tm.default, self.stick_cond, symbols_for_args[node.name], next_cond, 'L')
                self.stick_cond = next_cond
                self.stick_val = self.tm.default
            else:
                if remember:
                    pass
                else:
                    conds = [self.cond_alpha.pop() for _ in range(3)]
                    end_val = self.val_alpha.pop()

                    between_all.add(end_val)
                    self.set_rule(self.tm.default, conds[0], 'L')
                    self.set_rule(self.tm.default, conds[1], 'L')
                    self.set_rule(end_val, conds[2], 'S')

                    self.move_by_val(node.end, between_all, 'R')
                    ret = self.copy_range(
                        node.end, between_bin,
                        node.start, between_all,
                        self.tm.default, empty,
                        'L'
                        )
                    between_all = between_all.union({ret.start, ret.end})
                    self.move_by_val(ret.start, between_all, 'L')

                    for child in node.children:
                        set_funcs(child, remember=True)

                    self.set_rule(self.val_alpha.pop(), self.cond_alpha.pop(), 'S')

    def __init__(self, tm: machine.TuringMachine):
        self.tm = tm
        self.cond_alpha = alphabetgenerator.AlphabetGenerator(gen=self.tm.condition)
        self.val_alpha = alphabetgenerator.AlphabetGenerator()
        self.val_alpha.reserved.update(val for val in self.tm.tape)

        self.stick_cond = self.tm.condition
        self.stick_val = self.tm.current

        self.cache = {}

    def copy_one(
            self, to: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """Copy one element from current to 'to',
        on_way_vals - values that will be on our way,
        direction - movement direction"""
        self.put_one(
            self.stick_val, to,
            on_way_vals, direction
            )

    def move_one(
            self, to: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """The same as copy_one except of
        the fact that it deletes original
        """
        val = self.stick_val
        self.clean_one()
        self.put_one(
            val, to,
            on_way_vals, direction
            )

    def put_one(
            self, val: str, to: str,
            on_way_vals: Iterable,
            direction
            ):
        """
        Put 'val' to 'to'
        """
        self.val_alpha.reserved.add(val)
        on_way_vals = set(on_way_vals)

        self.move_by_val(
            to, on_way_vals,
            direction
            )

        self.set_rule(val,
                      self.cond_alpha.pop(),
                      'S'
                      )

    def clean_one(self):
        """Set current cell to TuringMachine default value"""
        new_cond = self.cond_alpha.pop()

        self.set_rule(self.tm.default, new_cond, 'S')

        self.stick_val = self.tm.default
        self.stick_cond = new_cond

    def clean_range(
            self,
            start: str, end: str,
            on_way_vals: Iterable,
            direction='R'
            ):
        """Set all sector with TuringMachine default value
        it clears all area with start except of end val point
        if direction is left, than start is rightmost point
        """
        on_way_vals = set(on_way_vals)

        if self.stick_val != start:
            raise InvalidRegionError(
                f"(should start with {start} symbol, not with {self.stick_val})"
                )

        on_way_vals = on_way_vals.difference({end})
        on_way_vals = on_way_vals.union({start})

        new_cond = self.cond_alpha.pop()
        self.set_rule(self.tm.default, new_cond, direction)
        for val in on_way_vals:
            self.tm.set_rule(
                val, new_cond,
                self.tm.default, new_cond,
                direction
                )

        self.stick_val = end
        self.stick_cond = self.cond_alpha.pop()
        self.tm.set_rule(
            end, new_cond,
            end, self.stick_cond,
            'S'
            )

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
        """The same as copy_range, except that it uses
        clean_range on original range"""
        self.copy_range(
            start1, between1,
            end1, between12,
            start2, after2,
            direction
            )
        self.clean_range(start1, end1, between1, direction)
        self.move_by_val(start2, between12, direction)

    def copy_range(
            self,
            start1: str,
            between1: Iterable,
            end1: str,
            between12: Iterable,
            start2: str,
            after2: Iterable,
            direction
            ):
        """Copy range from [start1...end1] to [start2...],
        where ... is the range to copy
        """
        if self.stick_val != start1:
            raise InvalidRegionError(f"should start with {self.stick_val}, not with {start1}")

        between1 = set(between1).difference({start1, end1})
        between12 = set(between12).difference({end1, start2})
        after2 = set(after2).difference(start2)
        whole = between1.union(between12, after2, {start1, end1, start2})
        self.val_alpha.reserved.update(whole)

        opposite_direction = 'R' if direction == 'L' else 'L'

        main = tuple(self.cond_alpha.pop() for _ in range(7))
        copy_one = {key: self.cond_alpha.pop() for key in between1}

        stop_val = self.val_alpha.pop()
        stop_vals = {key: self.val_alpha.pop() for key in between1}

        """Setting up the stop sign after start2"""
        self.set_rule(self.stick_val, main[0], 'S')
        tempset = between1.union(between12, {start1, end1})
        for val in tempset:
            self.tm.set_rule(val, main[0], val, main[0], direction)
        self.tm.set_rule(start2, main[0], start2, main[1], direction)
        for val in after2:
            self.tm.set_rule(val, main[1], stop_val, main[1], opposite_direction)
        self.tm.set_rule(start2, main[1], start2, main[5], 'S')
        """Going back to start1 or stop by stop_vals"""
        tempset = between1.union(between12, {end1, start2})
        for val in tempset:
            self.tm.set_rule(val, main[5], val, main[5], opposite_direction)
        for val in stop_vals.values():
            self.tm.set_rule(val, main[5], val, main[2], direction)
        self.tm.set_rule(start1, main[5], start1, main[2], direction)

        """Copy depending on the symbol of between1 gained"""
        tempset = between1.union(between12, {end1, start2})
        for val in between1:
            next_val = stop_vals[val]
            next_cond = copy_one[val]
            self.tm.set_rule(
                val, main[2],
                next_val, next_cond,
                direction
                )
            for elem in tempset:
                self.tm.set_rule(elem, next_cond, elem, next_cond, direction)
            self.tm.set_rule(stop_val, next_cond, val, main[3], direction)
        for val in after2:
            self.tm.set_rule(val, main[3], stop_val, main[6], opposite_direction)

        """Get back and make a cycle"""
        for val in tempset:
            self.tm.set_rule(val, main[6], val, main[6], opposite_direction)
        for val in stop_vals.values():
            self.tm.set_rule(val, main[6], val, main[2], direction)

        """Clean when everything is done"""
        self.tm.set_rule(end1, main[2], end1, main[4], opposite_direction)

        def key_by_value(dictionary, value):
            for key in dictionary:
                if dictionary[key] == value:
                    return key

        for val in stop_vals.values():
            prev = key_by_value(stop_vals, val)
            self.tm.set_rule(val, main[4], prev, main[4], opposite_direction)

        self.stick_cond = self.cond_alpha.pop()
        self.tm.set_rule(start1, main[4], start1, self.stick_cond, 'S')
        self.stick_val = start1

    def move_by_val(
            self, val: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """Stops once val was encountered on the tape"""
        on_way_vals = set(on_way_vals)
        new_cond = self.cond_alpha.pop()

        on_way_vals = on_way_vals.difference(set(val))
        on_way_vals = on_way_vals.union(set(self.stick_val))

        self.set_rule(self.stick_val, new_cond, direction)

        for oval in on_way_vals:
            self.tm.set_rule(
                oval, new_cond,
                oval, new_cond,
                direction
                )

        self.stick_val = val  # to use next macro function
        self.stick_cond = self.cond_alpha.pop()  # we need to stick them together
        self.tm.set_rule(val, new_cond, val, self.stick_cond, 'S')  # stay to choose what to do next

    def stop(self):
        """
        Finish macro machine execution, every command after this function
        will be useless
        """
        print(self.stick_val, self.stick_cond)
        self.set_rule(self.stick_val, self.stick_cond, 'STOP')

    def bin_func(
            self,
            start_arg, end_arg,
            end_func, end_answ
            ):
        """Compute a value of a binary function, given a
        1. Vector of this function, bounded with arg_end and func_end values
        2. Arguments of this function, bounded with arg_start and arg_end values

        Example:
            [start_arg, '1', '0', end_arg, '1', '0', '1', '1', end_func] ->
            -> [start_arg, '1', '0', end_arg, '1', '0', {'1'}, '1', end_func, '1', end_answ],
            where {'1'} is point from where value of this function was copied
            and zero1, zero2, one1, one2 is temporary values
            cond_gen is template for generating conditions
        """
        if self.stick_val != start_arg:
            raise InvalidRegionError

        self.val_alpha.reserved.update([start_arg, end_arg, end_func, end_answ])

        zero1 = self.val_alpha.pop()
        zero2 = self.val_alpha.pop()
        one1 = self.val_alpha.pop()
        one2 = self.val_alpha.pop()

        cond_names = tuple(self.cond_alpha.pop() for _ in range(25))
        self.set_rule(self.stick_val, cond_names[0], 'S')

        file = self._parse_file(
            self.FUNC_BY_VECTOR_FILE,
            *cond_names, start_arg=start_arg,
            end_arg=end_arg, end_func=end_func,
            end_answ=end_answ, zero1=zero1,
            zero2=zero2, one1=one1, one2=one2,
            )

        try:
            self.tm.rule_file(file.name)
        finally:
            file.close()

        self.stick_cond = cond_names[-1]  # the last condition of this macro
        self.stick_val = start_arg  # the last value of this macro

    FUNC_BY_VECTOR_FILE = 'macro_func_by_vector.txt'

    @staticmethod
    def _parse_file(name, *args, **kwargs):
        """Function for creating files with current conditions and values
        made out of template files declared in this package"""
        with open(name) as file:
            s = ''
            for line in file:
                if not line.strip() or \
                        line.startswith('//'):
                    continue
                s += line

        s = s.format(*args, **kwargs)
        temp = tempfile.NamedTemporaryFile(prefix=name, suffix='_TuringMachineMacro', mode='w+t')
        temp.write(s)
        temp.seek(0)

        return temp
# TODO: add two binary numbers
# TODO: mul two binary numbers
# TODO: negation of a binary number
# TODO: n superposition

# TODO: optimizer of conditions
