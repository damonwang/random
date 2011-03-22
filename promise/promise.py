#!/usr/bin/env python

from __future__ import with_statement
from threading import Lock

class Promise(object):

    '''
    Given a referentially transparent zero-arity function `func`,
    returns an object (the promise) such that calling the promise is
    equivalent to calling `func` itself except that the work is only
    ever done once. Promise instances are thread-safe.
    '''

    def raise_error(self, error):
        def f():
            raise e
        return f

    def return_cached(self, retval):
        return lamdba : retval

    def __init__(self, func):

        self.lock = Lock()
        self.never_called = True

        def call_function():

            with self.lock:
                if self.never_called:
                    self.never_called = False
                    try:
                        retval = func()
                    except Exception as e:
                        self.__call__ = self.raise_error(e)
                        raise e
                    else:
                        self.__call__ = self.return_cached(retval)
                        return retval
            return self()

        self.__call__ = call_function
