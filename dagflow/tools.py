from __future__ import print_function
from collections import Iterable
import itertools as I

class StopNesting(Exception):
    def __init__(self, object):
        self.object = object

def IsIterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)

def nth(iterable, n):
    "Returns the nth item or a default value"
    if n>-1:
        return next(I.islice(iterable, n, None))
    else:
        return tuple(iterable)[n]

class Undefined(object):
    def __init__(self, what):
        self.what=what

    def __str__(self):
        return 'Undefined '+self.what

    def __repr__(self):
        return 'Undefined("{what}")'.format(what=self.what)

    def __bool__(self):
        return False

    def __call__(self, *args, **kwargs):
        pass

undefinedname = Undefined('name')
undefineddata = Undefined('data')
undefineddatatype = Undefined('datatype')
undefinednode = Undefined('node')
undefinedgraph = Undefined('graph')
undefinedoutput = Undefined('output')
undefinedleg = Undefined('leg')
undefinedfunction = Undefined('function')

