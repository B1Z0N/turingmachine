from functools import partial

from turingmachine.machine import TuringMachine
from turingmachine.macro import Basic


def tm_equal(
        tm1: TuringMachine,
        tm2: TuringMachine
        ):
    assert tm1.tape == tm2.tape
    assert tm1.index == tm2.index


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
        print(self.bsc.tm)
        assert self.bsc.stick_val == 'b'
        assert self.bsc.stick_cond == 'q5'


class TemplateFuncMacroTesting:
    """
    Class for common setup of all
    macro function classes
    """

    def setup_class(self, string):
        tm = TuringMachine.from_str(string)
        self.bsc = Basic(tm)


class TestMoveByVal(TemplateFuncMacroTesting):
    def setup_class(self):
        super().setup_class("")

    def test_main(self):
        pass

    def test_prepare(self):

    def test__main_move(self):
        self.

    def test_reuse(self):
        pass

    def test_create(self):
        pass
