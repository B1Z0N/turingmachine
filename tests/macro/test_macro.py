from functools import partial

from turingmachine.machine import TuringMachine
from turingmachine.macro import MacroSticks, Basic, NextCondition, Macro


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
    # print(tm1.tape, tm2.tape, sep="\n")
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
        """Helper function for testing Basic.parallel_cond_move"""

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
        mac1.parallel_cond_move(*args, suppose_vals=suppose_vals, **kwargs)

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

    def test_parallelize_by_vals(self):
        create = lambda string: Basic(TuringMachine.from_str(string))

        tmac = create("a,b,1,0,o,t,c:::q1:")
        tmac.parallelise_by_vals("R", suppose_vals=["b", "1"])
        tmac.stop()
        tmac.tm.run()
        tmac2 = create("a,b,1,0,o,t,c:1::q1:")
        tmac2.val_cond.set(["b", "1"], "q1")
        tmac_equal(tmac, tmac2)

        tmac = create("a,b,1,0,o,t,c:::q1:")
        tmac.parallelise_by_vals("R", suppose_vals=["b", "1"])
        assert tmac.val_cond.get() == (["b", "1"], "q1")

    def test_manual_rule(self):
        def test(with_update=False):
            tmac = Basic(TuringMachine.from_str("1,b,1,0,o,t,c:::q1:"))
            tmac.manual_rule("1", "q1", "a", "q1", "R")
            if with_update is True:
                tmac.val_cond.set(stick_val="b", stick_cond="q1")
            tmac.stop()
            tmac.tm.run()
            tmac_equal(tmac, Basic(TuringMachine.from_str("a,b,1,0,o,t,c:1::q1:")))

        test(with_update=True)
        try:
            test()
        except AssertionError:
            pass
        else:
            raise AssertionError

    def test_stop(self):
        mac = Basic(TuringMachine.from_str("1,b,0,0,1:::q1:"))
        mac.set_rule("R", suppose_val="b")
        mac2 = Basic(TuringMachine.from_str("1,b,0,0,1:1::q1:"))
        mac.stop()
        mac.tm.run()
        tm_equal(mac.tm, mac2.tm)


class TestMoveByVal:

    def test_single_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))

        def test(start, final, move_vals, end_vals, direction, between_runs=None):
            tmac = create(start)

            tmac.move_by_val.single_move(move_vals, end_vals, direction)
            if between_runs is not None:
                between_runs(tmac)
            tmac.stop()
            tmac.tm.run()
            tmac.tm.view()

            tm_equal(tmac.tm, create(final).tm)

        test("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:", "1,0,0,0,1,1,0,b,1,0,o,t,t,c:13:0:q1:", ['0', '1', 'o', 't', 'b'], 'c', "R")

        def check_val_conds(tmac):
            assert tmac.val_cond.get() == (["c", "v"], "q3")

        test("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:", "1,0,0,0,1,1,0,b,1,0,o,t,t,c:13:0:q1:",
             ['0', '1', 'o', 't', 'b'], ['c', 'v'], "R", check_val_conds)


    def test_parallelise(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        end_val, end_conds = tur.move_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R",
                                                         start_vals=["0", "1"])
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,1:10::" + end_conds[1] + ":").tm)

        tur = create("a,0,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        end_val, end_conds = tur.move_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R",
                                                         start_vals=["1", "0"])
        tur.manual_rule(end_val, end_conds[1], "0", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "1", end_conds[0], "S")
        tur.val_cond.set("0", end_conds[1])
        tur.stop()
        tur.tm.run()
        print(tur.tm)
        tm_equal(tur.tm, create("a,0,0,1,1,1,b,2,2,2,0:10::" + end_conds[1] + ":").tm)

    def test_parallel_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.move_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.move_by_val.parallel_move([tur.tm.default], "", "R")
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,,1:11::" + end_conds[1] + ":").tm)

        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.move_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.parallel_cond_move("R", suppose_vals=tur.tm.default, next_conds=NextCondition.auto)
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,,1:11::" + end_conds[1] + ":").tm)

        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.move_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.move_by_val.parallel_move([tur.tm.default, "0", "1", "b", "2"], "a", "L")
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("1,1,0,1,1,1,b,2,2,2,:::" + end_conds[1] + ":").tm)


