from turingmachine.machine import TuringMachine
from turingmachine.macro import TuringMachineMacro

tm = TuringMachine.from_str("a,1,1,1,b,1,0,1,0,0,1,0,1,c:::q1:")
tmac = TuringMachineMacro(tm)
tmac.bin_func('a', 'b', 'c', 'd')
tmac.stop()
tm.run()
tm.view()
