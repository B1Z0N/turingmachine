from collections import deque
import string
from itertools import product
import sys
digit_letters = string.ascii_lowercase + string.digits

class TuringMachine:
    MAIN_OUTPUT = sys.stdout
    
    def __init__(self, start_vals, start_condition, index = 0, default = '', log_func = None):
        self.condition = start_condition
        self._rules = {}
        self.log = ''
        self._tape = deque(str(val) for val in start_vals)
        self._index = int(index)
        self._default = str(default)
        if log_func is None:
            self.log_func = self.main_log
        else:
            self.log_func = log_func
        if not self._tape:
            self._tape.append(self._default)
            
    def set_rule(self, val, condition, next_val, next_condition, move_func):
        """
        For example:
            set_rule('1', 'q43', '0', 'q44', TuringMachine.forward) is equivalent to
            1 q43 --> 0 q44 R
        """
        val, condition, next_val, next_condition = str(val), str(condition), str(next_val), str(next_condition)
        self._rules[(val, condition)] = (next_val, next_condition, move_func)
        
    def rule_str(self, format_string, delimiter = ' '):
        val, cond, _, next_val, next_cond, move = format_string.split(delimiter)
        if val =='DEL': val = self._default
        
        if move == 'R': move_func = self.forward
        elif move == 'L': move_func = self.back
        elif move == 'S': move_func = self.stop
        else: raise ValueError("wrong move character, must be either 'R','L' or 'S'")
        
        self.set_rule(val, cond, next_val, next_cond, move_func)
        
    def move(self):
        next_val, next_cond, move_func = self._rules[(self.current, self.condition)]
        self.log += self.log_func(self.current, self.condition, next_val, next_cond, move_func) + '\n'
        self.condition = next_cond
        
        return move_func(next_val)
    
    def run(self):
        while self.move() is not None:#untill stop function called
            pass
        
    def main_log(self, val, condition, next_val, next_condition, move_func, delimiter = ' ', file = None):
        if move_func == self.forward: move = 'R'
        elif move_func == self.back: move = 'L'
        elif move_func == self.stop: move = 'S'
        else: move = '"' + move_func.__name__ + '"'
        
        s = delimiter.join([val, condition, '-->', next_val, next_condition, move])
        if file is not None: print(s, file = file)
        
        return s
    
    @classmethod
    def from_str(cls, string):#t
        """
        Alternative constructor for creating
        TuringTape from formatted string.

        Some exmaples:
        1. TuringTape.from_str('1,2,3,4:3;5)'
        is equivalent to TuringTape([1, 2, 3, 4], index = 3, default = 5)
        2. TuringTape.from_str('1,2,3,4)'
        is equivalent to TuringTape([1, 2, 3, 4], index = 0, default = '')
        """
        
        val_list = string.split(',')
        def split_with_empty_str(string, splitchar):
            """
            behaviour:
            split_with_empty_str('2', ';') --> ('2', '')
            split_with_empty_str('2;3', ';') --> ('2', '3')
            """
            l = string.split(splitchar)
            if len(l) == 2:
                first, second = l
            elif len(l) == 1:
                first, second = (l[0], '')
            else:
                raise SyntaxError
            return first, second
        
        last_val, index = split_with_empty_str(val_list[-1], ':')
        val_list[-1] = last_val
        index, default = split_with_empty_str(index, ';')
        if not index: index = 0
        return cls(val_list, index, default)
    
    @classmethod
    def from_file(cls, fname):#t
        """
        Alternative constructor for creating
        TuringTape from formatted file:
        file with first string formatted for method
        from_str, described there
        """
        with open(fname) as file:
            s = file.read()
        s = s[:s.find('\n')]
        return cls.from_str(s)
    
    def forward(self, value):
        self._tape[self._index] = str(value)
        self._index += 1
        if len(self._tape) == self._index:
            self._tape.append(self._default)
        return self.current
    
    def back(self, value):
        self._tape[self._index] = str(value)
        if self._index == 0:
            self._tape.appendleft('')
        else:
            self._index -= 1
        return self.current
    
    def stop(self, value):
        self._tape[self._index] = str(value)
        
    def __repr__(self):
        tape = repr(self._tape)
        s = 'Index: ' + str(self._index) + '\nCondition: ' + self.condition + \
             '\nDefault: ' + self._default + '\nTape: ' + tape[tape.find('['):-1] + \
             '\nRules:\n'  
        for key, val in self._rules.items():
            s += self.main_log(key[0], key[1], val[0], val[1], val[2])
            
        return "TuringMachine(\n{}\n)".format(s)
    
    __str__ = __repr__
    
    def _get_cur(self):
        return self._tape[self._index]
    def _set_cur(self, val):    
        raise PermissionError("to set current item use back, forward or stop functions")
        
    current = property(_get_cur, _set_cur)
    
class TuringAlphabet:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.it = self.get_letters()
    def get_letter(self):
        for i in range(1, len(self.alphabet)):
            for elem in filter(lambda x: x[0] not in string.digits,
                               product(self.alphabet, repeat = i)):
                yield elem
    def pop(self):
        return next(self.it)
    
        
    
        
