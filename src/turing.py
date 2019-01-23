from collections import deque

class TuringCondition(str):
    pass

class TuringTape():
    def __init__(self, start_vals, index = 0, default = ''):
        self._tape = deque(str(val) for val in start_vals)
        self._index = index
        self._default = str(default)
        if not self._tape:
            self._tape.append(self._default)
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
    
