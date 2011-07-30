import unittest 
from record import Record

class TestFoo(unittest.TestCase):
    def setUp(self):
        record = Record.define('Foo', ('foo', 'bar', 'baz'))
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
        record = Record.define('Ham', ('ham', 'spam', 'eggs'))
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
    unittest.TextTestRunner().run(
        unittest.TestSuite(map(loader.loadTestsFromTestCase,
          (TestFoo, TestHam))))
