class Monomorphic(object):
    """
    Base class of monomorphic type.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return super(Monomorphic, self).__repr__()

    def apply(self, symbol_map):
        pass

    def get_free_slots(self, m, a):
        pass

    def free_from(self, symbol):
        pass

    def __eq__(self, another):
        return False


class Slot(Monomorphic):
    """
    Slot for free variables
    """

    type_map = {}

    def __new__(cls, name):
        if name in cls.type_map:
            return cls.type_map[name]
        type = super(Slot, cls).__new__(cls, name)
        cls.type_map[name] = type
        return type

    def __init__(self, name):
        super(Slot, self).__init__(name)

    def __repr__(self):
        return "'{}".format(self.name)

    def apply(self, symbol_map):
        symbol = symbol_map.get(self)
        if not symbol or symbol == self:
            return self
        return symbol.apply(symbol_map)

    def __eq__(self, another):
        return another and isinstance(another, Slot) and self.name == another.name

    def get_free_slots(self, symbol_map, free_slots=set()):
        if self not in symbol_map and self not in free_slots:
            free_slots.add(self)

    def free_from(self, symbol):
        return self != symbol


class Primitive(Monomorphic):
    """
    Primitive type
    """

    instance_map = {}

    def __new__(cls, name, argument=None):
        if name in cls.instance_map:
            return cls.instance_map[name]
        instance = super(Primitive, cls).__new__(cls, name, argument)
        cls.instance_map[name] = instance
        return instance

    def __init__(self, name, argument=None):
        super(Primitive, self).__init__(name)
        self.argument = argument

    def __repr__(self):
        return self.name

    def apply(self, symbol_map):
        return self

    def __eq__(self, another):
        return another and isinstance(another, Primitive) and self.name == another.name

    def free_from(self, symbol):
        return True


class Composite(Monomorphic):
    """
    Composite type
    """

    def __init__(self, constructor, argument):
        self.constructor = constructor
        self.argument = argument

    def __repr__(self):
        if isinstance(self.constructor, Composite) \
                and isinstance(self.constructor.constructor, Primitive) \
                and self.constructor.constructor.name == '->':
            left = self.constructor.argument
            right = self.argument
            if isinstance(left, Composite):
                return '({}) -> {}'.format(left, right)
            else:
                return '{} -> {}'.format(left, right)
        else:
            if isinstance(self.argument, Composite):
                return "{} ({})".format(self.constructor, self.argument)
            else:
                return "{} {}".format(self.constructor, self.argument)

    def apply(self, symbol_map):
        return Composite(self.constructor.apply(symbol_map), self.argument.apply(symbol_map))

    def __eq__(self, another):
        return another \
            and isinstance(another, Composite) \
            and self.constructor == another.constructor \
            and self.argument == another.argument

    def get_free_slots(self, symbol_map, free_slots=set()):
        self.constructor.get_free_slots(symbol_map, free_slots)
        self.argument.get_free_slots(symbol_map, free_slots)
        return free_slots

    def free_from(self, symbol):
        return self.constructor.free_from(symbol) and self.argument.free_from(symbol)


class Polymorphic(object):

    def __init__(self, quantifier, base):
        self.n, self.quantifier, symbol_map = 1, set(), {}
        for key in sorted(quantifier, lambda x, y: cmp(x.name, y.name)):
            renamed_slot = Slot(self.rename(self.n))
            if key != renamed_slot:
                symbol_map[key] = renamed_slot
            self.quantifier.add(renamed_slot)
            self.n += 1
        self.base = base.apply(symbol_map)

    def instantiate(self, generator):
        symbol_map = {}
        for key in self.quantifier:
            symbol_map[key] = generator()
        return self.base.apply(symbol_map)

    @staticmethod
    def rename(number):
        base_char = ord('a')
        letters = []
        while number > 0:
            number -= 1
            letters.append(chr(base_char + number % 26))
            number = number / 26
        letters.reverse()
        return ''.join(letters)

    def __repr__(self):
        buf = 'forall'
        for item in sorted(self.quantifier, lambda x, y: cmp(x.name, y.name)):
            buf += ' ' + repr(item)
        return '{}. {}'.format(buf, repr(self.base))


class Arrow(Composite):

    def __init__(self, argument, result):
        super(Arrow, self).__init__(
            Composite(Primitive("->"), argument),
            result
        )


class Product(Composite):

    def __init__(self, argument, result):
        super(Product, self).__init__(
            Composite(Primitive("*"), argument),
            result
        )


def unify(symbol_map, one, another):
    if isinstance(one, Slot) \
            and isinstance(another, Slot) \
            and one.apply(symbol_map) == another.apply(symbol_map):
        return True

    elif isinstance(one, Primitive) \
            and isinstance(another, Primitive) \
            and one.name == another.name \
            and one.argument == another.argument:
        return True

    elif isinstance(one, Composite) and isinstance(another, Composite):
        return unify(symbol_map, one.constructor, another.constructor) \
            and unify(symbol_map, one.argument, another.argument)

    elif isinstance(one, Slot):
        another_prime = another.apply(symbol_map)
        if another_prime.free_from(one):
            symbol_map[one] = another_prime
            return True
        return False

    elif isinstance(another, Slot):
        one_prime = one.apply(symbol_map)
        if one_prime.free_from(another):
            symbol_map[another] = one_prime
            return True
        return False

    else:
        return False
