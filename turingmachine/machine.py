"""
Module providing TuringMachine class

Usage:
    >>> tm = machine.TuringMachine(['1', '2', '3'], 'q1')
    >>> tm.set_rule('1', 'q1', '0', 'q1', tm.forward)
    >>> tm.rule_str('2 q1 -> 1 q2 L')
    >>> tm.rule_str('0 q2 -> 0 q2 R')
    >>> tm.rule_str('1 q2 -> 1 q2 R')
    >>> tm.rule_str('3 q2 -> 1 q2 S')
    >>> print(tm)
    TuringMachine(
    Index: 0
    Condition: q1
    Default:
    Tape: ['1', '2', '3']
    Rules:
    1 q1 --> 0 q1 R
    2 q1 --> 1 q2 L
    0 q2 --> 0 q2 R
    1 q2 --> 1 q2 R
    3 q2 --> 1 q2 S
    )
    >>> tm.move()
    '2'
    >>> tm
    TuringMachine(
    Index: 1
    Condition: q1
    Default:
    Tape: ['0', '2', '3']
    Rules:
    1 q1 --> 0 q1 R
    2 q1 --> 1 q2 L
    0 q2 --> 0 q2 R
    1 q2 --> 1 q2 R
    3 q2 --> 1 q2 S
    )
    >>> tm.run()
    >>> tm
    TuringMachine(
    Index: 2
    Condition: q2
    Default:
    Tape: ['0', '1', '1']
    Rules:
    1 q1 --> 0 q1 R
    2 q1 --> 1 q2 L
    0 q2 --> 0 q2 R
    1 q2 --> 1 q2 R
    3 q2 --> 1 q2 S
    )
    >>> print(tm.log)
    1 q1 --> 0 q1 R
    2 q1 --> 1 q2 L
    0 q2 --> 0 q2 R
    1 q2 --> 1 q2 R
    3 q2 --> 1 q2 S
"""

import itertools
import sys
from collections import deque, defaultdict


class TuringMachineError(Exception):
    """Main exception class for this module"""
    pass


class RuleNotFoundError(TuringMachineError):
    """Invokes when there is no rule for moving"""

    def __init__(
            self, val,
            cond, turing_machine
            ):
        msg = "Rule with {} is absent, in list of rules on this machine:\n{}\n"
        rule = "value: {}, condition: {}"

        super().__init__(
            msg.format(
                rule.format(val, cond),
                turing_machine
                )
            )


class TuringMachineStop(TuringMachineError):
    """Raise when Turing machine is stopped"""

    def __init__(self, msg=''):
        super().__init__(msg)


class RuleExistsError(TuringMachineError):
    """Raise when trying to add rule that already exist"""

    def __init__(self, val, cond):
        msg = f'Rule with value: {val} and condition: {cond} already exist'
        super().__init__(msg)


