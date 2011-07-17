import random

# Python needs mutable records!  Why has no-one written a
# mutablenamedtuple yet?
class ClockRecord(object):
    __slots__ = ('access', 'key')
    def __init__(self, access, key):
        self.access = access
        self.key = key

class HashRecord(object):
    __slots__ = ('clock_pos', 'value')
    def __init__(self, clock_pos, value):
        self.clock_pos = clock_pos
        self.value = value        

class Cache(dict):
    def __init__(self, max):
        dict.__init__(self)
        self.clock = [None] * max
        self.max = self.free = max
        self.next_slot = 0

    def __getitem__(self, key):
        # write a mutable record type
        record = dict.__getitem__(self, key)
        self.clock[record.clock_pos].access = True
        return record.value

    def __setitem__(self, key, val):
        if key in self: 
            # no extra slots are consumed by an in-place update
            dict.__setitem__(self, key, val)
            return
        if self.free > 0: self.free -= 1
        else: # evict
            while self.clock[self.next_slot].access:
                self.clock[self.next_slot].access = False
                self.next_slot = (self.next_slot + 1) % self.max
            self.__delitem__(self.clock[self.next_slot].key)
        self.clock[self.next_slot] = ClockRecord(access=True, key=key)
        dict.__setitem__(self, key, HashRecord(clock_pos=self.next_slot, value=val))
        self.next_slot = (self.next_slot + 1) % self.max

# def memoize(**kw):
#     cache = kw.get('cache', Cache(kw.get('cache_size', 10000)))
#     def decorate(func):
#         def decorated(*args):
#             try:
#                 if args in cache: val = cache[args]
#                 else: val = cache[args] = func(*args)
#             except TypeError: val = func(*args)
#             return val
#         return decorated
#     return decorate

class Memoized(object):
    __slots__ = ('cache', 'func')
    def __init__(self, func, **kw):
        self.cache = kw.get('cache', Cache(kw.get('cache_size', 10000)))
        self.func = func

    def __call__(self, *args):
        try:
            if args in self.cache: val = self.cache[args]
            else: val = self.cache[args] = self.func(*args)
        except TypeError: val = self.func(*args)
        return val

def memoize(**kw):
    return lambda f: Memoized(f, **kw)
        
@memoize(cache_size=1000)
def cache_fibonacci(n):
    'foo'
    if not isinstance(n, int): raise TypeError
    if n == 0: return 0
    if n == 1: return 1
    if n > 1:  return cache_fibonacci(n-2) + cache_fibonacci(n-1)
    if n < 0:  raise ValueError

@memoize(cache={})
def dict_fibonacci(n):
    'foo'
    if not isinstance(n, int): raise TypeError
    if n == 0: return 0
    if n == 1: return 1
    if n > 1:  return dict_fibonacci(n-2) + dict_fibonacci(n-1)
    if n < 0:  raise ValueError

def test_seq(n, f):
    for i in range(n):
        f(i)

def test_rand(n, f):
    values = range(n)
    random.shuffle(values)
    for i in values:
        f(i)
