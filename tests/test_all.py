from turing import machine, macro, gui

mt = machine.TuringMachine([1, 2, 3], 'q1')
mt.rule_str('1 q1 -> 1 q1 R')
mt.rule_str('2 q1 -> 1 q1 L')
mt.rule_str('3 q1 -> 2 q1 L')
mt.rule_str('DEL q1 -> 1 q1 S')

while True:
    input()
    mt.move()
    print(mt)

