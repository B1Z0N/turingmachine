from functools import partial

import turingmachine.macro as macro
from turingmachine.machine import TuringMachine
from turingmachine.macro import MacroSticks, Basic, MoveByVal, Macro, NextCondition

class TestMacroSticks:
    def test_set(self):
        self.sticks = MacroSticks('a', 'q1')
        assert self.sticks.is_sin_val_cond()
        assert self.sticks.get_conds() == "q1"
        assert self.sticks.get_values() == "a"

        val_cond = ['1', '2', '3'], ['q1', 'q2', 'q3']
        self.sticks.set(*val_cond)
        assert self.sticks.is_mul_val_cond()
        assert self.sticks.get() == val_cond
        assert self.sticks.get_conds() == val_cond[1]
        assert self.sticks.get_values() == val_cond[0]

        self.sticks.set('2', val_cond[1])
        assert self.sticks.is_sin_val_mul_cond()
        assert self.sticks.get() == ('2', val_cond[1])
        assert self.sticks.get_conds() == val_cond[1]
        assert self.sticks.get_values() == '2'

        try:
            self.sticks.set('123')  # erroneous behaviour
        except MacroSticks.StickError:
            print("Everything is ok")
        else:
            raise AssertionError

        try:
            self.sticks.set('123', TuringMachine.from_str('1,0,1,0:::q1:'))  # erroneous behaviour
        except MacroSticks.StickError:
            print("Everything is ok")
        else:
            raise AssertionError


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
    assert tmac1.val_cond.get() == tmac2.val_cond.get()

    assert tmac1.cond_alpha == tmac2.cond_alpha
    assert tmac1.val_alpha == tmac2.val_alpha


def func_for_testing(cls, function_name):
    def _(state, state2, *args, **kwargs):
        tm = TuringMachine.from_str(state)
        tm2 = TuringMachine.from_str(state2)
        tmac = cls(tm)
        getattr(tmac, function_name)(*args, **kwargs)
        tmac.stop()
        tm.run()
        tm.view()
        tm_equal(tm, tm2)

    return _

basic_func_for_testing = partial(func_for_testing, Basic)

