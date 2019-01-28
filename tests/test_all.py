from turingmachine.machine import  TuringMachine as TM

tm = TM.from_str('1,2,3:0::q1:1 q1 -> 2 q3 R,3 q2 -> 4 q4 S')
print(tm)
tm = TM.from_file('testf')
print(tm)

