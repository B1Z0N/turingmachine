from turingmachine.machine import TuringMachine as tm
from turingmachine.macro import TuringMachineMacro as tmm

tm1 = tm.from_str('a,1,0,2,3,b,_,2,1,c,0,1,l,2,k,l,j,k:::q1:')
tmac = tmm(tm1)
tmac.copy_range(
    'a', ['1', '0', '2', '3'],
    'b', ['_', '2', '1'],
    'c', ['j', 'k', 'l', '1', '2', '0'],
    'R'
    )
tmac.stop()
tm1.run()
tm1.view()
