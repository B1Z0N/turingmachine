from anytree import Node

from turingmachine.machine import TuringMachine
from turingmachine.macro import BinaryFunctionVector, TuringMachineGenFuncVecMacro

tm = TuringMachine.from_str("a,0,0,0,0,b,1,1,1,1,c:::q1:")
function = BinaryFunctionVector

f1 = function('a', 'b')
f2 = function('b', 'c')

f1 = Node(f1)
f2 = Node(f2, parent=f1)
x1 = Node('x1', parent=f1)
x11 = Node('x1', parent=f2)
x22 = Node('x2', parent=f2)

tmac = TuringMachineGenFuncVecMacro(f1, tm)
tmac.gen_func_vec()
tmac.stop()
tm.run()
tm.view()
