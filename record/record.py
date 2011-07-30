from collections import namedtuple
class Record (object):
    '''
    manual mutable-record object.

    Names may be anything AST.parse will accept for an _ast.Name object,
    although we will try (but not promise!) to throw an exception if you
    shadow an existing method (e.g., __repr__).

    Note that this means not all Record objects can be cleanly converted
    into namedtuples.  If we detect that namedtuple would reject a field
    name, no as_namedtuple method will be generated.
    '''

    __slots__ = ('foo', 'bar', 'baz')

    immutable_form = namedtuple('ImmutableRecord', __slots__)

    def __init__(self, foo=None, bar=None, baz=None):
        self.foo = foo
        self.bar = bar
        self.baz = baz

    def __repr__(self):
        'return a nicely formatted representation string'
        return 'Record(foo={foo}, bar={bar}, baz={baz})'.format(
                foo=self.foo, bar=self.bar, baz=self.baz)

    def as_dict(self):
        'return a new dict representing the same key->value mapping'
        return dict(foo=self.foo, bar=self.bar, baz=self.baz)

    def as_namedtuple(self):
        'return an immutable copy using collections.namedtuple.'
        return self.immutable_form(foo=self.foo, bar=self.bar, baz=self.baz)

    def but_with(self, foo=None, bar=None, baz=None):
        '''
        a functional update: return a new Record, filling in unspecified
        fields with the corresponding values in this Record.
        '''
        return Record(foo = foo or self.foo, bar = bar or self.bar,
                baz = baz or self.baz)
