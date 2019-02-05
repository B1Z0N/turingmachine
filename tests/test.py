from turingmachine.machine import TuringMachine as tm
from turingmachine.macro import TuringMachineMacro as tmm

tm1 = tm.from_str('a,1,1,b,1,0,0,1,c:::q1:')
tmac = tmm(tm1)
tmac.bin_func('a', 'b', 'c', 'd')
on_way = ['0', '1', 'b', 'c']
tmac.move_by_val('d', 'R', on_way)
tmac.stop()
tm1.run()
tm1.view()
