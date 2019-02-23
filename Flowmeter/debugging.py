import inspect

class magic_object:

    def __init__(o, c, f, a, k):
        o.h = c(*a, **k)
        o.f = f
        o.f("%s.__init__(*%s, **%s)" % (id(o.h), repr(a), repr(k)))

    def __getattr__(o, name):
        def d(*a, **k):
            r = getattr(o.h, name)(*a, **k)
            o.f("%s.%s(*%s, **%s) -> %s" % (id(o.h), name, repr(a), repr(k), repr(r)))
            return r
        return d


class magic_class:

    def __init__(o, c, f):
        o.c = c
        o.f = f

    def __call__(o, *a, **k):
        return magic_object(o.c, o.f, a, k)


def magic_printing_func(x):
    print ("\033[44;34;1m*\033[0m %s" % x)

def make_magic(the_class, printing_func=None):
    if printing_func is None:
        printing_func = magic_printing_func
#    globals()[the_class.__name__] = magic_class(the_class, printing_func)
    inspect.currentframe().f_back.f_globals[the_class.__name__] = magic_class(
        the_class, printing_func
    )