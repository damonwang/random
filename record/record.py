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

    __slots__ = {fields}

    immutable_form = namedtuple('Immutable{typename}', __slots__)

    def __init__(self, {fields_as_args}):
        {init}
    def __repr__(self):
        'return a nicely formatted representation string'
        return '{repr_format}'.format({field_values})

    def as_dict(self):
        'return a new dict representing the same key->value mapping'
        return dict({field_values})

    def as_namedtuple(self):
        'return an immutable copy using collections.namedtuple.'
        return self.immutable_form({field_values})

    def but_with(self, {fields_as_args}):
        \'\'\'
        a functional update: return a new record, filling in unspecified
        fields with the corresponding values in this record.
        \'\'\'
        return {typename}({field_values_as_defaults})
'''

def define(typename, field_names):
    class_definition = class_template.format(typename=typename,
            fields = repr(tuple(field_names)),
            fields_as_args = ', '.join('%s=None' % field for field in field_names),
            # this is an odd syntax, but necessary because making the
            # indentation work out across multiple lines is difficult
            # (This is clearly a limitation of the technique that will
            # become more of a problem if we try to generalize it into a
            # macro system.)
            init = '%s = %s' % (
                ', '.join('self.%s' % field for field in field_names),
                ', '.join('%s' % field for field in field_names)),
            repr_format = '{typename}({values})'.format(
                typename=typename,
                values = ', '.join('%s={%s}' % (field, field) 
                    for field in field_names)),
            field_values = ', '.join('%s=self.%s' % (field, field)
                for field in field_names),
            field_values_as_defaults = 
            ', '.join('{field} = {field} or self.{field}'.format(field=field)
                for field in field_names)
            )
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
        record = define('Foo', ('foo', 'bar', 'baz'))
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

class TestHam(unittest.TestCase):
    '''
    this test suite ensures that I've generalized all the specific
    references to foo, bar, baz etc. from when I wrote out the template
    manually.
    '''
    def setUp(self):
        record = define('Ham', ('ham', 'spam', 'eggs'))
        self.ham = record(ham=1, spam=2, eggs=3)

    def test_init(self):
        ham = self.ham
        self.assert_(ham.ham == 1)
        self.assert_(ham.spam == 2)
        self.assert_(ham.eggs == 3)

    def test_repr(self):
        self.assert_(repr(self.ham) == 'Ham(ham=1, spam=2, eggs=3)')

    def test_as_dict(self):
        ham = self.ham
        self.assert_(ham.as_dict() 
                == dict(ham=ham.ham, spam=ham.spam, eggs=ham.eggs))

    def test_as_namedtuple(self):
        ham = self.ham
        ntup = ham.as_namedtuple()
        self.assert_(ntup == (ham.ham, ham.spam, ham.eggs))
        self.assert_(ntup.ham == ham.ham)
        self.assert_(ntup.spam == ham.spam)
        self.assert_(ntup.eggs == ham.eggs)

    def test_but_with(self):
        new_ham = self.ham.but_with(spam='2', eggs='3')
        self.assert_(new_ham.spam == '2')
        self.assert_(new_ham.eggs == '3')
        self.assert_(new_ham.ham == self.ham.ham)


def test():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite(map(loader.loadTestsFromTestCase,
        (TestFoo, TestHam)))
    unittest.TextTestRunner().run(suite)
