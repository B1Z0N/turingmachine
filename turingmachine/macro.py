""""Class for adding basic functionality for
writing programs with TuringMachine class,
main class in this module is TuringMachineMacro"""

import tempfile
from collections import namedtuple
from collections.abc import Iterable

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
MacroFunction = namedtuple("MacroFunction", "name start_cond end_cond")


def return_macro_info(func):
    def _(*args, **kwargs):
        self = args[0]

        start_cond = self.stick_cond
        ret = func(*args, **kwargs)
        name = func.__name__
        name = name[0].upper() + name[1:]

        ret2 = MacroFunction(name, start_cond, self.stick_cond)
        if ret is None:
            return ret2
        else:
            return ret2, ret

    return _


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

    @return_macro_info
    def set_all_on_way(
            self, from_to: dict,
            on_way_vals: Iterable,
            stop_val,
            direction
            ):

        on_way_vals = set(on_way_vals)
        on_way_vals = on_way_vals.difference(from_to.keys(), {stop_val})

        for val in on_way_vals:
            self.tm.set_rule(
                val, self.stick_cond,
                val, self.stick_cond,
                direction
                )
        for _from, _to in from_to.items():
            self.tm.set_rule(_from, self.stick_cond, _to, self.stick_cond, direction)
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

    @return_macro_info
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

    @return_macro_info
    def move_one(
            self, to: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """The same as copy_one except of
        the fact that it deletes original
        """
        start_cond = self.stick_cond
        val = self.stick_val
        self.clean_one()
        self.put_one(
            val, to,
            on_way_vals, direction
            )

    @return_macro_info
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

    @return_macro_info
    def clean_one(self):
        """Set current cell to TuringMachine default value"""
        new_cond = self.cond_alpha.pop()

        self.set_rule(self.tm.default, new_cond, 'S')

    @return_macro_info
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

    @return_macro_info
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

    @return_macro_info
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

    @return_macro_info
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

    @return_macro_info
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


"""class TuringMachineGenFuncVecMacro(TuringMachineMacro):

    def is_equal_funcs(self, node1, node2):
        if node1.is_leaf and node2.is_leaf:
            return node1.name == node2.name
        else:
            if len(node1.children) != len(node2.children):
                return False
            return all(
                TuringMachineGenFuncVecMacro.is_equal_funcs(child1, child2)
                for child1, child2
                in zip(node1.children, node2.children)
                ) and node1.name == node2.name

    def get_func_and_args(self, tree):
        args = set()
        funcs = set()
        for elem in anytree.PostOrderIter(tree):
            if elem.is_leaf:
                args.add(elem.name)
            else:
                if any(
                        TuringMachineGenFuncVecMacro.is_equal_funcs(
                                node, elem
                                )
                        for node in funcs
                        ):
                    continue
                else:
                    funcs.add(elem)
        funcs = {elem.name for elem in funcs}
        return funcs, args

    def set_marker(self, marker):

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

    def prepare_results(self):
        self.set_marker(blank)
        self.set_marker(blank)
        res_val = self.val_alpha.pop()
        self.set_marker(res_val)

        return res_val

    def run_children(self, node):
        postponed = []
        for child in node.children:
            it = self.set_funcs_generator(child)
            next(it)
            if isinstance(child.name, BinaryFunctionVector):
                postponed.append(it)

        return postponed

    def run_postponed(self, postponed):
        for post in postponed:
            next(post)

        def set_funcs_generator(self, node):
            nonlocal first, before_vecs, between_all
            nonlocal blank, self, default, bin_vals

            if node.is_leaf:
                self.set_marker(symbols_for_args[node.name])
                yield
            else:
                vec = node.name
                if first is not True:
                    self.set_marker(symbols_for_funcs[vec])
                    yield
                else:
                    first = False

                res_val = self.prepare_results()  # place markers where results will be displayed
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
                postponed = self.run_children(node)

                self.set_marker(self.val_alpha.pop())
                self.run_postponed(postponed)

        def run_none_returning_generator(self, func):
            import types

            def _(*args, **kwargs):
                it = func(*args, **kwargs)
                if not isinstance(it, types.GeneratorType):
                    raise TypeError(repr(it) + "must be a generator")
                while True:
                    try:
                        next(it)
                    except StopIteration:
                        break

            return _

        set_funcs = run_none_returning_generator(set_funcs_generator)

    def put_args_gen(self):
        nonlocal self, args
        numbers = 2 ** len(args)
        cur_val = self.stick_val
        self.set_rule(self.stick_val, self.stick_cond, 'L', suppose_val=default)
        self.set_rule(str(numbers), self.cond_alpha.pop(), 'S')

        def set_args(self):
            nonlocal self, args, symbols_for_args

            numbers = self.stick_val

            def mybin(num, length):
                res = bin(num)[2:]
                return (length - len(res)) * '0' + res

            arg_num = len(args)
            cur_bin = mybin(int(numbers), arg_num)
            from_to = {symbols_for_args[arg]: num for arg, num in zip(args, cur_bin)}
            tempset = between_all.union(bin_vals, {numbers})

            self.set_all_on_way(from_to, tempset, vecs_start, 'R')
            self.move_by_val(numbers, tempset, 'L')

    def gen_func_vec(
            self,
            func_tree: anytree.Node
            ):

        funcs, args = self.get_func_and_args(func_tree)

        for function in funcs:
            self.val_alpha.reserved.union({function.start, function.end})

        symbols_for_args = {arg: self.val_alpha.pop() for arg in args}
        symbols_for_funcs = {func: self.val_alpha.pop() for func in funcs}

        vecs_start = self.stick_val
        blank = self.val_alpha.pop()  # symbol for blank spaces for future function results
        before_vecs = {blank}
        between_all = {blank}
        default = self.tm.default
        bin_vals = {'1', '0'}
        first = True
        after_vecs = {val for func in funcs for val in (func.start, func.end)}

        self.set_funcs(func_tree)
        self.put_args_gen()
        self.set_args()

# TODO: add two binary numbers
# TODO: mul two binary numbers
# TODO: negation of a binary number
# TODO: n superposition

# TODO: optimizer of conditions

"""
