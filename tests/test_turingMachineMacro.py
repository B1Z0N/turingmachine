from functools import partial

from turingmachine.machine import TuringMachine
from turingmachine.macro import TuringMachineMacro


def tm_equal(
        tm1: TuringMachine,
        tm2: TuringMachine
        ):
    assert tm1.tape == tm2.tape
    assert tm1.index == tm2.index


def func_for_testing(function_name, state, state2, *args, **kwargs):
    tm = TuringMachine.from_str(state)
    tm2 = TuringMachine.from_str(state2)
    tmac = TuringMachineMacro(tm)
    getattr(tmac, function_name)(*args, **kwargs)
    tmac.stop()
    tm.run()
    tm.view()
    tm_equal(tm, tm2)


class TestTuringMachineMacro:
    def test_move_by_val(self):
        test = partial(func_for_testing, "move_by_val")
        """Move right test"""
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,c:5::q1:', 'c', ['_', 'a', 'b', 'c'], 'R')  # with start and end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,c:5::q1:', 'c', ['_', 'b', 'c'], 'R')  # without start
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,c:5::q1:', 'c', ['_', 'a', 'b'], 'R')  # without end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,c:5::q1:', 'c', ['_', 'b'], 'R')  # without start and end
        """Move left test"""
        test('a,b,_,_,_,c:5::q1:', 'a,b,_,_,_,c:::q1:', 'a', ['_', 'a', 'b', 'c'], 'L')  # with start and end
        test('a,b,_,_,_,c:5::q1:', 'a,b,_,_,_,c:::q1:', 'a', ['_', 'a', 'b'], 'L')  # without start
        test('a,b,_,_,_,c:5::q1:', 'a,b,_,_,_,c:::q1:', 'a', ['_', 'b', 'c'], 'L')  # without end
        test('a,b,_,_,_,c:5::q1:', 'a,b,_,_,_,c:::q1:', 'a', ['_', 'b'], 'L')  # without start and end

    def test_copy_one(self):
        test = partial(func_for_testing, "copy_one")
        """Copy to right test"""
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,a:5::q1:', 'c', ['_', 'a', 'b', 'c'], 'R')  # with start and end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,a:5::q1:', 'c', ['_', 'b', 'c'], 'R')  # without start
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,a:5::q1:', 'c', ['_', 'a', 'b'], 'R')  # without end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,a:5::q1:', 'c', ['_', 'b'], 'R')  # without start and end
        """Copy to left test"""
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,c:::q1:', 'a', ['_', 'a', 'b', 'c'], 'L')  # with start and end
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,c:::q1:', 'a', ['_', 'a', 'b'], 'L')  # without start
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,c:::q1:', 'a', ['_', 'b', 'c'], 'L')  # without end
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,c:::q1:', 'a', ['_', 'b'], 'L')  # without start and end

    def test_move_one(self):
        test = partial(func_for_testing, "move_one")
        """Move to right test"""
        test('a,b,_,_,_,c:::q1:', ',b,_,_,_,a:5::q1:', 'c', ['_', 'a', 'b', 'c'], 'R')  # with start and end
        test('a,b,_,_,_,c:::q1:', ',b,_,_,_,a:5::q1:', 'c', ['_', 'b', 'c'], 'R')  # without start
        test('a,b,_,_,_,c:::q1:', ',b,_,_,_,a:5::q1:', 'c', ['_', 'a', 'b'], 'R')  # without end
        test('a,b,_,_,_,c:::q1:', ',b,_,_,_,a:5::q1:', 'c', ['_', 'b'], 'R')  # without start and end
        """Move to left test"""
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,:::q1:', 'a', ['_', 'a', 'b', 'c'], 'L')  # with start and end
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,:::q1:', 'a', ['_', 'a', 'b'], 'L')  # without start
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,:::q1:', 'a', ['_', 'b', 'c'], 'L')  # without end
        test('a,b,_,_,_,c:5::q1:', 'c,b,_,_,_,:::q1:', 'a', ['_', 'b'], 'L')  # without start and end

    def test_put_one(self):
        test = partial(func_for_testing, "put_one")

        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,w:5::q1:', 'w', 'c', ['_', 'a', 'b', 'c'], 'R')  # with start and end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,w:5::q1:', 'w', 'c', ['_', 'b', 'c'], 'R')  # without start
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,w:5::q1:', 'w', 'c', ['_', 'a', 'b'], 'R')  # without end
        test('a,b,_,_,_,c:::q1:', 'a,b,_,_,_,w:5::q1:', 'w', 'c', ['_', 'b'], 'R')  # without start and end

        test('a,b,_,_,_,c:5::q1:', 'w,b,_,_,_,c:::q1:', 'w', 'a', ['_', 'a', 'b', 'c'], 'L')  # with start and end
        test('a,b,_,_,_,c:5::q1:', 'w,b,_,_,_,c:::q1:', 'w', 'a', ['_', 'b', 'a'], 'L')  # without start
        test('a,b,_,_,_,c:5::q1:', 'w,b,_,_,_,c:::q1:', 'w', 'a', ['_', 'c', 'b'], 'L')  # without end
        test('a,b,_,_,_,c:5::q1:', 'w,b,_,_,_,c:::q1:', 'w', 'a', ['_', 'b'], 'L')  # without start and end

    def test_clean_one(self):
        test = partial(func_for_testing, "clean_one")
        test('a,b,_,_,_,c:::q1:', ',b,_,_,_,c:::q1:')

    def test_clean_range(self):
        test = partial(func_for_testing, "clean_range")
        test('a,b,_,_,_,c:::q1:', ',,,,,c:5::q1:', 'a', 'c', ['_', 'a', 'b', 'c'], 'R')  # with start and end
        test('a,b,_,_,_,c:::q1:', ',,,,,c:5::q1:', 'a', 'c', ['_', 'b', 'a'], 'R')  # without start
        test('a,b,_,_,_,c:::q1:', ',,,,,c:5::q1:', 'a', 'c', ['_', 'c', 'b'], 'R')  # without end
        test('a,b,_,_,_,c:::q1:', ',,,,,c:5::q1:', 'a', 'c', ['_', 'b'], 'R')  # without start and end

        test('a,b,_,_,_,c:5::q1:', 'a,,,,,:::q1:', 'c', 'a', ['_', 'a', 'b', 'c'], 'L')  # with start and end
        test('a,b,_,_,_,c:5::q1:', 'a,,,,,:::q1:', 'c', 'a', ['_', 'b', 'a'], 'L')  # without start
        test('a,b,_,_,_,c:5::q1:', 'a,,,,,:::q1:', 'c', 'a', ['_', 'c', 'b'], 'L')  # without end
        test('a,b,_,_,_,c:5::q1:', 'a,,,,,:::q1:', 'c', 'a', ['_', 'b'], 'L')  # without start and end

    def test_copy_range(self):
        test = partial(func_for_testing, "copy_range")

        between1 = ['1', '0']
        between12 = ['_', '1', '0']
        after2 = ['1', '0', 'h', '']

        test(
            'a,1,0,b,_,1,0,c,0,1,h:::q1:',
            'a,1,0,b,_,1,0,c,1,0,d:::q1:',
            'a', between1, 'b',
            between12, 'c', after2, 'R'
            )  # with start and end
        between1 += ['a', 'b']
        after2 += ['c']
        between12 += ['b', 'c']
        test(
            'a,1,0,b,_,1,0,c,0,1,h:::q1:',
            'a,1,0,b,_,1,0,c,1,0,d:::q1:',
            'a', between1, 'b',
            between12, 'c', after2, 'R'
            )  # without start and end
        test(
            'a,1,0,b,_,1,0,c,0,1,h:10::q1:',
            'd,0,1,b,_,1,0,c,0,1,h:10::q1:',
            'h', ['1', '0'], 'c',
            between12, 'b', ['1', '0', 'a', ''], 'L'
            )  # with start and end

    def test_move_range(self):
        test = partial(func_for_testing, "move_range")

        between1 = ['1', '0']
        between12 = ['_', '1', '0']
        after2 = ['1', '0', 'h', '']

        test(
            'a,1,0,b,_,1,0,c,0,1,h:::q1:',
            ',,,b,_,1,0,c,1,0,d:3::q1:',
            'a', between1, 'b',
            between12, 'c', after2, 'R'
            )  # with start and end
        between1 += ['a', 'b']
        after2 += ['c']
        between12 += ['b', 'c']
        test(
            'a,1,0,b,_,1,0,c,0,1,h:::q1:',
            ',,,b,_,1,0,c,1,0,d:3::q1:',
            'a', between1, 'b',
            between12, 'c', after2, 'R'
            )  # without start and end
        test(
            'a,1,0,b,_,1,0,c,0,1,h:10::q1:',
            'd,0,1,b,_,1,0,c,,,:7::q1:',
            'h', ['1', '0'], 'c',
            between12, 'b', ['1', '0', 'a', ''], 'L'
            )  # with start and end

    def test_stop(self):
        self.test_move_by_val()

    def test_set_all_on_way(self):
        test = partial(func_for_testing, "set_all_on_way")

        tm = TuringMachine.from_str("a,1,0,0,1,1,1,b,c,k,c,c,b:::q1:")
        tmac = TuringMachineMacro(tm)

        from_to = {'1': 's'}
        on_way_vals = ['1', '0', 'a', 'b']
        stop_val = 'b'

        tmac.set_all_on_way(from_to, on_way_vals, stop_val, 'R')
        tmac.set_rule(tmac.stick_val, tmac.cond_alpha.pop(), 'R', suppose_val='c')
        tmac.set_all_on_way({'c': 's'}, ['c', 'k', 'b'], stop_val, 'R')
        print(tm)
        tmac.stop()
        tm.run()

        from_val = {'0': 's'}
        on_way_vals = ['1', '0', 'j']
        stop_val = ''
        test("1,0,1,1,0,j,:::q1:",
             "1,s,1,1,s,j,:6::q1:",
             from_val,
             on_way_vals, stop_val,
             'R'
             )
        from_val = {'s': '0'}
        on_way_vals = ['1', 's', 'j']
        stop_val = ''
        test("1,s,1,1,s,j:5::q1:",
             ",1,0,1,1,0,j:-1::q1:",
             from_val,
             on_way_vals, stop_val,
             'L'
             )

    def test_bin_func(self):
        test = partial(func_for_testing, "bin_func")
        test("a,1,1,1,b,1,0,1,0,0,1,0,1,c:::q1:", "a,1,1,1,b,1,0,1,0,0,1,0,1,c,1,d:::q1:", 'a', 'b', 'c', 'd')
