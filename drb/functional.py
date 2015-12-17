# -*- coding: utf-8 -*-

class TooFewException(ValueError):
    pass

class TooManyException(ValueError):
    pass

def one(iterable):
    iterator = iter(iterable)
    try:
        value = iterator.next()
    except:
        raise TooFewException("Less than one element in {0} object".format(type(iterable)))

    try:
        iterator.next()
        raise TooManyException("More than one element in {0} object".format(type(iterable)))
    except StopIteration:
        return value
