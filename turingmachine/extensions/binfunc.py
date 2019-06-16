from turingmachine.macro import Basic, MacroMain, MacroFuncTemplate


class BinaryFunction(MacroFuncTemplate):
    """Class for managing binary function execution"""

    def is_reusable(self, obj: Basic, *args, **kwargs):
        pass

    def prepare(self, obj: Basic, *args, **kwargs):
        pass

    def reuse(self, obj: Basic, *args, **kwargs):
        pass

    def create(self, obj: Basic, *args, **kwargs):
        pass


class BinFunc(MacroMain):
    binary_function = BinaryFunction()
