from collections import namedtuple

from anytree import Node

from turingmachine.machine import TuringMachine
from turingmachine.macro import TuringMachineMacro

tm = TuringMachine.from_str("a,1,0,1,1,b:::q1:")
tmac = TuringMachineMacro(tm)

function = namedtuple("BinaryFunctionVector", "start end")
f1 = function('a', 'b')
f1 = Node(f1)
x1 = Node('x1', parent=f1)
x2 = Node('x2', parent=f1)

tmac.gen_func_vec(f1)
tmac.stop()
tm.run()
tm.view()
