from inner_type import Polymorphic, Composite, Primitive, Slot, Arrow, unify


class Environment(dict):

    def __init__(self, parent=None):
        super(Environment, self).__init__(parent if parent else {})
        self.type_slots = parent.type_slots if parent else {}

    def lookup(self, name):
        return self.get(name)


class Form(object):

    type_suffix = 0
    var_suffix = 0

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)

    def infer(self, env):
        pass

    @staticmethod
    def new_type(name=None):
        Form.type_suffix += 1
        return Slot('{}{}'.format(name or '', Form.type_suffix))

    @staticmethod
    def new_var(name=None):
        Form.var_suffix += 1
        return Slot('{}{}'.format(name or 't', Form.type_suffix))


class Id(Form):

    def infer(self, env):
        default_type = env.lookup(self.name)
        if not default_type:
            raise NameError('name {} is not defined'.format(default_type))
        elif isinstance(default_type, Polymorphic):
            return default_type.instantiate(self.new_type)
        else:
            return default_type


class Apply(Form):

    def __init__(self, func, arg):
        super(Apply, self).__init__(func)
        self.func = func
        self.arg = arg

    def infer(self, env):
        func_type = self.func.infer(env).apply(env.type_slots)
        arg_type = self.arg.infer(env).apply(env.type_slots)

        slot_foo, slot_bar = self.new_type(), self.new_type()
        arrow = Arrow(slot_foo, slot_bar)
        if not unify(env.type_slots, arrow, func_type):
            raise Exception('type of {} is not a function'.format(self.func, func_type.apply(env.type_slots)))

        arg_type_prime = slot_foo.apply(env.type_slots)
        if not unify(env.type_slots, arg_type_prime, arg_type):
            raise Exception('Type incompatible for {}'.format(self.arg))
        result = slot_bar.apply(env.type_slots)
        return result

    def __repr__(self):
        if not isinstance(self.arg, Id):
            template = '{} ({})'
        else:
            template = '{} {}'
        return template.format(self.func, self.arg)


class FunctionDefine(Form):

    def __init__(self, name, param, body, local=False):
        super(FunctionDefine, self).__init__(name)
        self.param = param
        self.body = body
        self.local = local

    def infer(self, env):
        inner_env = Environment(env)
        alpha, beta = self.new_type("a"), self.new_type("b")
        func_type = Arrow(alpha, beta)
        inner_env[self.param.name] = alpha
        inner_env[self.name] = Arrow(alpha, beta)
        inner_env.type_slots[beta] = self.body.infer(inner_env)
        env.type_slots.update(inner_env.type_slots)
        func_type = func_type.apply(inner_env.type_slots)
        if self.local:
            env[self.name] = func_type
            return func_type
        else:
            free_slots = set()
            func_type.get_free_slots(inner_env.type_slots, free_slots)
            poly_type = Polymorphic(free_slots, func_type)
            env[self.name] = poly_type
            return poly_type.instantiate(self.new_type)

    def __repr__(self):
        return 'function {} {} = {}'.format(self.name, self.param, self.body)


class Assign(Form):

    def __init__(self, name, arg):
        super(Assign, self).__init__(name)
        self.arg = arg

    def infer(self, env):
        t = self.arg.infer(env)
        env[self.name] = t
        return t

    def __repr__(self):
        return "set {} = {}".format(self.name, self.arg)
