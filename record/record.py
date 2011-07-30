import sys 
import unittest

class_template = '''
from collections import namedtuple
class {typename} (object):
    \'\'\'
    manual mutable-record object.

    Names may be anything AST.parse will accept for an _ast.Name object,
    although we will try (but not promise!) to throw an exception if you
    shadow an existing method (e.g., __repr__).

    Note that this means not all record objects can be cleanly converted
    into namedtuples.  If we detect that namedtuple would reject a field
    name, no as_namedtuple method will be generated.
    \'\'\'

    __slots__ = ('foo', 'bar', 'baz')

    immutable_form = namedtuple('Immutable{typename}', __slots__)

    def __init__(self, foo=None, bar=None, baz=None):
        self.foo = foo
        self.bar = bar
        self.baz = baz

    def __repr__(self):
        'return a nicely formatted representation string'
        return '{typename}(foo={{foo}}, bar={{bar}}, baz={{baz}})'.format(
                foo=self.foo, bar=self.bar, baz=self.baz)

    def as_dict(self):
        'return a new dict representing the same key->value mapping'
        return dict(foo=self.foo, bar=self.bar, baz=self.baz)

    def as_namedtuple(self):
        'return an immutable copy using collections.namedtuple.'
        return self.immutable_form(foo=self.foo, bar=self.bar, baz=self.baz)

    def but_with(self, foo=None, bar=None, baz=None):
        \'\'\'
        a functional update: return a new record, filling in unspecified
        fields with the corresponding values in this record.
        \'\'\'
        return {typename}(foo = foo or self.foo, bar = bar or self.bar,
                baz = baz or self.baz)
'''

def define(typename):
    class_definition = class_template.format(typename=typename)
    namespace = dict(__name__='Record_%s' % typename)

    # the following lines are closely copied from collections.namedtuple
    try: exec(class_definition, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.msg + ':\n\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the
    # frame
    # where the named tuple is created. Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try: result.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError): pass

    return result

class TestFoo(unittest.TestCase):
    def setUp(self):
        record = define('Foo')
        self.foo = record(foo=1, bar=2, baz=3)

    def test_init(self):
        foo = self.foo
        self.assert_(foo.foo == 1)
        self.assert_(foo.bar == 2)
        self.assert_(foo.baz == 3)

    def test_repr(self):
        self.assert_(repr(self.foo) == 'Foo(foo=1, bar=2, baz=3)')

    def test_as_dict(self):
        foo = self.foo
        self.assert_(foo.as_dict() 
                == dict(foo=foo.foo, bar=foo.bar, baz=foo.baz))

    def test_as_namedtuple(self):
        foo = self.foo
        ntup = foo.as_namedtuple()
        self.assert_(ntup == (foo.foo, foo.bar, foo.baz))
        self.assert_(ntup.foo == foo.foo)
        self.assert_(ntup.bar == foo.bar)
        self.assert_(ntup.baz == foo.baz)

    def test_but_with(self):
        new_foo = self.foo.but_with(bar='2', baz='3')
        self.assert_(new_foo.bar == '2')
        self.assert_(new_foo.baz == '3')
        self.assert_(new_foo.foo == self.foo.foo)

def test():
    tests = unittest.TestLoader().loadTestsFromTestCase(TestFoo)
    unittest.TextTestRunner().run(tests)