class TuringMachine:
    """Main class implementing an interface for
    programming Alan Turing Machine

    Attributes:
        current: current pointer position value
        condition: start condition of the machine
        log: log of all moves
        _rules: all rules
        tape: tape layout
        index: current pointer position index
        default: default value of empty cell
        log_func: logging function(default provided)
    """

    EMPTY_SIGN = 'B'

    MAIN_OUTPUT = sys.stdout

    def __init__(
            self, start_vals,
            start_condition, index=0,
            log_func=None, default=''
            ):
        self.stopped = False
        self._center = 0
        self.condition = str(start_condition)
        self._rules = defaultdict()
        self.log = ''
        self.tape = deque(str(val) for val in start_vals)
        self.index = int(index)
        self.default = default

        if log_func is None:
            self.log_func = self.default_log
        else:
            self.log_func = log_func

        if not self.tape:
            self.tape.append(self.default)

    def set_rule(
            self, val,
            condition, next_val,
            next_condition, move
            ):
        """
        Set a rule for moving according to it

        Arguments:
            val: tape cell value
            condition: machine condition
            next_val: next tape cell value
            next_condition: next machine condition
            move: direction R(right), L(left), S(stay) or STOP
        """
        move_func = self._move_char_to_func(move)  # to check for right format character R, L or S
        val, condition, next_val, next_condition = str(val), str(condition), str(next_val), str(next_condition)

        check = self._rules.get((val, condition))
        to = (
            next_val, next_condition,
            move_func
            )

        if check is None:
            """When this is a new rule we are adding"""
            self._rules[(val, condition)] = to
        elif check == to:
            """When there already are the same rule we are adding"""
            pass
        else:
            """When we are trying to rewrite the rule"""
            raise RuleExistsError(val, condition)

    def _move_char_to_func(self, move):
        """Converts moves R, L, S to functions in TuringMachine class"""
        if move == 'R':
            return self.forward
        elif move == 'L':
            return self.back
        elif move == 'S':
            return self.stay
        elif move == 'STOP':
            return self.stop
        else:
            raise ValueError(f"wrong move character: '{move}', must be either 'R','L' or 'S'")

    def rule_str(
            self, format_string,
            delimiter=' ', rules_delimiter=','
            ):
        """
        Add a rule using str
        Template:
            'val condition -> next_val next_condition direction'
            where direction is either R(right), L(left) or S(stop)
        Example:
            '1 q1 -> 2 q3 R'
        """
        if rules_delimiter in format_string:
            lst = format_string.split(rules_delimiter)
        else:
            lst = [format_string]

        for elem in lst:
            if elem.endswith('STOP'):
                val, cond, _, next_val, move = elem.split(delimiter)
                next_cond = cond
            else:
                val, cond, _, next_val, next_cond, move = elem.split(delimiter)
            if val == self.EMPTY_SIGN:
                val = self.default

            self.set_rule(
                val, cond,
                next_val, next_cond,
                move
                )

    def rule_file(self, name, delimiter=' '):
        with open(name) as file:
            s = file.read()
        s = s.strip().replace('\n', ',')
        if s:
            self.rule_str(s, delimiter=delimiter)

    def move(self):
        """Make a move according to the rules
        Returns:
            current value of the new cell"""
        if self.stopped:
            return

        try:
            next_val, next_cond, move_func = self._rules[(self.current, self.condition)]
        except KeyError:
            raise RuleNotFoundError(
                self.current, self.condition,
                self
                )

        self.log += self.log_func(
            self.current, self.condition,
            next_val, next_cond, move_func
            ) + '\n'
        self.condition = next_cond

        try:
            return move_func(next_val)
        except TuringMachineStop:
            self.stopped = True

    def run(self):
        """Make all available moves unless it is stopped or
        an exception is raised"""

        while not self.stopped:
            """until stop function called or paused"""
            self.move()

    def default_log(
            self, val,
            condition, next_val,
            next_condition, move_func,
            delimiter=' ', file=None,
            step_sign='->'
            ):
        """Default logging function
        Returns:
            move log string"""
        if move_func == self.forward:
            move = 'R'
        elif move_func == self.back:
            move = 'L'
        elif move_func == self.stay:
            move = 'S'
        elif move_func == self.stop:
            move = 'STOP'
        else:
            move = '"' + move_func.__name__ + '"'

        s = delimiter.join([
            val, condition,
            step_sign, next_val,
            next_condition, move
            ])

        if file is not None:
            print(s, file=file)

        return s

    @classmethod
    def from_str(
            cls, _str, tape_delimiter=',',
            rules_delimiter=',',
            section_delimiter=':',
            log_func=None
            ):
        """Alternative constructor, for creating cls from a string
        Template:
            'tape_elements_separated_by_comma:start_index:default:start_condition:rules_separated_by_comma'
        Example:
            '1,2,3:0:q1:1 q1 -> 0 q2 R,2 q2 -> 3 q2 S'
        Returns:
            new object of this class
        """
        tape, index, default, start_cond, rules = _str.split(section_delimiter)

        tape = tape.split(tape_delimiter)

        if not index:
            index = 0

        obj = cls(tape, start_cond, index=index, default=default, log_func=log_func)
        if rules:
            obj.rule_str(rules, rules_delimiter=rules_delimiter)

        return obj

    @classmethod
    def from_file(
            cls, file_name, tape_delimiter=',',
            section_delimiter=':', log_func=None
            ):
        """Alternative constructor, for creating cls from a file
        Template:
            tape_elements_separated_by_comma:start_index:default:start_condition
            rule
            rule
            ...
            rule
        Example:
            1,2,3:0:q1
            1 q1 -> 0 q2 R
            2 q2 -> 3 q2 S'
        Returns:
            new object of this class
        """
        with open(file_name) as file:
            head = file.readline()
            tail = file.read()

        if tail:
            head = head.replace('\n', section_delimiter)
            tail = tail.strip()
            tail = tail.replace('\n', ',')
        else:
            head = head.strip()

        init_str = head + tail

        return cls.from_str(
            init_str, tape_delimiter=tape_delimiter, log_func=log_func)

    def forward(self, value):
        """Put a value to the current position and move right on the tape
        Returns:
            current value of the new cell
        """
        self[self.index] = str(value)
        self.index += 1
        cur = self[self.index]

        return cur

    def back(self, value):
        """Put a value to the current position and move left on the tape
        Returns:
            current value of the new cell
        """
        self[self.index] = str(value)
        self.index -= 1
        cur = self[self.index]

        return cur

    def stay(self, value):
        """Put a value to the current position and stay here
        Returns:
            current value of the new cell
        """
        self[self.index] = str(value)

        return self.current

    def stop(self, value):
        self.stay(value)
        raise TuringMachineStop

    def _prepare_index(self, index):
        length = len(self.tape)
        center = self._center

        if index > 0:
            append_times = index - (length - center) + 1
            for i in range(append_times):
                self.tape.append(self.default)
        elif index < 0:
            append_times = - (index + center)
            for i in range(append_times):
                self.tape.appendleft(self.default)

            if append_times > 0:
                self._center += append_times

        return self._center + index

    def __getitem__(self, index):
        if isinstance(index, slice):
            start = self._prepare_index(index.start)
            stop = self._prepare_index(index.stop)
            return list(
                itertools.islice(
                    self.tape,
                    start, stop
                    )
                )
        index = self._prepare_index(index)
        return self.tape[index]

    def __setitem__(self, index, value):
        index = self._prepare_index(index)
        self.tape[index] = value

    def view(self):
        string = str(self)
        for line in string.splitlines()[0:6]:
            print(line)

    def __repr__(self):
        center = self[0]
        self[0] = '{' + center + '}'
        index = self[self.index]
        self[self.index] = '[' + index + ']'
        tape = str(self.tape)
        self[self.index] = index  #
        self[0] = center  # Order is very important

        s = 'Index[]: ' + str(self.index) + '\nCondition: ' + self.condition \
            + '\nDefault: ' + self.default + '\nCenter{}: ' + str(self._center) \
            + '\nTape: ' + tape[tape.find('['):-1] + '\nRules:\n'
        for key, val in self._rules.items():
            s += self.default_log(key[0], key[1], val[0], val[1], val[2]) + '\n'

        return "TuringMachine(\n{})".format(s)

    __str__ = __repr__

    def _get_cur(self):
        return self[self.index]

    def _set_cur(self, val):
        raise PermissionError("to set current item use back, forward, stay or stop functions")

    current = property(_get_cur, _set_cur)
