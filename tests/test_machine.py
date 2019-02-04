import copy

from turingmachine.machine import TuringMachine, RuleNotFoundError, TuringMachineStop


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
        self.tm5 = TuringMachine(
            self.start_vals, self.start_condition,
            index=self.index, log_func=self.log_func
            )

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
        self.tm2.rule_str('1 q1 -> 0 q1 L,B q1 -> 1 q1 R')
        self.tm2.rule_str('0 q1 -> 1 q1 R')

    def test_move(self):
        self.tm.move()
        self.tm2.move()

    def test_run(self):
        self.run_to_end = TuringMachine.from_str(
            "1,2,3:::q1:1 q1 -> 0 q1 L,B q1 -> 2 STOP",  # to stop on the fst element
            log_func=self.log_func
            )
        self.finish_with_exception = copy.deepcopy(self.tm)
        self.run_to_end.run()
        try:
            self.finish_with_exception.run()
        except RuleNotFoundError as e:
            print(e)

    def test_from_str(self):
        self.tm3 = TuringMachine.from_str(
            '1,2,3:::q1:1 q1 -> 0 q1 L,B q1 -> 1 q1 R,0 q1 -> 1 q1 R',
            log_func=self.log_func
            )
        self.tm3.move()  # to be similar to tm and tm2

    def test_from_file(self):
        self.file_name = 'machine_test_from_file'
        self.tm4 = TuringMachine.from_file(self.file_name, log_func=self.log_func)
        self.tm4.move() # to be similar to tm, tm2, tm3

    def test_rule_file(self):
        self.tm5.rule_file('machine_test_rule_file')

    def test_forward(self):
        self.tm_for_move.forward('kek')

    def test_back(self):
        self.tm_for_move.back('lol')

    def test_stop(self):
        self.tm_for_move.stay('stay')

    def test_stay(self):
        try:
            self.tm_for_move.stay('stop')
        except TuringMachineStop:
            pass

    def test__prepare_index(self):
        tm = TuringMachine.from_str('1,2,3:::q1:')
        tm._center = 1

        print(tm)

        index1 = tm._prepare_index(-1)
        print(index1, tm._tape[index1])
        assert tm._tape[index1] == '1' and index1 == 0

        index2 = tm._prepare_index(1)
        print(index2, tm._tape[index2])
        assert tm._tape[index2] == '3' and index2 == 2

        index3 = tm._prepare_index(4)
        print(index3, tm._tape[index3])
        assert tm._tape[index3] == '' and index3 == 5

        index4 = tm._prepare_index(-5)
        print(index4, tm._tape[index4])
        assert tm._tape[index4] == '' and index4 == 0


    def tear_down(self):
        s1 = str(self.tm)
        s2 = str(self.tm2)
        s3 = str(self.tm3)
        s4 = str(self.tm4)
        s5 = str(self.tm5)
        print(s1, s2, s3, s4)
        assert s1 == s2 == s3 == s4 == s5
