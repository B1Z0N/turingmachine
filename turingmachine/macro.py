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


BinaryFunctionVector = namedtuple("BinaryFunctionVector", "start end")


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
        def is_equal_funcs(node1, node2):
            if node1.is_leaf and node2.is_leaf:
                return node1.name == node2.name
            else:
                if len(node1.children) != len(node2.children):
                    return False
                return all(
                    is_equal_funcs(child1, child2) for child1, child2
                    in zip(node1.children, node2.children)
                    ) and node1.name == node2.name

        def get_func_and_args(tree):
            args = set()
            funcs = set()
            for elem in anytree.PostOrderIter(tree):
                if elem.is_leaf:
                    args.add(elem.name)
                else:
                    if any(
                            is_equal_funcs(
                                node, elem
                                )
                            for node in funcs
                            ):
                        continue
                    else:
                        funcs.add(elem)

            funcs = {elem.name for elem in funcs}

            return funcs, args

        funcs, args = get_func_and_args(func_tree)

        for function in funcs:
            self.val_alpha.reserved.union({function.start, function.end})

        symbols_for_args = {arg: self.val_alpha.pop() for arg in args}
        symbols_for_funcs = {func: self.val_alpha.pop() for func in funcs}

        blank = self.val_alpha.pop()  # symbol for blank spaces for future function results
        before_vecs = {blank}
        between_all = {blank}
        default = self.tm.default
        bin_vals = {'1', '0'}
        first = True
        after_vecs = {val for func in funcs for val in (func.start, func.end)}

        def set_funcs(node):
            nonlocal first, before_vecs, between_all
            nonlocal blank, self, default, bin_vals

            def set_marker(marker):
                """Function used for setting argument names in
                binary function arguments place
                """
                self.set_rule(
                    self.stick_val, self.stick_cond,
                    'L', suppose_val=default
                    )
                self.set_rule(
                    marker, self.cond_alpha.pop(),
                    'S'
                    )

                between_all.add(marker)
                before_vecs.add(marker)

            def prepare_results():
                nonlocal blank
                set_marker(blank)
                set_marker(blank)
                res_val = self.val_alpha.pop()
                set_marker(res_val)

                return res_val

            def run_children(node):
                postponed = []
                for child in node.children:
                    it = set_funcs(child)
                    next(it)
                    if isinstance(child.name, BinaryFunctionVector):
                        postponed.append(it)

                return postponed

            def run_postponed(postponed):
                for post in postponed:
                    next(post)

            if node.is_leaf:
                set_marker(symbols_for_args[node.name])
                yield
            else:
                vec = node.name
                if first is not True:
                    set_marker(symbols_for_funcs[vec])
                    yield
                else:
                    first = False

                res_val = prepare_results()  # place markers where results will be displayed
                #  res_val is the very left point of the tape

                move_set = between_all.union(bin_vals, after_vecs)
                self.move_by_val(vec.end, move_set, 'R')

                copy_res = self.copy_range(
                    vec.end, bin_vals, vec.start,
                    move_set, res_val, [default],
                    'L'
                    )

                between_all.add(copy_res.start)
                self.move_by_val(copy_res.start, move_set, 'L')
                postponed = run_children(node)

                set_marker(self.val_alpha.pop())
                run_postponed(postponed)

        it = set_funcs(func_tree)
        while True:
            try:
                next(it)
            except StopIteration:
                break

    def set_all_on_way(
            self, from_val, to_val,
            on_way_vals: Iterable, stop_val,
            direction
            ):
        on_way_vals = set(on_way_vals)
        on_way_vals = on_way_vals.difference({from_val, stop_val})

        for val in on_way_vals:
            self.tm.set_rule(
                val, self.stick_cond,
                val, self.stick_cond,
                direction
                )
        self.tm.set_rule(from_val, self.stick_cond, to_val, self.stick_cond, direction)
        ret_cond = self.cond_alpha.pop()
        self.tm.set_rule(stop_val, self.stick_cond, stop_val, ret_cond, 'S')

        self.stick_val = stop_val
        self.stick_cond = ret_cond

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
                f"(symbols {start}, {self.stick_val} not equal)"
                )

        on_way_vals = on_way_vals.difference({end})
        on_way_vals = on_way_vals.union({start})

        self.set_rule(self.tm.default, self.stick_cond, direction)
        for val in on_way_vals:
            self.tm.set_rule(
                val, self.stick_cond,
                self.tm.default, self.stick_cond,
                direction
                )

        self.stick_val = end
        new_cond = self.cond_alpha.pop()
        self.tm.set_rule(
            end, self.stick_cond,
            end, new_cond,
            'S'
            )
        self.stick_cond = new_cond

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
        ret = self.copy_range(
            start1, between1,
            end1, between12,
            start2, after2,
            direction
            )
        self.clean_range(start1, end1, between1, direction)

        return ret

    def copy_range(  # rewrite it with some glue in my head
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
        between12 = set(between12).difference({end1, start2, start1})
        after2 = set(after2).difference(start2)
        whole = between1.union(between12, after2, {start1, end1, start2})
        self.val_alpha.reserved.update(whole)

        opposite_direction = 'R' if direction == 'L' else 'L'

        main = tuple(self.cond_alpha.pop() for _ in range(7))
        copy_one = {key: self.cond_alpha.pop() for key in between1}

        stop_val = self.val_alpha.pop()
        stop_vals = {key: self.val_alpha.pop() for key in between1}

        """Setting up the stop sign after start2"""
        tempset = between1.union(between12, {start1, end1})
        for val in tempset:
            self.tm.set_rule(val, self.stick_cond, val, self.stick_cond, direction)
        self.tm.set_rule(start2, self.stick_cond, start2, main[0], direction)
        for val in after2:
            self.tm.set_rule(val, main[0], stop_val, main[0], opposite_direction)
        self.tm.set_rule(start2, main[0], start2, main[4], 'S')
        """Going back to start1 or stop by stop_vals"""
        tempset = between1.union(between12, {end1, start2})
        for val in tempset:
            self.tm.set_rule(val, main[4], val, main[4], opposite_direction)
        for val in stop_vals.values():
            self.tm.set_rule(val, main[4], val, main[1], direction)
        self.tm.set_rule(start1, main[4], start1, main[1], direction)

        """Copy depending on the symbol of between1 gained"""
        tempset = between1.union(between12, {end1, start2})
        for val in between1:
            next_val = stop_vals[val]
            next_cond = copy_one[val]
            self.tm.set_rule(
                val, main[1],
                next_val, next_cond,
                direction
                )
            for elem in tempset:
                self.tm.set_rule(elem, next_cond, elem, next_cond, direction)
            self.tm.set_rule(stop_val, next_cond, val, main[2], direction)
        for val in after2:
            self.tm.set_rule(val, main[2], stop_val, main[5], opposite_direction)

        """Get back and make a cycle"""
        for val in tempset:
            self.tm.set_rule(val, main[5], val, main[5], opposite_direction)
        for val in stop_vals.values():
            self.tm.set_rule(val, main[5], val, main[1], direction)

        """Clean when everything is done"""
        self.tm.set_rule(end1, main[1], end1, main[3], opposite_direction)

        def key_by_value(dictionary, value):
            for key in dictionary:
                if dictionary[key] == value:
                    return key

        for val in stop_vals.values():
            prev = key_by_value(stop_vals, val)
            self.tm.set_rule(val, main[3], prev, main[3], opposite_direction)

        self.stick_cond = self.cond_alpha.pop()
        self.tm.set_rule(start1, main[3], start1, self.stick_cond, 'S')
        self.stick_val = start1

        CopyRange = namedtuple("CopyRange", "start end")
        if direction == 'L':
            start2, stop_val = stop_val, start2

        return CopyRange(start2, stop_val)

    def move_by_val(
            self, val: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """Stops once val was encountered on the tape"""
        on_way_vals = set(on_way_vals)

        on_way_vals = on_way_vals.difference(set(val))
        on_way_vals = on_way_vals.union(set(self.stick_val))

        self.set_rule(self.stick_val, self.stick_cond, direction)

        for oval in on_way_vals:
            self.tm.set_rule(
                oval, self.stick_cond,
                oval, self.stick_cond,
                direction
                )

        self.stick_val = val
        self.set_rule(val, self.cond_alpha.pop(), 'S')

    def stop(self):
        """
        Finish macro machine execution, every command after this function
        will be useless
        """
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

        cond_names = [self.stick_cond]
        cond_names += [self.cond_alpha.pop() for _ in range(25)]

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