class TestCleanRange:
    def test_single_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tmac = create("1,1,0,1,1,1,b,2,2,2,:::q1:")
        tmac.clean_range.single_move(["1", "0"], "b", "R")
        tmac.stop()
        tmac.tm.run()
        tm_equal(tmac.tm, create(",,,,,,b,2,2,2,:6::q1:").tm)

        tmac = create("1,1,0,1,1,1,b,2,2,2:6::q1:")
        tmac.clean_range.single_move(["1", "0"], tmac.tm.default, "L", include_end=True, include_start=False)
        tmac.stop()
        tmac.tm.run()
        print(tmac.tm)
        tm_equal(tmac.tm, create(",,,,,,b,2,2,2:-1::q1:").tm)


class TestPutByVal:

    def test_single_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))

        def test(start, final, move_vals, end_vals, direction, put_val=None, between_runs=None):
            tmac = create(start)

            tmac.put_by_val.single_move(move_vals, end_vals, direction, put_val=put_val)
            if between_runs is not None:
                between_runs(tmac)
            tmac.stop()
            tmac.tm.run()
            tmac.tm.view()

            tm_equal(tmac.tm, create(final).tm)

        test("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:", "1,0,0,0,1,1,0,b,1,0,o,t,t,d:13:0:q1:",
             ['0', '1', 'o', 't', 'b'], 'c', "R", put_val="d")

        def check_val_conds(tmac):
            assert tmac.val_cond.get() == (["c", "v"], "q3")

        try:
            test("1,0,0,0,1,1,0,b,1,0,o,t,t,c:::q1:", "1,0,0,0,1,1,0,b,1,0,o,t,t,c:13:0:q1:",
                 ['0', '1', 'o', 't', 'b'], ['c', 'v'], "R", put_val="s", between_runs=check_val_conds)
        except Basic.UndeterminedConditionError:
            pass
        else:
            raise AssertionError

    def test_parallelise(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        end_vals, end_cond = \
            tur.put_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R",
                                       start_vals=["0", "1"], put_vals=["0", "1"])

        tur.stop()
        tur.tm.run()
        print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,1:10::" + end_cond + ":").tm)

        tur = create("a,0,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="0")
        end_vals, end_cond = \
            tur.put_by_val.parallelise(["1", "0", "b", "2"],
                                       tur.tm.default, "R", start_vals=["1", "0"], put_vals=["1", "0"])
        tur.stop()
        tur.tm.run()
        print(tur.tm)
        tmac2 = create("a,0,0,1,1,1,b,2,2,2,0:10::" + end_cond + ":")
        tmac2.val_cond.set(["1", "0"], end_cond)
        tm_equal(tur.tm, tmac2.tm)

    def test_parallel_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.put_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.put_by_val.parallel_move([tur.tm.default], "", "R")
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,,1:11::" + end_conds[1] + ":").tm)

        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.put_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.parallel_cond_move("R", suppose_vals=tur.tm.default, next_conds=NextCondition.auto)
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("a,1,0,1,1,1,b,2,2,2,,1:11::" + end_conds[1] + ":").tm)

        tur = create("a,1,0,1,1,1,b,2,2,2:::q1:")
        tur.single_move("R", suppose_val="1")
        tur.put_by_val.parallelise(["1", "0", "b", "2"], tur.tm.default, "R", start_vals=["0", "1"])
        end_val, end_conds = tur.put_by_val.parallel_move([tur.tm.default, "0", "1", "b", "2"], "a", "L")
        tur.manual_rule(end_val, end_conds[1], "1", end_conds[1], "S")
        tur.manual_rule(end_val, end_conds[0], "0", end_conds[0], "S")
        tur.val_cond.set("1", end_conds[1])
        tur.stop()
        tur.tm.run()
        # print(tur.tm)
        tm_equal(tur.tm, create("1,1,0,1,1,1,b,2,2,2,:::" + end_conds[1] + ":").tm)


class TestSetAllOnWay:
    def test_single_move(self):
        create = lambda string: Macro(TuringMachine.from_str(string))
        tmac = create("1,1,0,1,1,1,b,2,2,2,:::q1:")
        tmac.set_all_on_way.single_move(["1", "0"], "b", "R", to_val="s")
        tmac.stop()
        tmac.tm.run()
        tm_equal(tmac.tm, create("s,s,s,s,s,s,b,2,2,2,:6::q1:").tm)

        tmac = create("1,1,0,1,1,1,b,2,2,2:6::q1:")
        tmac.set_all_on_way.single_move(["1", "0"], tmac.tm.default, "L",
                                        to_val="d", include_end=True, include_start=False)
        tmac.stop()
        tmac.tm.run()
        print(tmac.tm)
        assert tmac.tm.tape == create("d,d,d,d,d,d,d,b,2,2,2:::q1:").tm.tape
