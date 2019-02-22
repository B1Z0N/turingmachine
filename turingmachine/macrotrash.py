""""Class for adding basic functionality for
writing programs with TuringMachine class,
main class in this module is TuringMachineMacro"""

import functools
import re
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


class MoveByVal(Basic):
    def move_by_val(
            self, val: str,
            on_way_vals: Iterable,
            direction: str,
            cycle=False
            ):
        self._is_reusable_move_by_val()

    def _new_move_by_val(
            self, val: str,
            on_way_vals: Iterable,
            direction: str
            ):
        """Stops once val was encountered on the tape"""
        self.set_rule(self.stick_val, self.stick_cond, direction)

        for oval in on_way_vals:
            self.tm.set_rule(
                oval, self.stick_cond,
                oval, self.stick_cond,
                direction
                )

        self.stick_val = val
        self.set_rule(val, self.cond_alpha.pop(), 'S')

        return namedtuple("MoveByValRet", "start_cond end_cond")

    def _reuse_move_by_val(self, conds, val, on_way_vals, direction):


class SetAllOnWay:
    def set_all_on_way(
            self, from_to: dict,
            on_way_vals: Iterable,
            stop_val,
            direction,
            cycle=False
            ):
        _decide_set_all_on_way()

    def _prepare_set_all_on_way(self):

    def _decide_set_all_on_way(
            self, from_to: dict,
            on_way_vals: Iterable,
            stop_val,
            direction
            ):
        pass

    def _new_set_all_on_way(
            self, from_to: dict,
            on_way_vals: Iterable,
            stop_val,
            direction
            ):
        start = self.stick_cond

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

        return namedtuple("PutAllOnWay", "move_cond stop_cond")(start, ret_cond)

    def _decide_set_all_on_way(self,  # TODO: staticmethod support in MacroReuseA
                               case, from_to: dict,
                               on_way_vals: Iterable,
                               stop_val,
                               direction,
                               ):
        on_way_vals = set(on_way_vals).difference(from_to.keys(), {stop_val})

        args, kwargs = case
        from_to1, on_way_vals1, stop_val1, direction1 = args

        def one_way_dicts_comparison(d1, d2):
            s1 = set(d1.items())
            s2 = set(d2.items())
            return s1.issubset(s2) or s1.isdisjoint(s2)

        return not any(
            (
                direction != direction1,
                stop_val != stop_val1,
                # stop_val1 in on_way_vals,
                # stop_val in on_way_vals1,
                # stop_val in from_to1.keys(),
                # stop_val in from_to1.values(),
                # stop_val1 in from_to.keys(),
                # stop_val1 in from_to.values()
                )
            ) and one_way_dicts_comparison(from_to1, from_to)

    def _reuse_set_all_on_way(
            self, case,
            from_to: dict,
            on_way_vals: Iterable,
            stop_val,
            direction
            ):

        on_way_vals = set(on_way_vals)
        on_way_vals = on_way_vals.difference(from_to.keys(), {stop_val})

        ret, args, _ = case
        from_to1, on_way_vals1, stop_val1, direction1 = args

        move_set = on_way_vals.difference(on_way_vals1)
        from_to_dict = dict(set(from_to.items()).difference(set(from_to1.items())))
        move_cond = ret.move_cond

        self.set_rule(self.stick_val, move_cond, 'S')

        for val in move_set:
            self.tm.set_rule(
                val, move_cond,
                val, move_cond,
                direction
                )

        for _from, _to in from_to_dict.items():
            self.tm.set_rule(
                _from, move_cond,
                _to, move_cond,
                direction
                )

        self.stick_val = stop_val
        self.stick_cond = ret.stop_cond

        from_to = dict(set(from_to.items()).union(from_to1.items()))
        on_way_vals = on_way_vals.union(on_way_vals1)

        args = from_to, on_way_vals, stop_val, direction
        kwargs = {}

        return ret, args, kwargs


BinaryFunctionVector = namedtuple("BinaryFunctionVector", "start end")
MacroFunction = namedtuple("MacroFunction", "name start_cond end_cond")


class Decision:
    def __init__(self, reuse: bool, args, kwargs=None):
        self.reuse = reuse
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}


