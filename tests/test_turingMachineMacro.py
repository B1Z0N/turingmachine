from turingmachine.machine import TuringMachine
from turingmachine.macro import TuringMachineMacro


class TestTuringMachineMacro:
    def setup_class(self):
        self.tm = TuringMachine.from_str('1,2,3,4,5:3::q1:')
        self.macro = TuringMachineMacro(self.tm)

    def test_run_rules(self):
        pass

    def test_move_pointer(self):
        self.macro.move_pointer(0, new_cond='q1')
        print(self.tm)

    def test_bin_to_un(self):
        pass
