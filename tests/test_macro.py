from functools import partial

import turingmachine.macro as macro
from turingmachine.machine import TuringMachine
from turingmachine.macro import Basic, MoveByVal


def tm_equal(
        tm1: TuringMachine,
        tm2: TuringMachine
        ):
    assert tm1.tape == tm2.tape
    assert tm1.index == tm2.index


def tmac_equal(
        tmac1: Basic,
        tmac2: Basic
        ):
    tm_equal(tmac1.tm, tmac2.tm)

    assert tmac1.stick_cond == tmac2.stick_cond
    assert tmac1.stick_val == tmac2.stick_val
    assert tmac1.cond_alpha == tmac2.cond_alpha

    assert tmac1.val_alpha == tmac2.val_alpha

def func_for_testing(cls, function_name, state, state2, *args, **kwargs):
    tm = TuringMachine.from_str(state)
    tm2 = TuringMachine.from_str(state2)
    tmac = cls(tm)
    getattr(tmac, function_name)(*args, **kwargs)
    tmac.stop()
    tm.run()
    tm.view()
    tm_equal(tm, tm2)


basic_func_for_testing = partial(func_for_testing, Basic)


class TestBasic:
    def setup_class(self):
        tm = TuringMachine.from_str("a,b,c:::q1:")
        self.bsc = Basic(tm)

    def test_set_rule(self):
        test = partial(basic_func_for_testing, "set_rule")

        test("a,b,c:::q1:", "s,b,c:1::q2:",  # two states first and final
             's', self.bsc.cond_alpha.pop(), 'R', suppose_val='b'  # args for function
             )

        test("a,b,c:::q1:", "s,b,c:::q3:",  # two states first and final
             's', self.bsc.cond_alpha.pop(), 'S'  # args for function
             )

        self.bsc.set_rule('s', self.bsc.cond_alpha.pop(), 'R', suppose_val='b')
        assert self.bsc.stick_cond == 'q4'
        assert self.bsc.stick_val == 'b'

        self.bsc.set_rule(self.bsc.stick_val, self.bsc.cond_alpha.pop(), 'S')
        assert self.bsc.stick_cond == 'q5'
        assert self.bsc.stick_val == 'b'

    def test_stop(self):
        self.bsc.stop()
        self.bsc.tm.run()
        assert self.bsc.stick_val == 'b'
        assert self.bsc.stick_cond == 'q5'


def prepare_class(obj, string, cls):
    tm = TuringMachine.from_str(string)
    obj.bsc = cls(tm)


def reset_to_class_setup(string=None):
    def f(func):
        def _(*args, **kwargs):
            res = func(*args, **kwargs)
            self = args[0]
            self.setup_class(string)

            return res

        return _

    return f


class TestMoveByVal:

    TESTSTRING1 = "1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:"

    def setup_class(self, string=None):
        class Kek(Basic):
            move = MoveByVal()

        string = "1,0,0,0,1,1,0,b:::q1:" if string is None else string
        """In case of calling from pytest, not from internal functions"""
        prepare_class(self, string, Kek)

    def test_main(self):
        self.setup_class('3,a,' + self.TESTSTRING1)

        lst = ['3']
        self.bsc.set_rule('3', self.bsc.cond_alpha.pop(), 'R', suppose_val='a')
        cond = self.bsc.cond_alpha.pop()
        cond2 = self.bsc.cond_alpha.pop()
        end_cond = self.bsc.cond_alpha.pop()
        print(cond, cond2, end_cond)
        for i in reversed(range(1, 3)):
            self.bsc.move('b', ['0', '1'], 'R', cycle=True)
            self.bsc.move('a', ['0', '1'], 'L', cycle=True)
            self.bsc.set_rule('a', cond, 'L', suppose_val=str(i + 1))
            if i > 1:
                self.bsc.set_rule(str(i), cond2, 'R', suppose_val='a')
            else:
                self.bsc.set_rule(str(i), end_cond, 'R', suppose_val='a')

        self.bsc.stop()
        print(self.bsc.tm)
        self.bsc.tm.run()

    @reset_to_class_setup(TESTSTRING1)
    def test_prepare(self):
        args = 'b', {'1', '0'}, 'R'
        self.bsc.move.prepare(*args)
        assert self.bsc.move.cur_case is None
        assert self.bsc.move.args == ('b', {'1', '0'}, 'R')

        val, on_way_vals, direction = args
        params = macro.Params(({val}, on_way_vals, direction), {})
        conds = macro.MoveByVal.MoveByValConds(move_cond='q1', end_cond='q2')

        cur_case = macro.MacroCase(conds, params)
        self.bsc.move.cases = [cur_case]
        self.bsc.move.cur_index = 0

        self.bsc.move.prepare('c', {'1', '0', 'o', 't'}, 'R')
        assert self.bsc.move.cur_case == cur_case
        assert self.bsc.move.args == ('c', {'1', '0', 'o', 't'}, 'R', False)

    def test__main_move(self):
        self.setup_class()
        self.bsc.move._main_move(
            'b', ('1', '0'), 'R'
            )
        self.bsc.stop()
        self.bsc.tm.run()

        self.bsc.tm.view()
        tm2 = TuringMachine.from_str("1,0,0,0,1,1,0,b:7::q2:")
        tmac2 = Basic(tm2)
        tmac2.cond_alpha.reserved.add('q1')
        tmac_equal(self.bsc, tmac2)

    def test_create(self):
        self.setup_class(self.TESTSTRING1)
        args = 'b', {'0', '1'}, 'R'
        self.bsc.move.create(*args)

        params = macro.Params(({'b'}, {'0', '1'}, 'R'), {})
        conds = macro.MoveByVal.MoveByValConds(move_cond='q1', end_cond='q2')

        cur_case = macro.MacroCase(conds, params)

        assert self.bsc.move.cases == [cur_case]

    def test_reuse(self):
        args = 'c', {'0', '1', 'o', 't'}, 'R', False
        self.bsc.move.reuse(*args)

        params = macro.Params(({'b', 'c'}, {'0', '1', 'o', 't'}, 'R'), {})
        conds = macro.MoveByVal.MoveByValConds(move_cond='q1', end_cond='q2')

        cur_case = macro.MacroCase(conds, params)

        assert self.bsc.move.cases == [cur_case]
