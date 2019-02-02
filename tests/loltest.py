from turingmachine.machine import TuringMachine
from turingmachine.macro import TuringMachineMacro

tm = TuringMachine.from_str('1,2,3,1,2,3,1,2,3,4,5:::q1:')
macro = TuringMachineMacro(tm)
tm._center = 7
print(tm)
macro.move_by_val('1', 'L', cond_templ='q1')
print(tm)
macro.move_by_pos(-7, cond_templ='q')
print(tm)