class TestBasic:
    def test_single_move(self):
        test = func_for_testing(Basic, "single_move")

        test("1,0,1,0,1,b,1,0,o,t,c:::q1:", "1,0,1,0,1,b,1,0,o,t,c:1::q1:", "R", suppose_val="0")
        test("1,0,1,0,1,b,1,0,o,t,c:2::q1:", "1,0,1,0,1,b,1,0,o,t,c:1::q1:", "L", suppose_val="0")
        test("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q1:", "R",
             suppose_val="b", next_val="1", next_cond=NextCondition.prev)
        test("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::e253:", "R",
             suppose_val="b", next_cond="e253")

    def join_tmac_equal(self, tmac1, tmac2):
        assert tmac1.val_cond.get() == tmac2.val_cond.get()

        assert tmac1.cond_alpha.reserved == tmac2.cond_alpha.reserved
        # assert tmac1.val_alpha.reserved == tmac2.val_alpha.reserved

        # print(tmac1.tm, tmac2.tm)

        def get_rules(tmac):
            return "\n".join(str(tmac.tm).split("\n")[7:])

        print(get_rules(tmac1))
        print(get_rules(tmac2), "\n\n")

        assert get_rules(tmac1) == get_rules(tmac2)

    def join_testing(self, state1, state2, conditions, *args, reserved=None, **kwargs):
        """ Helper function for testing Basic.join"""
        if reserved is None:
            reserved = conditions
        mac1 = Basic(TuringMachine.from_str(state1))
        mac2 = Basic(TuringMachine.from_str(state2))

        mac1.cond_alpha.reserved = mac1.cond_alpha.reserved.union(set(reserved))
        mac1.val_cond.set(mac1.val_cond.get()[0], list(conditions))
        mac1.join(*args, **kwargs)

        self.join_tmac_equal(mac1, mac2)

    def test_join(self):

        self.join_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q4:"
                                                 "1 q1 -> 1 q4 R,"
                                                 "1 q2 -> 1 q4 R,"
                                                 "1 q3 -> 1 q4 R",
                          ["q1", "q2", "q3"], "R", suppose_val="b")

        self.join_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q4:"
                                                 "1 q1 -> a q4 R,"
                                                 "1 q2 -> a q4 R,"
                                                 "1 q3 -> a q4 R",
                          ["q1", "q2", "q3"], "R", suppose_val="b", next_val="a")

        try:
            self.join_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q4:"
                                                     "1 q1 -> a q1 R,"
                                                     "1 q2 -> a q2 R,"
                                                     "1 q3 -> a q3 R",
                          ["q1", "q2", "q3"], "R", suppose_val="b", next_val="a", next_cond=NextCondition.prev)
        except Basic.UndeterminedConditionError:
            pass
        else:
            assert False, "Undetermined condition exception should be thrown in this case to pass the test"

        self.join_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q5:"
                                                 "1 q1 -> a q5 R,"
                                                 "1 q2 -> a q5 R,"
                                                 "1 q3 -> a q5 R",
                          ["q1", "q2", "q3"], "R", reserved=["q1", "q2", "q3", "q4"],suppose_val="b", next_val="a", next_cond=NextCondition.auto)

    parallel_tmac_equal = join_tmac_equal

    def parallel_testing(self, state1, state2, value, conditions1, conditions2,
                         *args, reserved1=None, reserved2=None, suppose_vals=None, **kwargs):
        """Helper function for testing Basic.parallel_move"""

        if reserved1 is None:
            reserved1 = conditions1

        if reserved2 is None:
            reserved2 = conditions2

        mac1 = Basic(TuringMachine.from_str(state1))
        mac2 = Basic(TuringMachine.from_str(state2))

        mac2.val_cond.set(mac2.val_cond.get_values() if suppose_vals is None
                          else suppose_vals, conditions2)
        mac2.cond_alpha.reserved = mac2.cond_alpha.reserved.union(reserved2)

        mac1.cond_alpha.reserved = mac1.cond_alpha.reserved.union(set(reserved1))
        mac1.val_cond.set(value, conditions1)
        mac1.parallel_move(*args, suppose_vals=suppose_vals, **kwargs)

        self.parallel_tmac_equal(mac1, mac2)

    def test_parallel_move(self):
        self.parallel_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q1:"
                                                     "1 q1 -> 1 q1 R,"
                                                     "1 q2 -> 1 q2 R,"
                                                     "1 q3 -> 1 q3 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q1", "q2", "q3"], "R", suppose_vals="b")

        self.parallel_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q1:"
                                                     "1 q1 -> 1 q1 R,"
                                                     "1 q2 -> 1 q2 R,"
                                                     "1 q3 -> 1 q3 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q1", "q2", "q3"], "R", suppose_vals="b")

        self.parallel_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q6:"
                                                     "1 q1 -> 1 q4 R,"
                                                     "1 q2 -> 1 q5 R,"
                                                     "1 q3 -> 1 q6 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q4", "q5", "q6"], "R",
                              reserved2=["q1", "q2", "q3", "q4", "q5", "q6"],
                              suppose_vals="b", next_conds=NextCondition.auto)

        self.parallel_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q6:"
                                                     "1 q1 -> 1 q4 R,"
                                                     "1 q2 -> 1 q6 R,"
                                                     "1 q3 -> 1 q5 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q4", "q6", "q5"], "R",
                              reserved2=["q1", "q2", "q3", "q4", "q5", "q6"],
                              suppose_vals="b", next_conds=["q4", "q6", "q5"])

        self.parallel_testing("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q6:"
                                                     "1 q1 -> 1 q4 R,"
                                                     "1 q2 -> 1 q6 R,"
                                                     "1 q3 -> 1 q5 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q4", "q6", "q5"], "R",
                              reserved2=["q1", "q2", "q3", "q4", "q5", "q6"],
                              suppose_vals=["a", "b", "c"], next_conds=["q4", "q6", "q5"])

    def set_rule_testing1(self, state1, state2, value, conditions1, conditions2,
                         *args, reserved1=None, reserved2=None, suppose_vals=None, **kwargs):
        """Helper function for testing Basic.set_rule"""

        if reserved1 is None:
            reserved1 = conditions1

        if reserved2 is None:
            reserved2 = conditions2

        mac1 = Basic(TuringMachine.from_str(state1))
        mac2 = Basic(TuringMachine.from_str(state2))

        mac2.val_cond.set(mac2.val_cond.get_values() if suppose_vals is None
                          else suppose_vals, conditions2)
        mac2.cond_alpha.reserved = mac2.cond_alpha.reserved.union(reserved2)

        mac1.cond_alpha.reserved = mac1.cond_alpha.reserved.union(set(reserved1))
        mac1.val_cond.set(value, conditions1)
        mac1.set_rule(*args, suppose_val=suppose_vals, **kwargs)

        self.parallel_tmac_equal(mac1, mac2)

    def set_rule_testing2(self, state1, state2, conditions, *args, reserved=None, **kwargs):
        """ Helper function for testing Basic.join"""
        if reserved is None:
            reserved = conditions
        mac1 = Basic(TuringMachine.from_str(state1))
        mac2 = Basic(TuringMachine.from_str(state2))

        mac1.cond_alpha.reserved = mac1.cond_alpha.reserved.union(set(reserved))
        mac1.val_cond.set(mac1.val_cond.get()[0], list(conditions))
        mac1.set_rule(*args, **kwargs)

        self.join_tmac_equal(mac1, mac2)

    def test_set_rule(self):
        test = func_for_testing(Basic, "set_rule")
        test("1,0,1,0,1,b,1,0,o,t,c:::q1:", "1,0,1,0,1,b,1,0,o,t,c:1::q1:", "R", suppose_val="0")

        self.set_rule_testing1("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q6:"
                                                     "1 q1 -> 1 q4 R,"
                                                     "1 q2 -> 1 q6 R,"
                                                     "1 q3 -> 1 q5 R",
                                                     "1",
                              ["q1", "q2", "q3"], ["q4", "q6", "q5"], "R",
                              reserved2=["q1", "q2", "q3", "q4", "q5", "q6"],
                              suppose_vals=["a", "b", "c"], next_cond=["q4", "q6", "q5"])

        self.set_rule_testing2("1,b,1,0,o,t,c:::q1:", "1,b,1,0,o,t,c:1::q4:"
                                                 "1 q1 -> a q4 R,"
                                                 "1 q2 -> a q4 R,"
                                                 "1 q3 -> a q4 R",
                          ["q1", "q2", "q3"], "R", suppose_val="b", next_val="a", join=True)

    def test_stop(self):
        mac = Basic(TuringMachine.from_str("1,b,0,0,1:::q1:"))
        mac.set_rule("R", suppose_val="b")
        mac2 = Basic(TuringMachine.from_str("1,b,0,0,1:1::q1:"))
        mac.stop()
        mac.tm.run()
        tm_equal(mac.tm, mac2.tm)


# def prepare_class(obj, string, cls):
#     tm = TuringMachine.from_str(string)
#     obj.bsc = cls(tm)
#
#
# def reset_to_class_setup(string=None):
#     def f(func):
#         def _(*args, **kwargs):
#             res = func(*args, **kwargs)
#             self = args[0]
#             self.setup_class(string)
#
#             return res
#
#         return _
#
#     return f
#
# class TestMoveByVal:
#     TESTSTRING1 = "1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:"
#
#     def setup_class(self, string=None):
#         tm = TuringMachine.from_str(self.TESTSTRING1)
#         self.tmac = Macro(tm)
#
#     def test_call(self):
#         tm1 = TuringMachine.from_str(self.TESTSTRING1)
#         tmac = Macro(tm1)
#
#         tmac.move_by_val(['0', '1'], 'b', 'R')
#         tmac.move_by_val(['0', '1', 'o', 't'], 'c', 'R')
#         tmac.stop()
#         tmac.tm.run()
#         tmac.tm.view()
#
#         final = TuringMachine.from_str("1,0,0,0,1,1,0,b,1,0,o,t,t,c:13:0:q1:")
#         tm_equal(tmac.tm, final)