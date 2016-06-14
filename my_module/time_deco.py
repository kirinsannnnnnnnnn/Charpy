import time
from functools import wraps


def time_deco(_a, cn):
    def wrappedwrapper(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            before = time.time()
            result = f(*args, **kwds)
            after = time.time()
            if _a:
                print((cn + '.' + str(f.__name__)).rjust(30) +
                      ' was used {} sec'.format(float(after - before)))
            return result
        return wrapper
    return wrappedwrapper
