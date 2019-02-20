import functools


class MacroFactory:
    NAMELIST = ("is_reusable", "prepare", "reuse", "create")

    def __init__(self, func_name, f_is_reusable, f_prepare, f_reuse, f_create):
        self.func_name = func_name
        self.is_reusable = self.method_from_static(f_is_reusable)
        self.prepare = self.method_from_static(f_prepare)
        self.reuse = self.method_from_static(f_reuse)
        self.create = self.method_from_static(f_create)
        self.func_dict = {
            self.create_func_name(name): getattr(self, name)
            for name in self.NAMELIST
            }

    @staticmethod
    def method_from_static(function):
        @functools.wraps(function)
        def _(self, *args, **kwargs):
            return function(*args, **kwargs)

        return _

    @staticmethod
    def create_class_name(func_name):
        import re
        reg = re.compile("_(.)")
        s = re.sub(reg, lambda m: m.group(1).upper(), func_name)
        return s[0].upper() + s[1:]

    def create_func_name(self, name):
        return "_" + name + "_" + self.func_name.__name__

    def create_class(self):
        name = self.create_class_name(self.func_name)
        cls = type(name, (object,), dict(object.__dict__))
        for key, val in self.func_dict.items():
            setattr(cls, key, val)

        def main_func(obj, *args, **kwargs):
            nonlocal self
            getattr(obj, self.func_dict[])
