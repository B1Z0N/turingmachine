from turingmachine.alphabetgenerator import AlphabetGenerator, NameTemplate


class TestNameTemplate:
    def setup_class(self):
        self.nmtmpl = NameTemplate('q43')

    def test_iterate(self):
        it = self.nmtmpl.iterate()
        for i in range(43, 60):
            next(it)
        print(self.nmtmpl.counter, self.nmtmpl.letter)
        assert self.nmtmpl.letter == 'q'
        assert self.nmtmpl.counter == 60


class TestAlphabetGenerator:
    def setup_class(self):
        self.gen = AlphabetGenerator()

    def test_set_template(self):
        self.gen.cur_template = 'q43'
        assert self.gen.pop() == 'q44'

    def test_del_template(self):
        del self.gen.cur_template
        assert self.gen.pop() == 'a'

    def test_get_letter(self):
        assert self.gen.pop() == 'b'
