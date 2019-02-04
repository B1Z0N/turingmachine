from turingmachine.machine import TuringMachine as tm
from turingmachine.macro import TuringMachineMacro as tmm

tm1 = tm.from_str('a,1,1,b,1,0,0,1,c:::q1:')
tmac = tmm(tm1)
tmac.bin_func('a', 'b', 'c', 'd', cond_gen='q')
tmac.move_by_val('d', 'R', ['1', '0', 'b', 'c'], cond_templ='q')
tmac.move_by_val('a', 'L', ['1', '0', 'b', 'c'])
tmac.move_by_val('b', 'R', ['1', '0', 'a'])
tmac.stop()
tm1.run()
tm1.view()