class MacroReuse:

    def __init__(
            self, f_create=None, f_reuse=None,
            f_decide=None
            ):
        if f_create is None or f_reuse is None:
            raise ValueError("Must pass some parameters, not None")

        if f_decide is not None:
            self.decide = f_decide
        else:
            self.decide = self.default_decide

        self.create = f_create
        self.reuse = f_reuse
        self.cases = []

    @staticmethod
    def default_decide(_, case, *args, **kwargs):
        return Decision((args, kwargs) == case, args, kwargs)

    @staticmethod
    def tup_to_decision(tup):
        return Decision(*tup)

    def prepare(self, obj, *args, **kwargs):
        res = Decision(*self.decide(obj, None, *args, **kwargs))
        it = None
        reuse = None
        for case in self.cases:
            it = self.decide(obj, case, *args, **kwargs)
            reuse = next(it)
            if reuse:
                res = Decision(reuse, *it)
                break

        if it is not None:
            if reuse is False:
                res = Decision(reuse, *it)

        return res

    def __call__(self, obj, *args, **kwargs):

        res = self.prepare(obj, *args, **kwargs)

        if res.reuse is True:
            self.reuse(obj, *res.args, **res.kwargs)
        else:
            self.create(obj, *res.args, **res.kwargs)
            self.cases.append((res.args, res.kwargs))

    def __get__(self, obj, cls):
        func = functools.partial(self.__call__, obj)
        return func


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

    set_all_on_way = MacroReuse(_new_set_all_on_way, _reuse_set_all_on_way, _is_reusable_set_all_on_way)

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

        def prepare():
            nonlocal between1, between12, after2

            if self.stick_val != start1:
                raise InvalidRegionError(f"should start with {self.stick_val}, not with {start1}")

            between1 = set(between1).difference({start1, end1})
            between12 = set(between12).difference({end1, start2, start1})
            after2 = set(after2).difference(start2)
            whole = between1.union(between12, after2, {start1, end1, start2})
            self.val_alpha.reserved.update(whole)

        def setup_stop_sign():
            tempset = between1.union(between12, {start1, end1})
            for val in tempset:
                self.tm.set_rule(val, self.stick_cond, val, self.stick_cond, direction)
            self.tm.set_rule(start2, self.stick_cond, start2, main[0], direction)
            for val in after2:
                self.tm.set_rule(val, main[0], stop_val, main[0], opposite_direction)
            self.tm.set_rule(start2, main[0], start2, main[4], 'S')

        def go_back():
            tempset = between1.union(between12, {end1, start2})
            for val in tempset:
                self.tm.set_rule(val, main[4], val, main[4], opposite_direction)
            for val in stop_vals.values():
                self.tm.set_rule(val, main[4], val, main[1], direction)
            self.tm.set_rule(start1, main[4], start1, main[1], direction)

        def copy_symbol():
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

        def cycle_it():
            tempset = between1.union(between12, {end1, start2})
            for val in tempset:
                self.tm.set_rule(val, main[5], val, main[5], opposite_direction)
            for val in stop_vals.values():
                self.tm.set_rule(val, main[5], val, main[1], direction)

        def clean_done():
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

        """Preparing variables"""
        prepare()

        opposite_direction = 'R' if direction == 'L' else 'L'

        main = tuple(self.cond_alpha.pop() for _ in range(7))
        copy_one = {key: self.cond_alpha.pop() for key in between1}

        stop_val = self.val_alpha.pop()
        stop_vals = {key: self.val_alpha.pop() for key in between1}

        """Setting up the stop sign after start2"""
        setup_stop_sign()
        """Going back to start1 or stop by stop_vals"""
        go_back()
        """Copy depending on the symbol of between1 gained"""
        copy_symbol()
        """Get back and make a cycle"""
        cycle_it()
        """Clean when everything is done"""
        clean_done()

        CopyRange = namedtuple("CopyRange", "start end")
        if direction == 'L':
            start2, stop_val = stop_val, start2

        return CopyRange(start2, stop_val)

    @return_macro_info
    def bin_func(
            self,
            start_arg_lst, end_arg_lst,
            end_func_lst, end_answ_lst
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
        if self.stick_val != start_arg_lst:
            raise InvalidRegionError

        start_arg = self.stick_val
        self.val_alpha.reserved.update([start_arg_lst, end_arg_lst, end_func_lst, end_answ_lst])

        zero1 = self.val_alpha.pop()
        zero2 = self.val_alpha.pop()
        one1 = self.val_alpha.pop()
        one2 = self.val_alpha.pop()

        cond_names = [self.stick_cond]
        cond_names += [self.cond_alpha.pop() for _ in range(25)]

        file = self._parse_file(
            self.FUNC_BY_VECTOR_FILE,
            *cond_names, start_arg=start_arg_lst,
            end_arg=end_arg_lst, end_func=end_func_lst,
            end_answ=end_answ_lst, zero1=zero1,
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
    def _gen_list_parametrs(s, kwargs):
        del_lst = []
        add_lst = []
        str_lst = set(s.splitlines())
        for kw, val in kwargs.items():
            if kw.endswith("_lst"):
                sch = kw[:-4]
                amount = len(val)

                reg = re.compile(f"({{{sch})(}})")
                del_set = set()
                add_set = set()
                for string in str_lst:
                    start_len = len(add_set)
                    for num in range(amount):
                        add_set.add(
                            re.sub(reg, lambda m: m.group(1) + str(num) + m.group(2), string)
                            )
                    if start_len != len(add_set):
                        del_set.add(string)

                str_lst = str_lst.difference(del_set).union(add_set)

                del_lst.append(kw)
                for num, value in enumerate(val):
                    add_lst.append((sch + str(num), value))

        for i in del_lst:
            del kwargs[i]
        kwargs.update(add_lst)

        return "\n".join(str_lst)

    def _parse_file(self, name, *args, **kwargs):
        """Function for creating files with current conditions and values
        made out of template files declared in this package"""

        with open(name) as file:
            s = ''
            for line in file:
                if not line.strip() or \
                        line.startswith('//'):
                    continue
                s += line

        #  s = self._gen_list_parametrs(s, kwargs)
        s = s.format(*args, **kwargs)
        temp = tempfile.NamedTemporaryFile(prefix=name, suffix='_TuringMachineMacro', mode='w+t')
        temp.write(s)
        temp.seek(0)

        return temp


def run_none_returning_generator(func):
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


class TuringMachineGenFuncVecMacro(TuringMachineMacro):

    def __init__(self, vec_tree, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cur_node = self.vec_tree = vec_tree
        self.between_all = []
        self.before_vecs = []

        self.funcs, self.args = self.get_func_and_args(self.vec_tree)

        for function in self.funcs:
            self.val_alpha.reserved.union({function.start, function.end})

        self.symbols_for_args = {arg: self.val_alpha.pop() for arg in self.args}
        self.symbols_for_funcs = {func: self.val_alpha.pop() for func in self.funcs}

        self.vecs_start = self.stick_val
        blank = self.val_alpha.pop()  # symbol for blank spaces for future function results
        self.before_vecs = {blank}
        self.between_all = {blank}
        self.bin_vals = {'1', '0'}
        self.first = True
        self.after_vecs = {val for func in self.funcs for val in (func.start, func.end)}
        self.blank = self.val_alpha.pop()

    @staticmethod
    def _is_equal_funcs(node1, node2):
        if node1.is_leaf and node2.is_leaf:
            return node1.name == node2.name
        else:
            if len(node1.children) != len(node2.children):
                return False
            return all(
                TuringMachineGenFuncVecMacro._is_equal_funcs(child1, child2)
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
                        TuringMachineGenFuncVecMacro._is_equal_funcs(
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
            'L', suppose_val=self.tm.default
            )
        self.set_rule(
            marker, self.cond_alpha.pop(),
            'S'
            )

        self.between_all.add(marker)
        self.before_vecs.add(marker)

    def prepare_results(self):
        self.set_marker(self.blank)
        self.set_marker(self.blank)
        res_val = self.val_alpha.pop()
        self.set_marker(res_val)

        return res_val

    def run_children(self, node):
        postponed = []
        for child in node.children:
            self.cur_node = child
            it = self.set_funcs_generator()
            next(it)
            if isinstance(child.name, BinaryFunctionVector):
                postponed.append(it)

        return postponed

    def run_postponed(self, postponed):
        for post in postponed:
            next(post)

    def set_funcs_generator(self):
        self.first = True
        node = self.cur_node

        if node.is_leaf:
            self.set_marker(self.symbols_for_args[node.name])
            yield
        else:
            vec = node.name
            if self.first is not True:
                self.set_marker(self.symbols_for_funcs[vec])
                yield
            else:
                self.first = False
            res_val = self.prepare_results()  # place markers where results will be displayed
            #  res_val is the very left point of the tape
            move_set = self.between_all.union(self.bin_vals, self.after_vecs)
            self.move_by_val(vec.end, move_set, 'R')
            copy_res = self.copy_range(
                vec.end, self.bin_vals, vec.start,
                move_set, res_val, [self.tm.default],
                'L'
                )
            self.between_all.add(copy_res.start)
            self.move_by_val(copy_res.start, move_set, 'L')
            postponed = self.run_children(node)
            self.set_marker(self.val_alpha.pop())
            self.run_postponed(postponed)

    set_funcs = run_none_returning_generator(set_funcs_generator)

    def put_args_gen(self):
        numbers = 2 ** len(self.args)
        cur_val = self.stick_val
        self.set_rule(self.stick_val, self.stick_cond, 'L', suppose_val=self.tm.default)
        self.set_rule(str(numbers), self.cond_alpha.pop(), 'S')

    def set_args(self):
        numbers = self.stick_val

        def mybin(num, length):
            res = bin(num)[2:]
            return (length - len(res)) * '0' + res

        arg_num = len(self.args)
        cur_bin = mybin(int(numbers), arg_num)
        from_to = {self.symbols_for_args[arg]: num for arg, num in zip(self.args, cur_bin)}
        tempset = self.between_all.union(self.bin_vals, {numbers})
        self.set_all_on_way(from_to, tempset, self.vecs_start, 'R')
        self.move_by_val(numbers, tempset, 'L')

    def gen_func_vec(self):
        self.set_funcs(self.vec_tree)
        self.put_args_gen()
        self.set_args()

# TODO: add two binary numbers
# TODO: mul two binary numbers
# TODO: negation of a binary number
# TODO: n superposition

# TODO: optimizer of conditions
