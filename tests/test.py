from turingmachine.machine import TuringMachine as tm
from turingmachine.macro import TuringMachineMacro as tmm

tm1 = tm.from_str('a,1,0,b,1,0,1,1,_,c,0,1,l,2,k,l,j,1:::q1:')
tmac = tmm(tm1)
tmac.move_range(
    'a', ['1', '0'],
    'b', ['_', '0', '1'],
    'c', ['j', 'k', 'l', '1', '2', '0'],
    'R'
    )
tmac.stop()
tm1.run()
tm1.view()
