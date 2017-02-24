import pprint
from inner_type import *
from inference import *

type1 = Arrow(
    Product(
        Arrow(Slot("a1"), Slot("a2")),
        Composite(Primitive("list"), Slot("a3"))),
    Composite(Primitive("list"), Slot("a2")))

type2 = Arrow(
    Product(
        Arrow(Slot("a3"), Slot("a4")),
        Composite(Primitive("list"), Slot("a3"))),
    Slot("a5"))

print "Unify Type 1 and Type 2:\n"
print "Type 1  ->", type1
print "Type 2  ->", type2, '\n'

map = {}
unify(map, type1, type2)
print "Slot map:", map, '\n'
print "Unifed result: ", "apply 1 ->", type1.apply(map)
print "Unifed result: ", "apply 2 ->", type2.apply(map), '\n'


env = Environment()

env['call'] = Polymorphic(
    set([Slot('a'), Slot('b')]),
    Arrow(Arrow(Slot('a'), Slot('b')), Arrow(Slot('a'), Slot('b'))))

env['seq'] = Polymorphic(
    set([Slot('a'), Slot('b')]),
    Arrow(Slot('a'), Arrow(Slot('b'), Slot('b'))))

env['car'] = Polymorphic(
    set([Slot('a')]),
    Arrow(
        Composite(Primitive('list'), Slot('a')),
        Slot('a')))

env['cdr'] = Polymorphic(
    set([Slot('a')]),
    Arrow(
        Composite(Primitive('list'), Slot('a')),
        Composite(Primitive('list'), Slot('a'))))

env['cons'] = Polymorphic(
    set([Slot('a')]),
    Arrow(
        Slot('a'),
        Arrow(
            Composite(Primitive('list'), Slot('a')),
            Composite(Primitive('list'), Slot('a')))))

env['newlist'] = Polymorphic(
    set([Slot('a')]),
    Arrow(
        Primitive('unit'),
        Composite(Primitive('list'), Slot('a'))))

env['empty?'] = Polymorphic(
    set([Slot('a')]),
    Arrow(Composite(Primitive('list'), Slot('a')), Primitive('bool')))

env['0'], env['1'] = Primitive('int'), Primitive('int')

env['if'] = Polymorphic(
    set([Slot('a')]),
    Arrow(Primitive('bool'),
          Arrow(Composite(Primitive('thunk'), Slot('a')),
                Arrow(Composite(Primitive('thunk'), Slot('a')), Slot('a')))))

env['nothing'] = Primitive('unit')

env['+'] = Arrow(
    Primitive('int'),
    Arrow(Primitive('int'), Primitive('int')))

env['hold'] = Polymorphic(
    set([Slot('a')]),
    Arrow(Slot('a'),
          Composite(Primitive('thunk'), Slot('a'))))


def translate(a):
    if isinstance(a, list):
        if a[0] == 'function':
            return FunctionDefine(a[1], translate(a[2]), translate(a[3]))
        elif a[0] == 'let' and len(a) == 3:
            return Assign(a[1], translate(a[2]))
        elif a[0] == 'letf' and len(a) == 4:
            return FunctionDefine(a[1], translate(a[2]), translate(a[3]), True)
        elif a[0] == 'lambda':
            t = Form.new_var()
            return translate(['seq', ['letf', t, a[1], a[2]], t])
        elif a[0] == 'begin':
            return translate(reduce(lambda x, y: ['seq', x, y], a[1:]))
        elif len(a) == 2:
            return Apply(translate(a[0]), translate(a[1]))
        else:
            return Apply(translate(a[:-1]), translate(a[-1]))
    else:
        return Id(a)


f_id = translate(
    ["function", "crz", "x",
        ["seq", ["letf", "crz1", "y",
                 ["seq", ["letf", "crz2", "z",
                          ["seq", "x",
                           ["seq", "y", "z"]]],
                     "crz2"]],
            "crz1"]])

f_length = translate(
    ["function", "length", "a",
        ["if", ["empty?", "a"],
            ["hold", "0"],
            ["hold", ["+", "1", ["length", ["cdr", "a"]]]]]])

f_sum = translate(
    ["function", "sum", "a",
        ["if", ["empty?", "a"],
            ["hold", "0"],
            ["hold", ["+", ["car", "a"], ["sum", ["cdr", "a"]]]]]])

f_map = translate(
    ["function", "map", "f",
        ["begin",
         ["lambda", "a",
          ["if", ["empty?", "a"],
           ["hold", ["newlist", "nothing"]],
           ["hold", ["cons", ["f", ["car", "a"]], ["map", "f", ["cdr", "a"]]]]]]]])

f_id.infer(env)
f_length.infer(env)
f_sum.infer(env)
f_map.infer(env)

print "Some inference examples are defined in test.py, there is inference result:\n"
pprint.pprint(env)
