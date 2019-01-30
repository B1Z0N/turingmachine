from turingmachine.machine import TuringMachine, RuleNotFoundError
import copy

class TestTuringMachine:
    def setup_class(self):
        self.start_vals = [1, 2, 3]
        self.index = 0
        self.start_condition = 'q1'
        self.log_func = None
        self.tm = TuringMachine(
            self.start_vals, self.start_condition,
            index=self.index, log_func=self.log_func
            )
        self.tm2 = TuringMachine(
            self.start_vals, self.start_condition,
            index=self.index, log_func=self.log_func
            )
        self.tm_for_move = copy.deepcopy(self.tm)

    def test_set_rule(self):
        self.tm.set_rule(
            '1', 'q1',
            '0', 'q1',
            'L'
            )
        self.tm.set_rule(
            '', 'q1',
            '1', 'q1',
            'R'
            )
        self.tm.set_rule(
            '0', 'q1',
            '1', 'q1',
            'R'
            )

    def test_rule_str(self):
        self.tm2.rule_str('1 q1 -> 0 q1 L')
        self.tm2.rule_str('DEF q1 -> 1 q1 R')
        self.tm2.rule_str('0 q1 -> 1 q1 R')

    def test_move(self):
        self.tm.move()
        self.tm2.move()

    def test_run(self):
        self.run_to_end = TuringMachine.from_str("1,2,3::q1:1 q1 -> 0 q1 L,DEF q1 -> 2 q2 S",
            #  to stop on the fst element
            self.log_func
            )
        self.finish_with_exception = copy.deepcopy(self.tm)
        self.run_to_end.run()
        try:
            self.finish_with_exception.run()
        except RuleNotFoundError as e:
            print(e)

    def test_from_str(self):
        self.tm3 = TuringMachine.from_str('1,2,3::q1:1 q1 -> 0 q1 L,DEF q1 -> 1 q1 R,0 q1 -> 1 q1 R', self.log_func)
        self.tm3.move()  # to be similar to tm and tm2



    def test_from_file(self):
        self.file_name = 'machine_test_file'
        self.tm4 = TuringMachine.from_file(self.file_name, self.log_func)
        self.tm4.move() # to be similar to tm, tm2, tm3

    def test_forward(self):
        self.tm_for_move.forward('kek')

    def test_back(self):
        self.tm_for_move.back('lol')

    def test_stop(self):
        self.tm_for_move.stop('stop')

    def tear_down(self):
        s1 = str(self.tm)
        s2 = str(self.tm2)
        s3 = str(self.tm3)
        s4 = str(self.tm4)
        print(s1, s2, s3, s4)
        assert s1 == s2 == s3 == s4
