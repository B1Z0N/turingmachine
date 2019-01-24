from collections import deque

class TuringCondition(str):
    pass

class TuringTape():
    def __init__(self, start_vals, index = 0, default = ''):
        self._tape = deque(str(val) for val in start_vals)
        self._index = int(index)
        self._default = str(default)
        if not self._tape:
            self._tape.append(self._default)
    @classmethod
    def from_str(cls, string):
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
    def from_file(cls, fname):
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
    def forward(self, value = None):
        if value is not None:
            self._tape[self._index] = str(value)
        self._index += 1
        if len(self._tape) == self._index:
            self._tape.append(self._default)
        return self.current
    def back(self, value = None):
        if value is not None:
            self._tape[self._index] = str(value)
        if self._index == 0:
            self._tape.appendleft('')
        else:
            self._index -= 1
        return self.current
    def stop(self, value):
        self._tape[self._index] = str(value)
    def __repr__(self):
        return "TuringTape({})".format(str(self))
    def __str__(self):
        dq = str(self._tape)
        return dq[dq.find('['):-1]
    def __rshift__(self, value):
        return self.forward(value)
    def __lshift__(self, value):
        return self.back(value)
    def _get_cur(self):
        return self._tape[self._index]
    def _set_cur(self, val):
        self.forward(val)
        
    current = property(_get_cur, _set_cur)
    
class TuringMachine:
    pass
