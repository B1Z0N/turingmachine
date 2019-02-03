from turingmachine.machine import TuringMachine as tm
from turingmachine.macro import TuringMachineMacro as tmm

tm1 = tm.from_str('a,1,1,b,1,0,0,1,c:::q9:')
t = tmm(tm1)
t.bin_func('a', 'b', 'c', 'd', cond_gen='q')
tm1.rule_file('temp.txt')
tm1.run()
tm1.view()